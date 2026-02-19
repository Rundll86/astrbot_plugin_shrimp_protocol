from urllib.parse import urlparse

from astrbot.api.event import AstrMessageEvent


def parse_shrimp_request(event: AstrMessageEvent):
    url = urlparse(event.message_str)
    if url.scheme != "shrimp":
        return None
    if url.hostname:
        first = url.hostname
    else:
        return None
    if url.path.startswith("/"):
        operation = url.path[1:]
    else:
        operation = url.path
    return [first, *operation.split("/")]
