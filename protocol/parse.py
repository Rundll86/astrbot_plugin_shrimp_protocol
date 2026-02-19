from urllib.parse import urlparse

from astrbot.api.event import AstrMessageEvent

ShrimpRequest = tuple[str, list[str]]


def parse_shrimp_request(
    event: AstrMessageEvent,
) -> ShrimpRequest | None:
    url = urlparse(event.message_str)
    if url.scheme != "shrimp":
        return None
    if url.hostname:
        command = url.hostname
    else:
        return None
    if url.path.startswith("/"):
        args = url.path[1:]
    else:
        args = url.path
    args = args.split("/")
    return command, args
