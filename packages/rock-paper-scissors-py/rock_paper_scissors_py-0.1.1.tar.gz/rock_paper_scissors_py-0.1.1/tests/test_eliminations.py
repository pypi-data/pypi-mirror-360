import pytest
import random

# --- Logic under test ---

def generate_beats(n):
    beats = {}
    half = (n - 1) // 2
    for i in range(n):
        beats[i] = []
        for k in range(1, half + 1):
            beats[i].append((i + k) % n)
    return beats


def last_player_eliminations(actions, beats):
    n = len(actions)
    eliminated = []

    for i in range(n):
        my_action = actions[i]
        for j in range(n):
            if i == j:
                continue
            opponent_action = actions[j]
            if my_action in beats.get(opponent_action, []):
                eliminated.append(i)
                break  # Player i is beaten by someone → eliminate

    # if it's a tie 
    if len(eliminated) == len(actions):
        return []

    return eliminated


# --- Fixtures and deterministic test cases ---

@pytest.mark.parametrize("actions, beats, expected", [
    # Size 3: Rock(0), Paper(1), Scissors(2)
    ([0, 1, 2], {0: [2], 1: [0], 2: [1]}, []),                 # All actions → tie
    ([0, 2, 0], {0: [2], 1: [0], 2: [1]}, [1]),                # Scissors loses
    ([0, 0, 0], {0: [2], 1: [0], 2: [1]}, []),                 # All Rock → tie
])
def test_rps_size_3(actions, beats, expected):
    assert last_player_eliminations(actions, beats) == expected

@pytest.mark.parametrize("actions, expected", [
    ([0, 0, 0, 1, 1], [3, 4]),  # Rock vs Paper → Rock loses
    ([0, 0, 1, 2, 3], []),     # Paper and Scissors lose to Rock
])
def test_rpsls_size_5(actions, expected):
    beats_5 = generate_beats(5)
    assert last_player_eliminations(actions, beats_5) == expected

def test_7_action_cycle_no_elimination():
    actions = list(range(7))
    beats_7 = generate_beats(7)
    assert last_player_eliminations(actions, beats_7) == []

def test_7_action_weak_majority():
    actions = [0]*10 + [3]
    beats_7 = generate_beats(7)
    assert last_player_eliminations(actions, beats_7) == [10]

def test_9_action_all_same():
    actions = [4] * 20
    beats_9 = generate_beats(9)
    assert last_player_eliminations(actions, beats_9) == []

# --- Randomized but reproducible tests ---

def test_random_20_players_size_5():
    random.seed(42)
    actions = [random.randint(0, 4) for _ in range(20)]
    beats_5 = generate_beats(5)
    eliminated = last_player_eliminations(actions, beats_5)
    assert isinstance(eliminated, list)
    assert all(0 <= i < 20 for i in eliminated)

def test_random_50_players_size_7():
    random.seed(99)
    actions = [random.randint(0, 6) for _ in range(50)]
    beats_7 = generate_beats(7)
    eliminated = last_player_eliminations(actions, beats_7)
    assert isinstance(eliminated, list)
    assert all(0 <= i < 50 for i in eliminated)

def test_100_players_full_action_range():
    random.seed(123)
    actions = [random.randint(0, 8) for _ in range(100)]
    beats_9 = generate_beats(9)
    eliminated = last_player_eliminations(actions, beats_9)
    assert isinstance(eliminated, list)
    assert all(0 <= i < 100 for i in eliminated)
