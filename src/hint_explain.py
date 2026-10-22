"""Post-hoc reason generator for AI hint suggestions."""

import logging
from game_logic import get_flipped_cells
import config_game as CG
import config_text as CT

logger = logging.getLogger(__name__)

NUM_CORNERS = 4  # structural: Reversi has exactly 4 corner cells


def explain_hint(board: "list[list[int]]",
                 row: int, col: int,
                 player: int,
                 grid_size: int) -> str:
    """
    Return a short human-readable reason for suggesting (row, col).
    Checks properties in priority order:
      1. Corner capture
      2. High flip count (>= HINT_FLIP_MENTION_MIN)
      3. Edge position
      4. Default fallback
    """
    last = grid_size - 1

    if (row == 0 or row == last) and (col == 0 or col == last):
        logger.debug("Hint reason: corner at (%d,%d)", row, col)
        return CT.HINT_REASON_CORNER

    flip_count = len(get_flipped_cells(board, row, col, player, grid_size))

    if flip_count >= CG.HINT_FLIP_MENTION_MIN:
        logger.debug("Hint reason: flips %d at (%d,%d)", flip_count, row, col)
        return CT.HINT_REASON_FLIPS.format(n=flip_count)

    if row == 0 or row == last or col == 0 or col == last:
        logger.debug("Hint reason: edge at (%d,%d)", row, col)
        return CT.HINT_REASON_EDGE

    logger.debug("Hint reason: default at (%d,%d)", row, col)
    return CT.HINT_REASON_DEFAULT
