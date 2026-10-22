# Reversi

> **Version:** 1.0.0
> **Date:** Oct. 22, 2026
> **Author:** Matteo P.
> **URL:** https://github.com/pmatteo68/reversi

---

## Abstract

A desktop implementation of Reversi built with Python and Tkinter.  Two
players alternate placing discs on a square board.  Black moves first.  A disc
may only be placed where it flanks at least one opponent disc in any of the
eight directions; all flanked discs flip to the placing player's colour.  If a
player has no valid move, the turn passes.  When neither player can move, the
player with more discs on the board wins.

The computer opponent uses a minimax engine with alpha-beta pruning, move
ordering, and a multi-factor evaluation function.  An autoplay mode runs a
fully unattended game from start to finish, exercising the complete game flow
including pass handling and the end-of-game statistics window.

The game runs fully offline with no dependency on external services.

---

## Setup

### Prerequisites

Python is not assumed to be on the system PATH.  The path to the Python
interpreter is configured in the files under `bin/`.  Edit those files if your
Python installation is in a different location before running any script.

### 1. Create the virtual environment (once)

Open a terminal inside the `v<X.Y.Z>` directory and run the setup script.

**Windows:**

```
create_env.cmd
```

**Unix / macOS:**

```
bash create_env.sh
```

The script puts Python on the PATH, creates a virtual environment, activates
it, and installs all dependencies.  If the virtual environment already exists
the script simply activates it without reinstalling anything.

### 2. Launch the game

**Windows:**

```
play.cmd
```

**Unix / macOS:**

```
bash play.sh
```

### Optional: open an environment-ready shell (Windows only)

```
open_env.cmd
```

---

## How to play

### Human vs. Machine

Choose your board size and who goes first on the start screen, then click
**Start Game**.  On your turn, valid-move hints appear on the board; click a
highlighted cell to place your disc.  If you have no valid moves your turn is
passed automatically.  A live stats panel beside the board tracks per-player
metrics throughout the game.  When neither player can move, the winning discs
flash and a summary window appears with statistics and a position-advantage
chart.

Click **Get Hint** at any point on your turn to ask the AI for a suggestion;
the recommended cell flashes and a brief reason (e.g. "Corner capture!" or
"Flips 5 discs") appears in the status bar.

### Autoplay mode

Click **Auto Play** on the start screen.  Both players are controlled by the
AI with no human intervention.  The full game including the summary window
plays out automatically.

### Save and load

Use the **Save Game** and **Load Game** controls to persist and resume a game
at any point.  Saves are plain JSON files.

---

## Configuration

All parameters, labels, and visual settings are externalised into configuration
files under `src/`.  Each file is self-documenting -- read the inline comments
there for accepted values, hard limits, and defaults.  Nothing is hard-coded in
the source.

- Game rules, board size, initial board layout, AI selection, all timings and
  animation settings: `config_game.py`
- Every user-visible string: `config_text.py`
- Active skin: `config_ui.py`
- AI search depth and evaluation weights: the built-in engine's own config file
  under `ai_engines/`

---

## Skins

Set `SKIN` in `src/config_ui.py` to any of the names below (or `"random"` to
pick one at random on every launch).

| Key | Description |
|---|---|
| `default` | Classic green board, black vs white discs |
| `midnight` | Near-black canvas, neon-tinted discs |
| `sunset` | Warm amber and coral tones |
| `ocean` | Deep navy, teal and cyan |
| `forest` | Mossy greens and bark browns |
| `candy` | Pastel bubblegum palette |
| `vivid_1` | Full-saturation primaries on white |
| `vivid_2` | Electric cobalt and cyan on pale blue |
| `mint_gray` | Cool gray canvas with mint accents |
| `black_and_white` | Pure monochrome grayscale |

### Creating a new skin

Copy any existing skin module in `src/skins/`, rename it, edit the constants,
then register the new name in `src/config_ui.py`.  Any attribute left out falls
back automatically to the defaults defined in `config_ui.py`.

---

## AI plugin system

