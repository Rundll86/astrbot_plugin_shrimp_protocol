from collections.abc import AsyncGenerator, Callable
from types import CoroutineType

from astrbot.api.event import MessageEventResult

CommandHandler = Callable[
    ..., AsyncGenerator[MessageEventResult] | CoroutineType | None
]
