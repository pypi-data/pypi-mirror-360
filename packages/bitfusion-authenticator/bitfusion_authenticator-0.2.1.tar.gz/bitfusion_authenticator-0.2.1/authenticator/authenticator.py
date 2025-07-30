import asyncio
import time
from typing import Optional

import httpx
from jose import jwk, jwt
from jose.exceptions import ExpiredSignatureError, JWTClaimsError, JWTError


class AuthError(Exception):
    pass


class Authenticator:
    def __init__(
        self,
        jwks_url: str,
        cache_ttl: int = 3600,
    ):
        self.jwks_url = jwks_url
        self.cache_ttl = cache_ttl
        self._jwks: Optional[dict] = None
        self._jwks_fetched_at: float = 0
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(timeout=5.0)

    async def _fetch_jwks(self) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(self.jwks_url)
        resp.raise_for_status()
        return resp.json()

    async def _get_jwks(self) -> dict:
        async with self._lock:
            now = time.time()
            if self._jwks is None or (now - self._jwks_fetched_at) > self.cache_ttl:
                jwks = await self._fetch_jwks()
                self._jwks = jwks
                self._jwks_fetched_at = now
            return self._jwks

    async def _get_public_key_for_token(self, token: str):
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise AuthError("No 'kid' in token header")

        jwks = await self._get_jwks()
        for key_dict in jwks.get("keys", []):
            if key_dict.get("kid") == kid:
                return jwk.construct(key_dict)

        raise AuthError(f"JWK with kid={kid} not found")

    async def validate_token(self, token: str, audience: Optional[str] = None) -> dict:
        try:
            public_key = await self._get_public_key_for_token(token)
            return jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=audience,
            )
        except ExpiredSignatureError:
            raise AuthError("Token expired")
        except JWTClaimsError:
            raise AuthError("Invalid claims")
        except JWTError as e:
            raise AuthError(f"Invalid token: {e}")