The AI engine is fully pluggable.  Point `AI_ENGINE` in `src/config_game.py`
at any module inside `src/ai_engines/` and it will be loaded automatically.

The built-in engine uses minimax with alpha-beta pruning and an evaluation
function that weighs disc parity, mobility, corner ownership, and X-square
penalties.  Its tuning constants live in its own config file under
`src/ai_engines/`.

### Writing a custom AI engine

1. Create `src/ai_engines/my_engine.py`.
2. Import and subclass `ReversiAIEngine` from `src/ai_engines/base.py`.
3. Implement the three abstract methods:

```python
from ai_engines.base import ReversiAIEngine


class MyEngine(ReversiAIEngine):

    def get_name(self) -> str:
        return "My Custom Engine"

    def reset(self) -> None:
        pass   # clear any per-game state here

    def _compute_next_move(
        self,
        board: list,
        player: int,
        grid_size: int,
    ) -> tuple:
        """
        Return (row, col) for the next move.

        board     -- grid_size x grid_size list of lists.
                     Values: 0 = empty, 1 = Black (Player 1), 2 = White (Player 2).
        player    -- the player whose turn it is (1 or 2).
        grid_size -- the board dimension (e.g. 8 for a standard 8x8 board).

        The base class validates the returned cell.  If it is not in the
        list of valid moves the first valid move is substituted and a warning
        is logged.  Do not handle passes here -- they are resolved by the
        App before _compute_next_move is called.
        """
        from game_logic import get_valid_moves
        moves = get_valid_moves(board, player, grid_size)
        return moves[0]   # replace with your logic


def create() -> MyEngine:
    return MyEngine()
```

4. Set `AI_ENGINE = "my_engine"` in `src/config_game.py`.

The AI facade loads the configured module and calls its `create()` factory
automatically.  In autoplay mode two independent engine instances are created
so the two players do not share state.

**Helper functions available in `game_logic.py`**

| Function | Description |
|---|---|
| `get_valid_moves(board, player, grid_size)` | List of `(row, col)` tuples |
| `get_flipped_cells(board, row, col, player, grid_size)` | Discs that would flip on a given placement |
| `apply_move(board, row, col, player, grid_size)` | Returns `(new_board, flipped_cells)` without mutating the original |
| `count_discs(board, player, grid_size)` | Disc count for one player |
| `count_all_discs(board, grid_size)` | Dict `{player: count}` for both players |

Constants: `EMPTY = 0`, `PLAYER_1 = 1` (Black), `PLAYER_2 = 2` (White),
`OTHER_PLAYER = {1: 2, 2: 1}`.

---

## Save file format

Saved games are plain JSON files.  The format is versioned and
self-documenting; open any saved game in a text editor to inspect it.

---

## Logging

Log output goes to `reversi.log` in the `v1.0.0/` directory and to stderr.
All game events are logged at `DEBUG` level; the start banner and final
game-summary lines are logged at `INFO`.  Control verbosity with the
`GAME_LOG_LEVEL` environment variable (see the files under `bin/`).

---

## Project structure

```
reversi_python/v<X.Y.Z>/
  play.cmd / play.sh    -- launch scripts
  create_env.cmd / .sh  -- virtual environment setup
  open_env.cmd          -- Windows: opens a ready CMD window
  bin/                  -- Python PATH and environment configuration
  requirements.txt      -- pip dependencies
  src/
    main.py             -- entry point
    config_*.py         -- configuration files (game rules, text, UI)
    game_*.py           -- game logic, persistence, statistics
    ai_engine.py        -- AI facade
    ui_*.py             -- UI components (main window, board, panel, stats)
    ai_engines/         -- AI engine implementations (currently: minimax, as documented above)
    skins/              -- visual skin modules (currently: 10 built-in, as documented above)
```

---

## Dependencies

- Python 3.9 or later
- Tkinter (bundled with standard Python distributions)
- matplotlib (optional -- required only for the position-advantage chart)
- All other dependencies: see `requirements.txt`.
