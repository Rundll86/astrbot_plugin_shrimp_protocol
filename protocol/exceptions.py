class BrokenPotRequest(Exception):
    pass


class UntastyFood(Exception):
    def __init__(self) -> None:
        super().__init__("太难吃了。")
