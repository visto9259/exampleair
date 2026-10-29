"""Data models of the exampleair library."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .exceptions import ExampleAirInvalidResponseError


@dataclass
class Status:
    """The status of an Example Air monitor."""

    serial_number: str
    name: str
    firmware: str
    temperature: float
    humidity: float
    pm25: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Status:
        """Build a status from the JSON the monitor returns.

        The names follow the API of the monitor. Values are passed on
        as they are: no unit conversion or rounding happens here.
        """
        try:
            return cls(
                serial_number=str(data["serial_number"]),
                name=str(data["name"]),
                firmware=str(data["firmware"]),
                temperature=float(data["temperature"]),
                humidity=float(data["humidity"]),
                pm25=int(data["pm25"]),
            )
        except (KeyError, TypeError, ValueError) as err:
            raise ExampleAirInvalidResponseError(
                f"Unexpected status data: {err!r}"
            ) from err
