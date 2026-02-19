from astrbot.core.platform.message_session import MessageSession

from .exceptions import BrokenPotRequest


class PotDescriptor:
    def __init__(self, bot: str, session: MessageSession) -> None:
        self.bot = bot
        self.session = session

    def __eq__(self, value: object) -> bool:
        if isinstance(value, PotDescriptor):
            return value.bot == self.bot and value.session == self.session
        else:
            return False


class PotContext:
    def __init__(self) -> None:
        self.pots: list[PotDescriptor] = []

    def add(self, bot: str, session: MessageSession):
        if self.includes(bot, session):
            raise BrokenPotRequest("锅装不下了。")
        self.pots.append(PotDescriptor(bot, session))

    def remove(self, bot: str, session: MessageSession):
        if not self.includes(bot, session):
            raise BrokenPotRequest("锅已经烧干了。")
        self.pots.remove(PotDescriptor(bot, session))

    def get_bots(self):
        return [x.bot for x in self.pots]

    def get_sessions(self):
        return [x.session for x in self.pots]

    def filter(self, bot: str, session: MessageSession):
        return filter(lambda x: x == PotDescriptor(bot, session), self.pots)

    def includes(self, bot: str, session: MessageSession):
        return len([*self.filter(bot, session)]) > 0
