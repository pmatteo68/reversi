"""
Game logic configuration for Reversi.
All gameplay-affecting parameters live here.

Hard limits on board parameters:
  GRID_SIZE must be even: Reversi requires 4 initial discs in the center in a
    2x2 arrangement; an odd grid size has no well-defined center pair.
    Supported even values: 4, 6, 8, 10, 12.
  GRID_SIZE_MAX <= 12: at CELL_SIZE=64 and GRID_SIZE=12 the canvas is
    12*64 + 2*24 = 816 px wide; exceeding that risks overflow on common displays.
  GRID_SIZE_MIN >= 4: the 4x4 board is the smallest that allows a valid
    starting position and at least one playable move per player.

Structural constant: only 2 players are supported. NUM_PLAYERS=2 is referenced
wherever the code assumes exactly two players; changing it is not supported.
"""

# -- Number of players (structural constant; only 2 is supported) ---------------
NUM_PLAYERS = 2

# -- Initial discs per player (always 2 in standard Reversi) --------------------
# Structural constant: Reversi always begins with a 2x2 centre arrangement.
NUM_INITIAL_DISCS_PER_PLAYER = 2

# -- Initial board state -------------------------------------------------------
# Controls which discs are placed before the first move.
#
#   "standard"
#       Classic Reversi starting position: four discs in a 2x2 centre.
#       Adapts automatically to any even grid size.
#
#   "empty"
#       No discs placed before the first move.  The flanking rule still applies,
#       so on an empty board neither player can move and the game ends immediately
#       unless you also override the AI or use this with house rules.
#       Provided for experimentation only.
#
#   [(row, col, player), ...]
#       Explicit list of disc placements.  row and col are 0-indexed from the
#       top-left corner of the grid.  player is 1 (Black) or 2 (White).
#       Entries whose coordinates fall outside the current grid size are silently
#       ignored, so a custom state defined for an 8x8 board still loads safely
#       on a 4x4 board (minus any out-of-range discs).
#       Example -- standard 8x8 position written explicitly:
#           [(3, 3, 2), (3, 4, 1), (4, 3, 1), (4, 4, 2)]
INITIAL_BOARD_STATE = "standard"

# -- Board size (square grid; must be even) ------------------------------------
# Only even values are valid. Step between dropdown options is 2.
GRID_SIZE_STEP    = 2
GRID_SIZE_MIN     = 4
GRID_SIZE_MAX     = 12
GRID_SIZE_DEFAULT = 8

# -- AI engine -----------------------------------------------------------------
AI_ENGINE = "minimax_alphabeta"   # module name inside ai_engines/

# -- AI animation timing -------------------------------------------------------
AI_THINK_DELAY_MS      = 400    # pause before AI move begins (ms)
AI_INTER_MOVE_PAUSE_MS = 300    # pause after each committed move before next phase (ms)

# -- Pass-notification display -------------------------------------------------
PASS_NOTIFY_DURATION_MS = 1200  # how long the "player passes" notice is shown (ms)

# -- Disc placement pop animation ----------------------------------------------
# A brief "pop" effect when a disc is placed on the board.
PLACE_ANIM_ENABLED = True
PLACE_ANIM_STEPS   = 4      # number of size steps in the pop animation
PLACE_ANIM_STEP_MS = 30     # ms per step

# -- Disc flip animation -------------------------------------------------------
# Flipped discs cycle between opponent color and player color.
FLIP_ANIM_ENABLED      = True
FLIP_FLASH_COUNT       = 4    # number of on/off half-cycles per batch
FLIP_FLASH_INTERVAL_MS = 80   # ms per half-cycle

# -- Win flash animation -------------------------------------------------------
WIN_FLASH_COUNT       = 6    # number of on/off half-cycles for winning discs
WIN_FLASH_INTERVAL_MS = 150  # ms per half-cycle

# -- Valid-move hint display ---------------------------------------------------
SHOW_VALID_MOVE_HINTS = True  # show dots on valid-move cells during human turn

# -- AI move-hint (Get Hint button) --------------------------------------------
# The hint overlay is a border rectangle that flashes around the suggested cell.
# Total visible duration = HINT_FLASH_COUNT * HINT_FLASH_INTERVAL_MS ms.
# With the defaults (6 x 250 ms = 1500 ms) the hint border flashes 3 times.
HINT_FLASH_COUNT       = 6    # number of on/off half-cycles for hint border
HINT_FLASH_INTERVAL_MS = 250  # ms per half-cycle

# Minimum number of discs flipped by a hint move before the reason phrase
# mentions the flip count (e.g. "Flips 5 discs").  Below this threshold a
# more generic label is used instead.
HINT_FLIP_MENTION_MIN  = 4

# -- Autoplay (testing / demo) -------------------------------------------------
AUTOPLAY_MOVE_DELAY_MS = 600  # delay before each autoplay move (ms)

# -- Start-screen defaults -----------------------------------------------------
# "human" = human plays as Black (Player 1, goes first)
# "ai"    = human plays as White (Player 2, AI goes first as Black)
DEFAULT_FIRST_PLAYER = "human"
