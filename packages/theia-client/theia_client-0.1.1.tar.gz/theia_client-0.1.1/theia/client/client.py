import ipaddress
from typing import AsyncGenerator

import aiohttp

from theia.core import primitives, web

_DEFAULT_TIMEOUT_S = 2
_DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=_DEFAULT_TIMEOUT_S)


class Client:
    """A basic client for interacting with the Theia server.

    Offers basic asyncio-based HTTP and WebSocket connections to the server
    """

    def __init__(self, host: ipaddress.IPv4Address | str, port: int):
        self._host = host
        self._port = port
        self._session: aiohttp.ClientSession | None = None

    def open(self) -> None:
        """Opens an HTTP session linking the client to the server."""
        if self._session is None:
            self._session = aiohttp.ClientSession(timeout=_DEFAULT_TIMEOUT)

    async def close(self) -> None:
        """Closes the HTTP session linking the client to the server."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def status_subscription(
        self, frequency: float | None = None
    ) -> AsyncGenerator[primitives.SystemStatus, None]:
        """Generates status for the system.

        Establishes a websocket with the server and yields the status at the requested
        frequency. If no frequency is configured, will produce a status at 1 hz. May
        raise a aiohttp.client_exceptions.WSMessageTypeError if the server shuts down
        while the client is still connected.
        """
        if not self._session:
            raise RuntimeError("Client is not open.")

        url = _status_ws_url(self._host, self._port, frequency)
        async with self._session.ws_connect(url) as ws:
            while not ws.closed:
                raw_status = await ws.receive_json()
                yield primitives.SystemStatus.from_dict(raw_status)

    async def get_image(self, stream_id: str, pts: int, draw: bool = False) -> bytes:
        """Gets the image, with or w/o bounding boxes, corresponding to the given pts.

        Raises a RuntimeError if the client is not open.
        """
        if not self._session:
            raise RuntimeError("Client is not open.")

        url = _stream_image_http_url(self._host, self._port, stream_id, pts, draw)
        async with self._session.get(url) as resp:
            resp.raise_for_status()
            image = await resp.read()
            return image


def _status_ws_url(
    host: ipaddress.IPv4Address | str, port: int, frequency: float | None
) -> str:
    base_url = f"ws://{host}:{port}{web.status_path()}"
    if frequency is not None:
        base_url += f"?frequency={frequency}"
    return base_url


def _stream_image_http_url(
    host: ipaddress.IPv4Address | str, port: int, stream_id: str, pts: int, draw: bool
) -> str:
    """Returns the HTTP URL for a stream's image endpoint."""
    return f"http://{host}:{port}{web.stream_image_path(stream_id, pts)}?draw={draw}"
