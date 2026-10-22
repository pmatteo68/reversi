"""Default skin -- classic green Reversi board, black vs white discs."""

SKIN_NAME = "Default"

# -- Window -------------------------------------------------------------------
WINDOW_WIDTH         = 580
WINDOW_HEIGHT        = 640
LAYOUT_INIT_DELAY_MS = 10

# -- General background -------------------------------------------------------
BG_COLOR            = "#e8f0e8"
PANEL_BG            = "#e8f0e8"
PANEL_DIVIDER_COLOR = "#a0b8a0"

# -- Board canvas -------------------------------------------------------------
# CELL_SIZE must be >= DISC_DIAMETER + 2*DISC_MARGIN for consistent spacing.
# At DISC_DIAMETER=52 and DISC_MARGIN=6, CELL_SIZE=64.
CELL_SIZE     = 64
DISC_DIAMETER = 52
DISC_MARGIN   = 6
BOARD_PADDING = 20    # outer margin around the full grid

BOARD_FRAME_COLOR = "#1a6b2a"   # dark green felt
BOARD_FRAME_PAD   = 4           # inner padding of board frame rectangle

CELL_EMPTY_COLOR   = "#2d8a36"  # empty cell (medium green)
CELL_OUTLINE_COLOR = "#145218"  # dark green grid line
CELL_OUTLINE_WIDTH = 2

PLAYER_1_COLOR      = "#1a1a1a"      # Black disc
PLAYER_1_COLOR_DESC = "Black"
PLAYER_2_COLOR      = "#f5f5f5"      # White disc
PLAYER_2_COLOR_DESC = "White"

WIN_FLASH_COLOR_P1 = "#ffd700"  # gold flash for Black winner
WIN_FLASH_COLOR_P2 = "#ffa500"  # orange flash for White winner
HINT_FLASH_COLOR   = "#00e5ff"  # cyan border for hint suggestion

DISC_OUTLINE_WIDTH = 1
DISC_OUTLINE_COLOR = "#555555"

# -- Valid move hints ---------------------------------------------------------
HINT_DOT_RADIUS        = 9     # radius of the hint dot (px)
HINT_DOT_COLOR         = "#7dd484"   # light green dot
HINT_DOT_OUTLINE_COLOR = "#145218"   # dark green outline

# -- Status bar ---------------------------------------------------------------
STATUS_BAR_HEIGHT   = 44
STATUS_BG           = "#c8dcc8"
STATUS_FONT         = ("Helvetica", 12)
STATUS_COLOR        = "#1a3a1a"
STATUS_LABEL_PADX   = 12
STATUS_BTN_PADX     = 4
STATUS_BTN_PADX_END = 8
STATUS_BTN_PADY     = 4
STATUS_BTN_FONT     = ("Helvetica", 9)

# -- Buttons ------------------------------------------------------------------
BTN_BG        = "#1a6b2a"
BTN_FG        = "#ffffff"
BTN_ACTIVE_BG = "#228b36"
BTN_FONT      = ("Helvetica", 11, "bold")
BTN_RELIEF    = "flat"
BTN_PADX      = 14
BTN_PADY      = 6
BTN_BD        = 0
MENU_BD       = 0

# -- Start screen -------------------------------------------------------------
START_TITLE_FONT     = ("Helvetica", 30, "bold")
START_TITLE_COLOR    = "#1a6b2a"
START_SUBTITLE_FONT  = ("Helvetica", 14)
START_SUBTITLE_COLOR = "#3a5a3a"
START_ENGINE_PADY    = 8
START_TITLE_PADY     = 6
START_SUBTITLE_PADY  = 22
START_WHO_FIRST_PADY = 14
START_BTN_PADX       = 8
START_RULES_PADY     = 18
START_BOTTOM_ROW_PADY = 14
START_SECTION_PADY   = 16
START_ENGINE_LABEL_PADY_TOP = 2

