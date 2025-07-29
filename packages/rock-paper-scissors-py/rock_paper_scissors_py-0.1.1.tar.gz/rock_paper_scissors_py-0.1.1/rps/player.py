import random
from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, name: str, action=None) -> None:
        self.name = name
        self.action = action

    @abstractmethod
    def choose_action(self, action_count: int) -> int:
        pass


class FixedActionPlayer(Player):
    def __init__(self, name: str, action: int) -> None:
        super().__init__(name)
        self.action = action

    def choose_action(self, action_count: int) -> int:
        return self.action


class RandomActionPlayer(Player):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.action = None

    def choose_action(self, action_count: int) -> int:
        self.action = random.randrange(0, action_count)
        return self.action
