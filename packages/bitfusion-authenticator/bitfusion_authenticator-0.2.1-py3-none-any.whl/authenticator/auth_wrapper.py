from httpx import AsyncClient, Response
import logging

logger = logging.getLogger(__name__)

class Unauthorized(Exception):
    def __init__(self, token, *args):
        self.token = token
        super().__init__(*args)


class AuthWrapper:
    def __init__(
        self, auth_service_url: str, client_id: str, client_secret: str, token=None
    ):
        self.auth_url = auth_service_url
        self._http_client = AsyncClient()

        self._client_id = client_id
        self._client_secret = client_secret
        
        self._token: str | None = token

    async def __aenter__(self):
        if not self._token:
            self._token = await self._get_token()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._http_client.aclose()

    async def _get_token(self) -> str:
        endpoint = f"{self.auth_url}/client/token"
        resp = await self._http_client.post(
            endpoint,
            json={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        resp.raise_for_status()
        logger.debug("Got new token.")
        return resp.json()["token"]

    async def request(self, method: str, url: str, **kwargs) -> Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"

        method = method.upper()

        logger.debug("Sending request. First try...")
        resp = await self._http_client.request(method, url, headers=headers, **kwargs)

        if resp.status_code == 401:
            logger.debug("Recevied 401. Getting new token...")
            self._token = await self._get_token()
            headers["Authorization"] = f"Bearer {self._token}"
            logger.debug("Sending request. Second try...")
            resp = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )
            if resp.status_code == 401:
                raise Unauthorized(self._token)

        return resp
