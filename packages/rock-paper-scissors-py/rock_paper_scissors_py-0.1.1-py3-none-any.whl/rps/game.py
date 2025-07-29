from typing import List
from .player import Player
from .utils import GameOfSize


class Game:
    def __init__(self, players, action_count: int) -> None:
        if action_count % 2 == 0:
            raise ValueError(f"Action count must be odd")
        if action_count < 0:
            raise ValueError(f"Action count must be greater than or equal to 3")

        if not players or len(players) < 2:
            raise ValueError(f"Must have at least two players")

        self._players = players
        self._action_count = action_count
        self._beats = {}

        # set beats/game rules created by https://www.umop.com/rps.htm
        if 5 <= action_count <= 15 and action_count % 2 != 0 and action_count != 13:
            self._beats = GameOfSize(action_count).BEATS
        else:
            # if the action count is greater than 15 or is 13, then generate the beats dictionary (symmetric game)
            self.generate_beats()

        self.check_player_action()

    @property
    def beats(self):
        return self._beats

    @property
    def players(self):
        return self._players

    def generate_beats(self):
        """generate beats dictionary for games with action size 17 or greater"""
        beats = {}
        half = (self._action_count - 1) // 2  # number of actions each one beats
        for i in range(self._action_count):
            beat_list = []
            for k in range(1, half + 1):
                beat_index = (i + k) % self._action_count
                beat_list.append(beat_index)
            beats[i] = beat_list
        self._beats = beats

    def check_player_action(self):
        valid_players = []
        for player in self._players:
            # Only check action for FixedActionPlayer
            if hasattr(player, "action") and player.action is not None:
                if 0 <= player.action < self._action_count:
                    valid_players.append(player)
            else:
                valid_players.append(
                    player
                )  # Keep players that don't have action attribute
        self._players = valid_players

    def eliminate(self, actions: List[int]) -> List[int]:
        """get the list of players that should be eliminated"""
        n = len(self._players)
        beats = self._beats
        eliminated = []
        result = []

        for i in range(n):
            my_action = actions[i]
            for j in range(n):
                if i == j:
                    continue
                opponent_action = actions[j]
                if my_action in beats.get(opponent_action, []):
                    eliminated.append(i)
                    break  # Player i is beaten by someone → eliminate

        # if it's a tie (all actions are played), no one is eliminated
        if len(eliminated) == len(actions):
            return []

        for n in eliminated:
            for i, p in enumerate(self._players):
                if i == n:
                    result.append(p)

        print(
            "eliminated players: ",
            [(p.name, p.action) for p in result],
        )

        return eliminated

    def _get_winner(self, actions: List[int]) -> List[Player]:
        # print(f"name: {[(p.name, p.action) for p in self._players]}")
        eliminated = self.eliminate(actions)
        winners = []

        for i in range(len(self._players)):
            if i in eliminated:
                continue
            winners.append(self._players[i])
        return winners

    def play_round(self):
        actions = [player.choose_action(self._action_count) for player in self._players]
        print(
            "current players: ",
            [(p.name, p.action) for p in self._players],
        )
        self._players = self._get_winner(actions)

        return self._players

    def play(self):
        round = 1
        while len(self._players) > 1:
            print(f"Round {round}")
            self.play_round()
            round += 1
            print(" ")

        print(f"Winner is {self._players[0].name}")
        return self._players[0].name
