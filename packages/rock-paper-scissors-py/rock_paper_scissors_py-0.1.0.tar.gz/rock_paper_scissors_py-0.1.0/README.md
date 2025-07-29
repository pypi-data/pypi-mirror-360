# rock-paper-scissors-py

Multi-player and multi-action Rock, Paper, Scissors game client.

## Installation

To install, run the following commands:

```bash
git@github.com:jwc20/rock-paper-scissors-py.git
cd rock-paper-scissors-py
```

To use the engine, first setup and activate a python virtual environment (venv)

```bash
python3 -m venv .venv

# or use astral/uv
uv venv --python 3.13


. ./.venv/bin/activate
```

Install from requirements.txt

```bash
pip3 install -r requirements.txt

# or
uv add -r requirements.txt
```

## Usage:

To import, type

```python
import rps
```

Set the number of actions allowed in the game

```python
action_three = 3 # rock, paper, scissors
action_five = 5 # rock, paper, scissors, Spock, lizard
```

Set the players with either fixed or random actions

```python
player_jae = rps.FixedActionPlayer("Jae", 0) # always plays Rock, like an idiot

# bunch of random players with random actions
random_player_names = [f"random{i}" for i in range(20)]
random_players = [RandomActionPlayer(name) for name in random_player_names]
```

Set the game and play

```python
game = rps.Game(random_players, action_three)

game.play()
```

### Example

Run the `example.py` in the root directory

```bash
python example.py

# or

uv run example.py
```

---

## Note

Game consists of `m` players and `n` actions where `m >= 2` and `n >= 3` and `n` is an odd number.

Actions are hand gestures played by the players (rock, paper, scissors).

If the number of actions set in the game is between 5 and 15, the game uses the rules made by [Sam Kass](https://www.samkass.com/theories/RPSSL.html) and [David C. Lovelace](https://www.umop.com/rps.htm).

---

## See also:

- https://www.umop.com/rps.htm

- https://www.samkass.com/theories/RPSSL.html
