"""All user-visible text for Reversi -- change here to localise or rebrand."""

from sw_metadata import getSWName, getVersion
from config_game import GRID_SIZE_DEFAULT, NUM_PLAYERS
import ai_engine
import config_ui as _CU

# -- Window -------------------------------------------------------------------
WINDOW_TITLE = getSWName() + " v. " + getVersion()

# -- Start screen -------------------------------------------------------------
START_TITLE    = getSWName()
START_SUBTITLE = "Flank and flip your way to victory!"

START_ENGINE_LABEL = "AI engine:"
START_WHO_FIRST    = "Who goes first?"
START_FIRST_HUMAN  = "  Human  "
START_FIRST_AI     = "  Machine  "

START_GRID_LABEL   = "Board size:"

def make_rules_hint(grid_size: int) -> str:
    return str(grid_size) + " x " + str(grid_size) + " board  |  " + PLAYER_1_NAME + " moves first"

# -- Buttons ------------------------------------------------------------------
BTN_START     = "  Start Game  "
BTN_CLOSE     = "  Close  "
BTN_NEW_GAME  = "New Game"
BTN_SAVE_GAME = "Save Game"
BTN_LOAD_GAME = "Load Game"
BTN_AUTOPLAY  = "  Auto Play  "
BTN_GET_HINT  = "Get Hint"
BTN_EXIT      = "Exit"
BTN_QUIT      = "Quit"

# -- Status messages ----------------------------------------------------------
STATUS_HUMAN_TURN    = "Your turn -- click a highlighted cell to place your disc"
STATUS_AI_TURN       = "Machine is thinking..."
STATUS_ANIMATING     = "..."
STATUS_HINT_THINKING = "Hint: thinking..."
STATUS_HINT_READY    = "Hint: suggested move is highlighted"
STATUS_HINT_NO_MOVES = "Hint: no valid moves available"
STATUS_HINT_REASON   = "Hint: {reason}"

HINT_REASON_CORNER  = "Corner capture!"
HINT_REASON_FLIPS   = "Flips {n} discs"
HINT_REASON_EDGE    = "Edge play"
HINT_REASON_DEFAULT = "Best calculated move"

def make_status_pass(player_name: str) -> str:
    return player_name + " has no valid moves -- passing"

# -- Player names (status bar, stats, chart) -- derived from active skin ------
PLAYER_1_NAME = _CU.PLAYER_1_COLOR_DESC
PLAYER_2_NAME = _CU.PLAYER_2_COLOR_DESC
PLAYER_HUMAN  = "Human"
PLAYER_AI     = "Machine"

# -- Phase / turn header labels -----------------------------------------------
TURN_HEADER_P1 = PLAYER_1_NAME + "'s turn"
TURN_HEADER_P2 = PLAYER_2_NAME + "'s turn"

# -- Game-over messages -------------------------------------------------------
GAMEOVER_P1_WINS    = PLAYER_1_NAME + " wins!"
GAMEOVER_P2_WINS    = PLAYER_2_NAME + " wins!"
GAMEOVER_HUMAN_WINS = "You win!"
GAMEOVER_AI_WINS    = "Machine wins!"
GAMEOVER_DRAW       = "Draw!"

# -- Autoplay splash ----------------------------------------------------------
AUTOPLAY_SPLASH_THINKING = "Machine is thinking..."

# -- Menu labels --------------------------------------------------------------
MENU_GAME  = "Game"
MENU_NEW   = "New Game"
MENU_SAVE  = "Save Game..."
MENU_LOAD  = "Load Game..."
MENU_QUIT  = "Quit"
MENU_HELP  = "Help"
MENU_RULES = "Rules"
MENU_ABOUT = "About..."

# -- Dialog messages ----------------------------------------------------------
MSG_NO_GAME      = "No game in progress."
MSG_SAVED        = "Game saved to:\n{path}"
MSG_SAVE_ERROR   = "Could not save game:\n{err}"
MSG_LOAD_ERROR   = "Could not load game:\n{err}"
MSG_INVALID_MOVE = "That cell is not a valid move."
SAVE_FILETYPE    = "Reversi saved games (*.json)"

