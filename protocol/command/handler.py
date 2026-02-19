import inspect
from typing import TYPE_CHECKING

from astrbot.api.event import AstrMessageEvent

from ..constants import CALL_METHOD_HEAD
from ..exceptions import CannotTasteAir, LockedShrimp, UntastyFood
from .structs import CommandHandler

if TYPE_CHECKING:
    from ..server import Server


class Command:
    def __init__(self, handler: CommandHandler, need_session: bool = False) -> None:
        self.handler = handler
        self.argument_count = len(inspect.signature(handler).parameters.values()) - 2
        self.need_session = need_session

    async def run(self, event: AstrMessageEvent, server: "Server", *args: str):
        if len(args) != self.argument_count:
            raise UntastyFood()
        return self.handler(*args, **{"event": event, "server": server})


class CommandStore:
    def __init__(self, parent: "CommandStore | None" = None) -> None:
        self.store: dict[str, Command] = {}
        self.parent = parent

    async def run(
        self, command_name: str, event: AstrMessageEvent, server: "Server", *args: str
    ):
        full = self.get_full_store()
        if command_name in full:
            command = self.store[command_name]
            if command.need_session and not server.is_message_in_session(event):
                raise LockedShrimp()
            else:
                return await command.run(event, server, *args)
        else:
            raise CannotTasteAir()

    def command(self, **kwargs):
        def decorator(func: CommandHandler):
            command = func.__name__
            self.store[command] = Command(func, **kwargs)

            def wrapper(*args: str):
                return f"{CALL_METHOD_HEAD}shrimp://{command}/{'/'.join(args)}"

            return wrapper

        return decorator

    def get_full_store(self) -> dict[str, Command]:
        return (self.parent.get_full_store() if self.parent else {}) | self.store
