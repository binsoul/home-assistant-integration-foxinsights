"""FoxInsights API class."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass

import aiohttp
import async_timeout

from .const import API_URL, LOGGER, REQUEST_TIMEOUT


@dataclass
class FoxInsightsDevice:
    """FoxInsights device."""

    hwid: str
    currentMeteringAt: str
    nextMeteringAt: str
    daysReach: int | None
    validationError: str | None
    batteryLevel: str | None
    fillLevelPercent: int | None
    fillLevelQuantity: int | None
    quantityUnit: str

    @classmethod
    def init_from_response(cls, response):
        """Create object from response."""
        return cls(
            response.get("hwid"),
            response.get("currentMeteringAt"),
            response.get("nextMeteringAt"),
            response.get("daysReach"),
            response.get("validationError"),
            response.get("batteryLevel"),
            response.get("fillLevelPercent"),
            response.get("fillLevelQuantity"),
            response.get("quantityUnit"),
        )


class FoxInsightsApiError(Exception):
    """Exception to indicate a general API error."""


class FoxInsightsApiConnectionError(FoxInsightsApiError):
    """Exception to indicate a communication error."""


class FoxInsightsApiAuthenticationError(FoxInsightsApiError):
    """Exception to indicate an authentication error."""


class FoxInsightsApi:
    """FoxInsights API (https://github.com/foxinsights/customer-api)."""

    def __init__(self, email: str, password: str, session: aiohttp.ClientSession):
        """Initialize FoxInsights API."""
        self._email = email
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict[str, FoxInsightsDevice]:
        """Update data."""

        access_token = await self._get_token()
        if access_token is None:
            return {}

        try:
            json_data = await self._request(
                self._session,
                method="get",
                url=API_URL + "device",
                headers={
                    "Authorization": "Bearer " + access_token,
                    "Accept": "application/json; charset=UTF-8",
                },
            )

            devices = {}
            for dev in json_data.get("items"):
                device = FoxInsightsDevice.init_from_response(dev)
                devices[device.hwid] = device

            return devices
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.error("Error getting token: %s ", exception, exc_info=True)

            raise exception

    async def async_test_login(self) -> bool:
        """Test if login is possible."""
        token = await self._get_token()

        return token is not None

    async def _get_token(self) -> str | None:
        """Get token for FoxInsights."""

        try:
            json_data = await self._request(
                self._session,
                method="post",
                url=API_URL + "login",
                data={
                    "email": self._email,
                    "password": self._password,
                },
                headers={"Content-type": "application/json; charset=UTF-8"},
            )

            return json_data.get("access_token")
        except Exception as exception:  # pylint: disable=broad-except
            LOGGER.exception("Error getting token: %s ", exception)

            raise FoxInsightsApiAuthenticationError(exception) from exception

    async def _request(
        self,
        session: aiohttp.ClientSession,
        method: str,
        url: str,
        data: dict | None = None,
        headers: dict | None = None,
        retry: int = 3,
    ) -> any:
        """Get information from the API."""

        LOGGER.debug("Request %s, retry=%s", url, retry)

        try:
            async with async_timeout.timeout(REQUEST_TIMEOUT):
                response = await session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                if response.status in (401, 403):
                    raise FoxInsightsApiAuthenticationError(
                        "Invalid credentials",
                    )
                response.raise_for_status()
                return await response.json()

        except asyncio.TimeoutError as exception:
            if retry > 0 and response.status != 429:
                return await self._request(
                    session, method, url, data, headers, retry - 1
                )

            raise FoxInsightsApiConnectionError(
                "Timeout error fetching information",
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            if retry > 0 and response.status != 429:
                return await self._request(
                    session, method, url, data, headers, retry - 1
                )

            raise FoxInsightsApiConnectionError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise FoxInsightsApiError("An unexpected error occurred") from exception
