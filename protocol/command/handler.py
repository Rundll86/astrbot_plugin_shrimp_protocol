import inspect

from astrbot.api.event import AstrMessageEvent

from ..exceptions import UntastyFood
from ..server import Server
from .structs import CommandHandler


class Command:
    def __init__(self, handler: CommandHandler) -> None:
        self.handler = handler
        self.argument_count = len(inspect.signature(handler).parameters.values()) - 2

    def run(self, event: AstrMessageEvent, server: Server, *args: str):
        if len(args) != self.argument_count:
            raise UntastyFood()
        self.handler(*args, {"event": event, "server": server})


class CommandStore:
    def __init__(self, parent: "CommandStore | None" = None) -> None:
        self.store: dict[str, Command] = {}
        self.parent = parent

    def run(self, command: str, event: AstrMessageEvent, server: Server, *args: str):
        if command in self.get_full_store():
            self.store[command].run(event, server, *args)

    def command(self, command: str):
        def decorator(func: CommandHandler):
            self.store[command] = Command(func)

        return decorator

    def get_full_store(self) -> dict[str, Command]:
        return (self.parent.get_full_store() if self.parent else {}) | self.store
