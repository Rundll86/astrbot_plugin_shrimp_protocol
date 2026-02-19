from typing import Any

import socketio
from aiohttp import web

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, MessageChain
from astrbot.api.star import Star
from astrbot.core.message.components import Plain

from .command.handler import CommandStore
from .constants import DEFAULT_CHANNEL_NAME
from .parse import ShrimpRequest
from .pot import PotContext


class Server:
    def __init__(
        self,
        star: Star,
        command_store: CommandStore,
        pot_context: PotContext | None = None,
        channel_name: str = DEFAULT_CHANNEL_NAME,
    ) -> None:
        self.app = web.Application()
        self.socket = socketio.AsyncServer(
            async_mode="aiohttp", cors_allowed_origins="*"
        )
        self.socket.attach(self.app)
        self.star = star
        self.channel_name = channel_name
        self.pot_context = pot_context if pot_context else PotContext()
        self.command_store = command_store

        async def socket_receive(text, json):
            logger.info(f"调料入锅：{text}")
            for session in self.pot_context.get_sessions():
                await self.star.context.send_message(
                    session,
                    MessageChain(chain=[Plain(f"shrimp://cook/{json['data']}")]),
                )

        self.socket.on(self.channel_name, socket_receive)

    def is_message_in_session(self, event: AstrMessageEvent):
        return self.pot_context.match(event.get_platform_id(), event.session)

    async def emit(self, data: Any):
        await self.socket.emit(self.channel_name, data)

    async def call(self, request: ShrimpRequest, event: AstrMessageEvent):
        self.command_store.run(request[0], event, self, *request[1])

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        await web.TCPSite(self.runner, "0.0.0.0", 25565).start()

    async def stop(self):
        await self.runner.cleanup()
