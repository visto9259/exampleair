"""Client for Example Air monitors."""

from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import ClientError, ClientSession

from .exceptions import (
    ExampleAirConnectionError,
    ExampleAirInvalidResponseError,
)
from .models import Status

DEFAULT_TIMEOUT = 10


class ExampleAirClient:
    """Talk to an Example Air monitor."""

    def __init__(
        self,
        host: str,
        session: ClientSession,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Initialize the client.

        `host` is a hostname or IP address. The caller owns `session`
        and is responsible for closing it.
        """
        self._host = host
        self._session = session
        self._timeout = timeout

    @property
    def host(self) -> str:
        """Return the host of the monitor."""
        return self._host

    async def _request(self, method: str, path: str) -> Any:
        """Make a request and return the decoded JSON."""
        url = f"http://{self._host}/{path}"
        try:
            async with asyncio.timeout(self._timeout):
                response = await self._session.request(method, url)
                response.raise_for_status()
                return await response.json(content_type=None)
        except TimeoutError as err:
            raise ExampleAirConnectionError(
                f"Timeout connecting to {self._host}"
            ) from err
        except ClientError as err:
            raise ExampleAirConnectionError(
                f"Error connecting to {self._host}: {err}"
            ) from err
        except ValueError as err:
            raise ExampleAirInvalidResponseError(
                f"{self._host} did not return valid JSON"
            ) from err

    async def get_status(self) -> Status:
        """Return the current status of the monitor."""
        data = await self._request("get", "status")
        if not isinstance(data, dict):
            raise ExampleAirInvalidResponseError(
                "Expected a JSON object from the monitor"
            )
        return Status.from_dict(data)
