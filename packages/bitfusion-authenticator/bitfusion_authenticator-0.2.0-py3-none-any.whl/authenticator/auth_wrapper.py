from httpx import AsyncClient, Response


class AuthWrapper:
    def __init__(
        self, auth_service_url: str, client_id: str, client_secret: str, dev_token=None
    ):
        self.auth_url = auth_service_url
        self._http_client = AsyncClient()

        self._client_id = client_id
        self._client_secret = client_secret

        self._dev_token = dev_token
        self._token: str | None = None

    async def __aenter__(self):
        if not self._token:
            self._token = await self._get_token()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self._http_client.aclose()

    async def _get_token(self) -> str:
        if self._dev_token:
            return self._dev_token

        endpoint = f"{self.auth_url}/client/token"
        resp = await self._http_client.post(
            endpoint,
            json={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
        )
        resp.raise_for_status()
        return resp.json()["token"]

    async def request(self, method: str, url: str, **kwargs) -> Response:
        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._token}"

        method = method.upper()

        resp = await self._http_client.request(method, url, headers=headers, **kwargs)

        if resp.status_code == 401:
            self._token = await self._get_token()
            headers["Authorization"] = f"Bearer {self._token}"
            resp = await self._http_client.request(
                method, url, headers=headers, **kwargs
            )

        return resp