# -- Rules text ---------------------------------------------------------------
RULES_TEXT = (
    getSWName() + "  --  Rules\n\n"
    "Two players alternate placing discs on the board.\n"
    + PLAYER_1_NAME + " moves first. A move must flank at least one\n"
    "opponent disc in any of the 8 directions.\n\n"
    "All flanked opponent discs are flipped to your colour.\n"
    "If you have no valid moves, your turn is skipped.\n"
    "The game ends when neither player can move.\n\n"
    "The player with more discs on the board wins.\n\n"
    "Default board: "
    + str(GRID_SIZE_DEFAULT) + " x " + str(GRID_SIZE_DEFAULT) + "."
)

# -- About dialog -------------------------------------------------------------
ABOUT_TITLE    = "About " + getSWName()
ABOUT_SUBTITLE = getSWName()
ABOUT_BODY     = (
    getSWName() + " v. " + getVersion() + "\n\n"
    "A classic strategy game.\n\n"
    "AI: " + ai_engine.get_name() + "."
)

# -- Stats window -------------------------------------------------------------
STATS_TITLE              = "Game Summary"
STATS_SECTION_RESULT     = "RESULT"
STATS_SECTION_DISCS      = "DISC COUNT"
STATS_SECTION_MOVES      = "MOVES"
STATS_SECTION_FLIPS      = "FLIPS"
STATS_SECTION_TIMING     = "TIMING"

STATS_WINNER_LABEL       = "Winner"
STATS_WINNER_P1          = PLAYER_1_NAME
STATS_WINNER_P2          = PLAYER_2_NAME
STATS_WINNER_HUMAN       = PLAYER_HUMAN
STATS_WINNER_AI          = PLAYER_AI
STATS_WINNER_DRAW        = "Draw"

STATS_ROW_FINAL_DISCS_P1 = PLAYER_1_NAME + " discs (final)"
STATS_ROW_FINAL_DISCS_P2 = PLAYER_2_NAME + " discs (final)"
STATS_ROW_TOTAL_DISCS    = "Total discs on board"

STATS_ROW_MOVES_P1       = PLAYER_1_NAME + " moves"
STATS_ROW_MOVES_P2       = PLAYER_2_NAME + " moves"
STATS_ROW_TOTAL_MOVES    = "Total moves"
STATS_ROW_PASSES_P1      = PLAYER_1_NAME + " passes"
STATS_ROW_PASSES_P2      = PLAYER_2_NAME + " passes"

STATS_ROW_FLIPPED_P1     = "Discs flipped by " + PLAYER_1_NAME
STATS_ROW_FLIPPED_P2     = "Discs flipped by " + PLAYER_2_NAME
STATS_ROW_MAX_FLIP_P1    = PLAYER_1_NAME + " max single flip"
STATS_ROW_MAX_FLIP_P2    = PLAYER_2_NAME + " max single flip"

STATS_ROW_AVG_TIME_P1    = PLAYER_1_NAME + " avg move time"
STATS_ROW_AVG_TIME_P2    = PLAYER_2_NAME + " avg move time"
STATS_DURATION_LABEL     = "Game duration"
STATS_NA                 = "--"

STATS_CHART_P1_LABEL     = PLAYER_1_NAME
STATS_CHART_P2_LABEL     = PLAYER_2_NAME
STATS_CHART_X_LABEL      = "Move #"
STATS_CHART_Y_LABEL      = "Position advantage (" + PLAYER_1_NAME + ")"
STATS_CHART_ZERO_LABEL   = "Equal"

# -- Live panel (in-game side panel) -----------------------------------------
PANEL_TITLE             = "Live Stats"
PANEL_ROW_DISCS         = "Discs"
PANEL_ROW_MOVES         = "Moves"
PANEL_ROW_PASSES        = "Passes"
PANEL_ROW_VALID_MOVES   = "Valid moves"
PANEL_ROW_LAST_FLIP     = "Last flip"
PANEL_VALUE_NA          = "-"
