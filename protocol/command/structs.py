from collections.abc import AsyncGenerator, Callable

from astrbot.api.event import MessageEventResult

CommandHandler = Callable[..., AsyncGenerator[MessageEventResult] | None]
