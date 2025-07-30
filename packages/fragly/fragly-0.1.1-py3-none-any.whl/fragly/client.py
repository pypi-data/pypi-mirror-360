import aiohttp
from typing import Dict, Any, Optional
from .exceptions import FraglyFragmentAPIError, InvalidUsernameError, InsufficientBalanceError

class fragly:
    """
    Async client for interacting with PepeFragment API service.
    Base URL is pre-set to https://docs.lunovr.ru
    """

    BASE_URL = "https://docs.lunovr.ru"

    def __init__(self, api_token: str, timeout: int = 30):
        """
        :param api_token: Your API token for authentication
        :param timeout: Request timeout in seconds
        """
        self.api_token = api_token
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "X-API-Token": self.api_token,
                    "accept": "application/json",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        await self._ensure_session()
        url = f"{self.BASE_URL}{endpoint}"
        try:
            async with self.session.post(url, json=payload) as resp:
                data = await resp.json()
                if resp.status == 400:
                    if "Insufficient balance" in str(data.get("message", "")):
                        raise InsufficientBalanceError(data.get("message", "Insufficient balance."))
                    raise PepeFragmentAPIError(data.get("message", "Bad request"))
                if resp.status == 404:
                    raise InvalidUsernameError("User not found.")
                resp.raise_for_status()
                return data
        except aiohttp.ClientError as e:
            raise PepeFragmentAPIError(f"Network error: {str(e)}") from e

    async def buy_stars(self, username: str, quantity: int, hide_sender: int = 0) -> Dict[str, Any]:
        payload = {"username": username.lstrip("@"), "quantity": quantity, "hide_sender": hide_sender}
        return await self._post("/api/buyStars", payload)

    async def buy_premium(self, username: str, months: int, hide_sender: int = 0) -> Dict[str, Any]:
        payload = {"username": username.lstrip("@"), "months": months, "hide_sender": hide_sender}
        return await self._post("/api/buyPremium", payload)

    async def check_username(self, username: str) -> Dict[str, Any]:
        payload = {"username": username.lstrip("@")}
        return await self._post("/api/check_username", payload)