LABEL_FONT  = ("Helvetica", 11)
LABEL_COLOR = "#3a5a3a"

# -- Menu colors --------------------------------------------------------------
MENU_FG = "#1a3a1a"

# -- Turn indicator in status bar ---------------------------------------------
TURN_COLOR_P1   = "#1a1a1a"   # Black
TURN_COLOR_P2   = "#777777"   # Gray (for white disc text)
TURN_COLOR_DRAW = "#5a7a5a"

# -- About / Rules dialogs ----------------------------------------------------
ABOUT_WRAP_WIDTH          = 380
ABOUT_PADX                = 24
ABOUT_PADY                = 8
ABOUT_TITLE_PADY_TOP      = 20
ABOUT_DIVIDER_PADX        = 20
ABOUT_HEADER_DIVIDER_PADY = 10
ABOUT_BODY_DIVIDER_PADY   = 6
ABOUT_CLOSE_PADY_TOP      = 10
ABOUT_CLOSE_PADY_BOT      = 20
BOARD_BORDER              = "#a0b8a0"

RULES_WRAP_WIDTH     = 420
RULES_LABEL_PADX     = 24
RULES_LABEL_PADY     = 16
RULES_CLOSE_PADY_BOT = 16

# -- Stats window -------------------------------------------------------------
STATS_WINDOW_WIDTH   = 540
STATS_PADDING        = 18
STATS_TITLE_PADY_BOT = 10
STATS_CLOSE_SPACER_H = 6
STATS_SECTION_BG     = BTN_BG
STATS_SECTION_FG     = BTN_FG
STATS_SECTION_FONT   = ("Helvetica", 10, "bold")
STATS_SECTION_PADY   = 6
STATS_ROW_LABEL_FONT  = ("Helvetica", 11)
STATS_ROW_VALUE_FONT  = ("Helvetica", 11, "bold")
STATS_ROW_LABEL_COLOR = STATUS_COLOR
STATS_ROW_VALUE_COLOR = "#1a6b2a"
STATS_ROW_PADX        = 14
STATS_ROW_PADY        = 2
STATS_DIVIDER_COLOR   = BOARD_BORDER
STATS_TITLE_FONT      = START_TITLE_FONT
STATS_TITLE_COLOR     = START_TITLE_COLOR
STATS_DELAY_MS        = 800

STATS_TABLE_PADY_TOP     = 4
STATS_TABLE_PADY_BOT     = 2
STATS_TABLE_COL_PAD      = 24
STATS_TABLE_DIVIDER_PADY = 3

STATS_SHOW_CHART        = True
STATS_CHART_HEIGHT_IN   = 2.6
STATS_CHART_DPI         = 90
STATS_CHART_BG          = BG_COLOR
STATS_CHART_P1_COLOR    = "#1a1a1a"
STATS_CHART_P2_COLOR    = "#888888"
STATS_CHART_LINE_COLOR  = "#3a5a3a"
STATS_CHART_ZERO_COLOR  = "#a0b8a0"
STATS_CHART_GRID_COLOR  = "#c0d8c0"
STATS_CHART_FILL_ALPHA  = 0.20
STATS_CHART_LINE_WIDTH  = 1.8
STATS_CHART_ZERO_WIDTH  = 1.0
STATS_CHART_FONT_SIZE   = 7
STATS_CHART_LABEL_PAD   = 2
STATS_CHART_TICK_LENGTH = 3
STATS_CHART_TICK_PAD    = 2
STATS_CHART_SPINE_WIDTH = 0.8
STATS_CHART_GRID_WIDTH  = 0.5
STATS_CHART_LAYOUT_PAD  = 0.6

STATS_SECTION_PACK_PADY_TOP = 8
STATS_SECTION_PACK_PADY_BOT = 2
STATS_CLOSE_BTN_PADY_TOP    = 8
STATS_CHART_PACK_PADY_TOP   = 8
