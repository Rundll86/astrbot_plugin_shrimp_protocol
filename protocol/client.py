import asyncio
from collections.abc import Callable
from typing import Any

import socketio

from .constants import DEFAULT_CHANNEL_NAME


class ClientConfig:
    def __init__(
        self,
        server_url: str = "http://localhost:25565",
        channel_name: str = DEFAULT_CHANNEL_NAME,
        peer: str = "default_peer",
        reconnect_attempts: int = 5,
        reconnect_delay: float = 3.0,
    ) -> None:
        self.server_url = server_url
        self.channel_name = channel_name
        self.peer = peer
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay


class Client:
    def __init__(self, config: ClientConfig | None = None) -> None:
        self.config = config if config else ClientConfig()
        self.sio = socketio.AsyncClient()
        self._data_handler: Callable[[str], Any] | None = None
        self._connected = False
        self._reconnect_count = 0
        self.sio.on("connect", self._on_connect)
        self.sio.on("disconnect", self._on_disconnect)
        self.sio.on(self.config.channel_name, self._on_channel_data)

    def on_data(self, handler: Callable[[str], Any]) -> Callable[[str], Any]:
        self._data_handler = handler
        return handler

    async def _on_connect(self) -> None:
        self._connected = True
        self._reconnect_count = 0

    async def _on_disconnect(self) -> None:
        self._connected = False
        if self._reconnect_count < self.config.reconnect_attempts:
            self._reconnect_count += 1
            await asyncio.sleep(self.config.reconnect_delay)
            await self.connect()

    async def _on_channel_data(self, data: dict[str, Any]) -> None:
        if data.get("peer") != self.config.peer:
            return
        received_data = data.get("data", "")
        if self._data_handler:
            result = self._data_handler(received_data)
            if asyncio.iscoroutine(result):
                await result

    async def connect(self) -> None:
        if self._connected:
            return
        await self.sio.connect(self.config.server_url)

    async def disconnect(self) -> None:
        if not self._connected:
            return
        await self.sio.disconnect()

    def is_connected(self) -> bool:
        return self._connected

    async def send(self, data: str) -> None:
        if not self._connected:
            raise RuntimeError("未连接到服务器")
        payload = {"data": data, "peer": self.config.peer}
        await self.sio.emit(self.config.channel_name, payload)

    async def __aenter__(self) -> "Client":
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.disconnect()
