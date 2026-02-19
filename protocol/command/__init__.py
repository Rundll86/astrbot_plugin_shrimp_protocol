from astrbot.api.event import AstrMessageEvent

from ..server import Server
from .handler import CommandStore

default_store = CommandStore()


@default_store.command("cook")
async def cook(data: str, event: AstrMessageEvent, server: Server):
    await server.emit(
        {
            "data": data,
            "peer": event.get_platform_id(),
        }
    )


def init():
    return default_store
