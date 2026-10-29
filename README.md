# exampleair

Async Python client for Example Air air quality monitors on your local
network. Built to be used by a Home Assistant integration.

```python
import asyncio

import aiohttp
from exampleair import ExampleAirClient


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        client = ExampleAirClient("192.168.1.50", session)
        status = await client.get_status()
        print(status.name, status.temperature, status.humidity, status.pm25)


asyncio.run(main())
```

The client takes the `aiohttp` session from the caller, so Home Assistant
can pass in its shared session. Errors derive from `ExampleAirError`;
`ExampleAirConnectionError` means the monitor could not be reached.
Values are passed on as the monitor reports them: no unit conversion.

## Development

```
pip install -e ".[test]"
pytest
```

## Releasing

Bump `version` in `pyproject.toml`, tag it (`git tag v0.1.0`), and publish a
GitHub release. The `publish` workflow builds and uploads it to PyPI.

## Dev container

Open the folder in VS Code and choose **Dev Containers: Reopen in Container**.
The container installs the library in editable mode with its test
dependencies, and the tests show up in the Testing panel (or run `pytest`).
