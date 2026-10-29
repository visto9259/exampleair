"""Exceptions of the exampleair library."""


class ExampleAirError(Exception):
    """Base error of the library."""


class ExampleAirConnectionError(ExampleAirError):
    """The monitor could not be reached."""


class ExampleAirInvalidResponseError(ExampleAirError):
    """The monitor answered with something the library cannot read."""
