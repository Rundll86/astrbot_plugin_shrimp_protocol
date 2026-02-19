import asyncio

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

    @filter.command_group("shrimp")
    def shrimp():
        pass

    @shrimp.command("join")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def shrimp_join_group(self, event: AstrMessageEvent):
        try:
            self.server.pot_context.add(event.get_platform_id(), event.session)
            yield event.plain_result("本是同根深，相煎何太急？")
        except Exception as e:
            yield event.plain_result(str(e))

    @shrimp.command("leave")
    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def shrimp_leave_group(self, event: AstrMessageEvent):
        try:
            self.server.pot_context.remove(event.get_group_id(), event.session)
        except Exception as e:
            yield event.plain_result(str(e))

    @filter.event_message_type(filter.EventMessageType.GROUP_MESSAGE)
    async def astrbot_receive(self, event: AstrMessageEvent):
        if self.server.is_message_in_session(event):
            data = parse_shrimp_request(event)
            if data:
                try:
                    await self.server.call(data, event)
                except Exception as e:
                    yield event.plain_result(str(e))
