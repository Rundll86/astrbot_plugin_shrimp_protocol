from typing import TYPE_CHECKING

from astrbot.api.event import AstrMessageEvent

from .handler import CommandStore

if TYPE_CHECKING:
    from ..server import Server

default_store = CommandStore()


@default_store.command(need_session=True)
async def cook(data: str, event: AstrMessageEvent, server: "Server"):
    await server.emit({"data": data, "peer": event.get_platform_id()})
    yield event.plain_result("有点好吃哈。")


@default_store.command()
async def join(event: AstrMessageEvent, server: "Server"):
    try:
        server.pot_context.add(event.get_platform_id(), event.session)
        yield event.plain_result("煮豆燃豆萁，豆在釜中泣。")
    except Exception as e:
        yield event.plain_result(str(e))


@default_store.command()
async def leave(event: AstrMessageEvent, server: "Server"):
    try:
        server.pot_context.remove(event.get_platform_id(), event.session)
        yield event.plain_result("本是同根深，相煎何太急？")
    except Exception as e:
        yield event.plain_result(str(e))


def init():
    return default_store
