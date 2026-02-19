class ShrimpException(Exception):
    def __init__(self, msg: str, code: int) -> None:
        super().__init__(f"Shrimp {code}: {msg}")


class BrokenPotRequest(ShrimpException):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, 400)


class UntastyFood(ShrimpException):
    def __init__(self) -> None:
        super().__init__("太难吃了。", 400)


class CannotTasteAir(ShrimpException):
    def __init__(self) -> None:
        super().__init__("你不能品尝虚空。", 404)


class LockedShrimp(ShrimpException):
    def __init__(self) -> None:
        super().__init__("此虾已被锁定。", 403)
