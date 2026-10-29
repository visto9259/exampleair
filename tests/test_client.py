"""Tests for the Example Air client, against a fake monitor."""

import asyncio

from aiohttp import ClientSession, web
import pytest

from exampleair import (
    ExampleAirClient,
    ExampleAirConnectionError,
    ExampleAirInvalidResponseError,
    Status,
)

GOOD = {
    "serial_number": "EA123456",
    "name": "Living room",
    "firmware": "1.2.0",
    "temperature": 21.5,
    "humidity": 45.0,
    "pm25": 8,
}


async def _client(aiohttp_server, handler) -> tuple[ExampleAirClient, ClientSession]:
    app = web.Application()
    app.router.add_get("/status", handler)
    server = await aiohttp_server(app)
    session = ClientSession()
    client = ExampleAirClient(f"{server.host}:{server.port}", session, timeout=0.5)
    return client, session


async def test_get_status(aiohttp_server) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.json_response(GOOD)

    client, session = await _client(aiohttp_server, handler)
    async with session:
        status = await client.get_status()

    assert status == Status(
        serial_number="EA123456",
        name="Living room",
        firmware="1.2.0",
        temperature=21.5,
        humidity=45.0,
        pm25=8,
    )


async def test_http_error(aiohttp_server) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(status=500)

    client, session = await _client(aiohttp_server, handler)
    async with session:
        with pytest.raises(ExampleAirConnectionError):
            await client.get_status()


async def test_timeout(aiohttp_server) -> None:
    async def handler(_: web.Request) -> web.Response:
        await asyncio.sleep(2)
        return web.json_response(GOOD)

    client, session = await _client(aiohttp_server, handler)
    async with session:
        with pytest.raises(ExampleAirConnectionError):
            await client.get_status()


async def test_unreachable() -> None:
    async with ClientSession() as session:
        client = ExampleAirClient("127.0.0.1:1", session, timeout=0.5)
        with pytest.raises(ExampleAirConnectionError):
            await client.get_status()


@pytest.mark.parametrize(
    "body",
    [
        pytest.param("not json", id="not-json"),
        pytest.param("[1, 2]", id="not-an-object"),
        pytest.param('{"name": "x"}', id="missing-keys"),
        pytest.param(
            '{"serial_number": "1", "name": "x", "firmware": "1",'
            ' "temperature": "hot", "humidity": 1, "pm25": 1}',
            id="bad-value",
        ),
    ],
)
async def test_invalid_response(aiohttp_server, body: str) -> None:
    async def handler(_: web.Request) -> web.Response:
        return web.Response(text=body)

    client, session = await _client(aiohttp_server, handler)
    async with session:
        with pytest.raises(ExampleAirInvalidResponseError):
            await client.get_status()
