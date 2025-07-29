import random
from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.action = None
        self._score = 0
        self._history = []

    @abstractmethod
    def choose_action(self, action_count):
        pass


class FixedActionPlayer(Player):
    def __init__(self, name, action):
        super().__init__(name)
        self.action = action

    def choose_action(self, action_count):
        return self.action


class RandomActionPlayer(Player):
    def __init__(self, name: str):
        super().__init__(name)
        self.action = None

    def choose_action(self, action_count: int) -> int:
        self.action = random.randrange(0, action_count)
        return self.action
