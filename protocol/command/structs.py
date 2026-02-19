from collections.abc import Callable
from types import CoroutineType

CommandHandler = Callable[..., CoroutineType | None]
