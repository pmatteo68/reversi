"""
UI skin selector for Reversi.
Set SKIN to any module name from the skins/ directory to switch the active skin.
Use SKIN = "random" to pick a skin at random on each launch.
"""
import importlib
import logging
import random

logger = logging.getLogger(__name__)

SKINS = (
    "default",         # Default         - classic green board, black vs white
    "midnight",        # Midnight        - near-black canvas, neon discs
    "sunset",          # Sunset          - warm amber/coral tones
    "ocean",           # Ocean           - deep navy, teal and cyan
    "forest",          # Forest          - mossy greens, bark browns
    "candy",           # Candy           - pastel bubblegum palette
    "vivid_1",         # Vivid-1         - full-saturation primaries on white
    "vivid_2",         # Vivid-2         - electric cobalt+cyan on pale blue
    "mint_gray",       # Mint-Gray       - cool gray canvas, mint accents
    "black_and_white", # B&W             - pure monochrome grayscale
)

# Active skin -- replace "default" with any name above, or use "random"
SKIN = "default"

try:
    SKIN = random.choice(SKINS) if SKIN == "random" else SKIN
    _skin = importlib.import_module("skins." + SKIN)
except (ImportError, ValueError) as _err:
    logger.error(
        "Skin '%s' could not be loaded (%s) -- falling back to default", SKIN, _err
    )
    from skins import default as _skin


def get_name() -> str:
    return _skin.SKIN_NAME


# Layout constants not defined per-skin; skins may override any of these.
_DEFAULTS = {
    "START_ENGINE_LABEL_PADY_TOP": 2,
    "RULES_WRAP_WIDTH":            420,
    "RULES_LABEL_PADX":            24,
    "RULES_LABEL_PADY":            16,
    "RULES_CLOSE_PADY_BOT":        16,
    "STATS_SECTION_PACK_PADY_TOP": 8,
    "STATS_SECTION_PACK_PADY_BOT": 2,
    "STATS_CLOSE_BTN_PADY_TOP":    8,
    "STATS_CHART_PACK_PADY_TOP":   8,
    "STATS_TABLE_PADY_TOP":        4,
    "STATS_TABLE_PADY_BOT":        2,
    "STATS_TABLE_COL_PAD":         24,
    "STATS_TABLE_DIVIDER_PADY":    3,
    "STATUS_BTN_FONT":             ("Helvetica", 9),
    "MIN_WINDOW_WIDTH":            560,
    # Live panel layout (skins may override any of these)
    "PANEL_PADX":                  14,
    "PANEL_PADY":                  16,
    "PANEL_TITLE_PADY_BOT":        6,
    "PANEL_HEADER_PADY_BOT":       4,
    "PANEL_HDR_DIV_PADY":          4,
    "PANEL_COL_PADX":              14,
    "PANEL_ROW_PADY":              4,
    "PANEL_VALUE_WIDTH":           6,
    "PANEL_ROW_DIV_PADY":          3,
    # Hint border rectangle (drawn around the suggested cell)
    "HINT_BORDER_WIDTH":           3,   # outline width in pixels
    "HINT_BORDER_MARGIN":          4,   # inset from cell edge in pixels
    "PANEL_TITLE_FONT":            ("Helvetica", 12, "bold"),
    "PANEL_HDR_FONT":              ("Helvetica", 10, "bold"),
    "PANEL_ROW_LABEL_FONT":        ("Helvetica", 10),
    "PANEL_ROW_VALUE_FONT":        ("Helvetica", 10, "bold"),
}

# Color defaults derived from the active skin so they adapt automatically.
_COMPUTED_DEFAULTS = {
    "PANEL_TITLE_COLOR":       lambda: _skin.START_TITLE_COLOR,
    "PANEL_ROW_LABEL_COLOR":   lambda: _skin.LABEL_COLOR,
    "PANEL_ROW_VALUE_COLOR":   lambda: _skin.STATS_ROW_VALUE_COLOR,
    "PANEL_ROW_DIVIDER_COLOR": lambda: _skin.PANEL_DIVIDER_COLOR,
    # Panel column-header text colours.
    # P1 uses the disc colour (black is always readable).
    # P2 uses DISC_OUTLINE_COLOR as a readable stand-in: the actual disc colour
    # (near-white) is invisible on light backgrounds.
    "PANEL_HDR_COLOR_P1":      lambda: _skin.PLAYER_1_COLOR,
    "PANEL_HDR_COLOR_P2":      lambda: _skin.DISC_OUTLINE_COLOR,
    # Fallbacks for attributes introduced after the initial skin contract.
    # Custom skins that omit these still work; built-in skins define them
    # explicitly for a tailored appearance.
    "PLAYER_1_COLOR_DESC":     lambda: "Dark",
    "PLAYER_2_COLOR_DESC":     lambda: "Light",
    "HINT_FLASH_COLOR":        lambda: "#ffb300",
}


def __getattr__(name: str):
    try:
        return getattr(_skin, name)
    except AttributeError:
        if name in _DEFAULTS:
            return _DEFAULTS[name]
        if name in _COMPUTED_DEFAULTS:
            return _COMPUTED_DEFAULTS[name]()
        raise
