import asyncio
from venv import logger

import socketio
from aiohttp import web

from astrbot.api.event import AstrMessageEvent, MessageChain, filter
from astrbot.api.star import Star
from astrbot.core.message.components import Plain
from astrbot.core.platform.message_session import MessageSession

from .constants import SOCKETIO_MESSAGE_EVENT
from .utils import parse_shrimp_request


class ShrimpProtocolPlugin(Star):
    potMaps: dict[str, list[MessageSession]] = {}

    def __init__(self, context, config):
        super().__init__(context, config)
        self.protocol = ShrimpProtocol(self)
        asyncio.create_task(self.protocol.start())

    async def terminate(self):
        logger.info("Shrimp.Protocol对等体正在清理。")
        asyncio.create_task(self.protocol.stop())

    @filter.command_group("shrimp")
    def shrimp():
        pass

    @shrimp.command("add-pot")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def shrimp_start_group(self, event: AstrMessageEvent):
        if event.get_platform_id() not in self.potMaps:
            self.potMaps[event.get_platform_id()] = []
        if event.session in self.potMaps[event.get_platform_id()]:
            yield event.plain_result("太多了，锅装不下了！")
        else:
            self.potMaps[event.get_platform_id()].append(event.session)
            yield event.plain_result("本是同根深，相煎何太急？")

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def astrbot_receive(self, event: AstrMessageEvent):
        if (
            event.get_platform_id() in self.potMaps
            and event.session in self.potMaps[event.get_platform_id()]
        ):
            data = parse_shrimp_request(event)
            if data:
                if len(data) == 2:
                    if data[0] == "cook":
                        await self.protocol.socket.emit(
                            SOCKETIO_MESSAGE_EVENT,
                            {
                                "data": data[1],
                                "peer": event.get_platform_id(),
                            },
                        )
                else:
                    yield event.plain_result("好难吃。")


class ShrimpProtocol:
    def __init__(self, star: ShrimpProtocolPlugin) -> None:
        self.app = web.Application()
        self.socket = socketio.AsyncServer(
            async_mode="aiohttp", cors_allowed_origins="*"
        )
        self.socket.attach(self.app)
        self.star = star

        async def socket_receive(text, json):
            for pots in self.star.potMaps.values():
                for pot in pots:
                    await self.star.context.send_message(
                        pot,
                        MessageChain(chain=[Plain(f"shrimp://cook/{json['data']}")]),
                    )

        self.socket.on(SOCKETIO_MESSAGE_EVENT, socket_receive)

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        await web.TCPSite(self.runner, "0.0.0.0", 25565).start()

    async def stop(self):
        await self.runner.cleanup()
