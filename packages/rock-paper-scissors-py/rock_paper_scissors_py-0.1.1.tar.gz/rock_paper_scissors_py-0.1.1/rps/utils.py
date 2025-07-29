"""
https://www.umop.com/rps.htm
"""

from enum import Enum


class GameOfSize:
    def __init__(self, size):
        self.size = size
        if size == 5:
            self.BEATS = GameOfSizeFive.BEATS.value
        elif size == 7:
            self.BEATS = GameOfSizeSeven.BEATS.value
        elif size == 9:
            self.BEATS = GameOfSizeNine.BEATS.value
        elif size == 11:
            self.BEATS = GameOfSizeEleven.BEATS.value
        elif size == 15:
            self.BEATS = GameOfSizeFifteen.BEATS.value


class GameOfSizeFive(Enum):
    BEATS = {
        0: [2, 3],  # Rock crushes Scissors & Lizard
        1: [0, 4],  # Paper covers Rock & disproves Spock
        2: [1, 3],  # Scissors cuts Paper & decapitates Lizard
        3: [1, 4],  # Lizard eats Paper & poisons Spock
        4: [0, 2],  # Spock vaporizes Rock & smashes Scissors
    }


class GameOfSizeSeven(Enum):
    BEATS = {
        0: [1, 2, 3],  # Rock beats Fire, Scissors, Sponge
        1: [2, 4, 3],  # Fire beats Scissors, Paper, Sponge
        2: [4, 3, 5],  # Scissors beat Paper, Sponge, Air
        3: [4, 5, 6],  # Sponge beats Paper, Air, Water
        4: [5, 0, 6],  # Paper beats Air, Rock, Water
        5: [1, 0, 6],  # Air beats Fire, Rock, Water
        6: [0, 1, 2],  # Water beats Rock, Fire, Scissors
    }


class GameOfSizeNine(Enum):
    BEATS = {
        0: [1, 2, 3, 4],  # Rock beats Fire, Scissors, Human, Sponge
        1: [2, 4, 3, 5],  # Fire beats Scissors, Sponge, Human, Paper
        2: [4, 5, 3, 6],  # Scissors beat Sponge, Paper, Human, Air
        3: [4, 5, 6, 7],  # Human beats Sponge, Paper, Air, Water
        4: [5, 6, 7, 8],  # Sponge beats Paper, Air, Water, Gun
        5: [6, 0, 7, 8],  # Paper beats Air, Rock, Water, Gun
        6: [1, 0, 7, 8],  # Air beats Fire, Rock, Water, Gun
        7: [0, 1, 2, 8],  # Water beats Rock, Fire, Scissors, Gun
        8: [0, 2, 3, 7],  # Gun beats Rock, Scissors, Human, Water
    }


class GameOfSizeEleven(Enum):
    BEATS = {
        0: [1, 2, 3, 5, 6],  # Rock beats Fire, Scissors, Human, Sponge, Tree
        1: [2, 3, 4, 5, 6],  # Fire beats Scissors, Human, Wolf, Sponge, Paper
        2: [3, 4, 5, 6, 7],  # Scissors beat Human, Wolf, Sponge, Paper, Air
        3: [4, 5, 6, 7, 8],  # Human beats Wolf, Sponge, Paper, Air, Water
        4: [5, 6, 7, 8, 9],  # Wolf beats Sponge, Paper, Air, Water, Devil
        5: [6, 7, 8, 9, 10],  # Sponge beats Paper, Air, Water, Devil, Gun
        6: [7, 0, 8, 9, 10],  # Paper beats Air, Rock, Water, Devil, Gun
        7: [1, 0, 8, 9, 10],  # Air beats Fire, Rock, Water, Devil, Gun
        8: [0, 1, 2, 9, 10],  # Water beats Rock, Fire, Scissors, Devil, Gun
        9: [0, 1, 10, 2, 3],  # Devil beats Rock, Fire, Gun, Scissors, Human
        10: [0, 2, 3, 4, 9],  # Gun beats Rock, Scissors, Human, Wolf, Devil
    }


class GameOfSizeFifteen(Enum):
    BEATS = {
        0: [1, 2, 3, 4, 5, 6, 14],  # Rock beats Fire, Scissors, Snake, Human, Tree, Wolf, Gun
        1: [2, 3, 4, 5, 6, 7, 14],  # Fire beats Scissors, Snake, Human, Tree, Wolf, Sponge, Gun
        2: [3, 4, 5, 6, 7, 14, 12],  # Scissors beat Snake, Human, Tree, Wolf, Sponge, Gun, Devil
        3: [4, 5, 6, 7, 8, 9, 12],  # Snake beats Human, Tree, Wolf, Sponge, Paper, Air, Devil
        4: [5, 6, 7, 8, 9, 10, 13],  # Human beats Tree, Wolf, Sponge, Paper, Air, Water, Lightning
        5: [6, 7, 8, 9, 10, 11, 13],  # Tree beats Wolf, Sponge, Paper, Air, Water, Dragon, Lightning
        6: [7, 8, 9, 10, 11, 12, 13],  # Wolf beats Sponge, Paper, Air, Water, Dragon, Devil, Lightning
        7: [8, 9, 10, 11, 12, 13, 14],  # Sponge beats Paper, Air, Water, Dragon, Devil, Lightning, Gun
        8: [9, 10, 11, 12, 13, 14, 1],  # Paper beats Air, Water, Dragon, Devil, Lightning, Gun, Fire
        9: [10, 0, 11, 12, 13, 14, 1],  # Air beats Water, Rock, Dragon, Devil, Lightning, Gun, Fire
        10: [0, 1, 2, 12, 13, 14, 7],  # Water beats Rock, Fire, Scissors, Devil, Lightning, Gun, Sponge
        11: [12, 13, 1, 2, 0, 3, 4],  # Dragon beats Devil, Lightning, Fire, Scissors, Rock, Snake, Human
        12: [0, 1, 2, 3, 4, 11, 10],  # Devil beats Rock, Fire, Scissors, Snake, Human, Dragon, Water
        13: [2, 14, 0, 5, 3, 4, 6],  # Lightning beats Scissors, Gun, Rock, Tree, Snake, Human, Wolf
        14: [0, 2, 3, 4, 5, 6, 10],  # Gun beats Rock, Scissors, Snake, Human, Tree, Wolf, Water
    }
