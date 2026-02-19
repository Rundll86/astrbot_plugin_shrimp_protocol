from urllib.parse import urlparse

from astrbot.api.event import AstrMessageEvent

from .constants import CALL_METHOD_HEAD

ShrimpRequest = tuple[str, list[str]]


def parse_shrimp_request(
    event: AstrMessageEvent,
) -> ShrimpRequest | None:
    if not event.message_str.startswith(CALL_METHOD_HEAD):
        return None
    url = urlparse(event.message_str[len(CALL_METHOD_HEAD) :])
    if url.scheme != "shrimp":
        return None
    if url.hostname:
        command = url.hostname
    else:
        return None
    args = url.path.strip("/").split("/")
    return command, list(filter(bool, args))
