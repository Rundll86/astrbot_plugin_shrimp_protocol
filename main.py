import asyncio
from venv import logger

from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Star

from .protocol import command
from .protocol.parse import parse_shrimp_request
from .protocol.server import Server


class ShrimpProtocolPlugin(Star):
    def __init__(self, context, config):
        super().__init__(context, config)
        self.server = Server(self, command.init())
        asyncio.create_task(self.server.start())

    async def terminate(self):
        asyncio.create_task(self.server.stop())

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def astrbot_receive(self, event: AstrMessageEvent):
        request = parse_shrimp_request(event)
        if request:
            logger.info(f"已解析调料：{request}")
            try:
                result = await self.server.call_async(request, event)
                logger.info(type(result))
                yield result
            except Exception as e:
                yield event.plain_result(str(e))
