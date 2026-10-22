"""
Minimax with alpha-beta pruning for Reversi.

The engine plays as `player` (PLAYER_1 or PLAYER_2) and maximises its own
heuristic position score minus the opponent's.

Evaluation combines:
  - Corner captures  (highest priority; stable cells)
  - X-square penalty (cells diagonally adjacent to empty corners)
  - Mobility         (number of legal moves available)
  - Disc parity      (raw disc count advantage)

Move ordering: corners first, then edges, then interior, X-squares last.
"""
import math
import logging
from .base import ReversiAIEngine
from .minimax_alphabeta_config import (
    SEARCH_DEPTH,
    CORNER_WEIGHT,
    X_SQUARE_PENALTY,
    MOBILITY_WEIGHT,
    PARITY_WEIGHT,
    KILLER_MOVE_ENABLED,
)
from game_logic import (
    EMPTY, PLAYER_1, PLAYER_2, OTHER_PLAYER,
    get_valid_moves, apply_move,
)

logger = logging.getLogger(__name__)

_SCORE_WIN = 100000   # terminal win score


def _corners(grid_size: int) -> "list[tuple[int,int]]":
    last = grid_size - 1
    return [(0, 0), (0, last), (last, 0), (last, last)]


def _x_squares(grid_size: int) -> "list[tuple[int,int]]":
    last = grid_size - 1
    return [(1, 1), (1, last - 1), (last - 1, 1), (last - 1, last - 1)]


def _corner_for_x(x_sq: "tuple[int,int]", grid_size: int) -> "tuple[int,int]":
    last = grid_size - 1
    r, c = x_sq
    cr = 0 if r == 1 else last
    cc = 0 if c == 1 else last
    return (cr, cc)


def _cell_priority(row: int, col: int, corners: set, x_set: set,
                   grid_size: int) -> int:
    """Return move ordering priority (lower = try first)."""
    if (row, col) in corners:
        return 0
    if row == 0 or row == grid_size - 1 or col == 0 or col == grid_size - 1:
        if (row, col) not in x_set:
            return 1          # edge (not X-square)
        return 3              # edge X-square (not actually in x_set but near corner)
    if (row, col) in x_set:
        return 3              # interior X-square
    return 2                  # interior


def _order_moves(moves: "list[tuple[int,int]]",
                 board: "list[list[int]]",
                 player: int,
                 opponent: int,
                 grid_size: int) -> "list[tuple[int,int]]":
    """Order moves: corners > edges > interior > X-squares."""
    if not KILLER_MOVE_ENABLED:
        return moves

    corners = set(_corners(grid_size))
    x_squares = set(_x_squares(grid_size))

    def key(move):
        xp = 0
        if move in x_squares:
            cr_cc = _corner_for_x(move, grid_size)
            if board[cr_cc[0]][cr_cc[1]] == EMPTY:
                xp = 1          # penalise X-square only when corner is still empty
        base = _cell_priority(move[0], move[1], corners, x_squares, grid_size)
        return base + xp

    return sorted(moves, key=key)


def _evaluate(board: "list[list[int]]",
              player: int,
              opponent: int,
              grid_size: int) -> int:
    """Heuristic evaluation for `player` on the current board."""
    # -- Disc parity ----------------------------------------------------------
    p_discs = 0
    o_discs = 0
    for r in range(grid_size):
        for c in range(grid_size):
            v = board[r][c]
            if v == player:
                p_discs += 1
            elif v == opponent:
                o_discs += 1
    total_d  = p_discs + o_discs
    disc_score = ((100 * (p_discs - o_discs)) // total_d) if total_d > 0 else 0

    # -- Mobility -------------------------------------------------------------
    p_moves = len(get_valid_moves(board, player,   grid_size))
    o_moves = len(get_valid_moves(board, opponent, grid_size))
    total_m = p_moves + o_moves
    mob_score = ((100 * (p_moves - o_moves)) // total_m) if total_m > 0 else 0

    # -- Corner occupancy -----------------------------------------------------
    last    = grid_size - 1
    corners = [(0, 0), (0, last), (last, 0), (last, last)]
    p_corners = sum(1 for r, c in corners if board[r][c] == player)
    o_corners = sum(1 for r, c in corners if board[r][c] == opponent)
    corner_score = (p_corners - o_corners) * CORNER_WEIGHT

    # -- X-square penalty (only when the adjacent corner is still empty) ------
    x_squares_list = _x_squares(grid_size)
    x_pen = 0
    for xr, xc in x_squares_list:
        if xr < grid_size and xc < grid_size:
            cr, cc = _corner_for_x((xr, xc), grid_size)
            if board[cr][cc] == EMPTY:
                if board[xr][xc] == player:
                    x_pen -= X_SQUARE_PENALTY
                elif board[xr][xc] == opponent:
                    x_pen += X_SQUARE_PENALTY

    return (disc_score * PARITY_WEIGHT
            + mob_score * MOBILITY_WEIGHT
            + corner_score
            + x_pen)


def _minimax(board: "list[list[int]]",
             depth: int,
             alpha: float,
             beta: float,
             maximizing: bool,
             player: int,
             opponent: int,
             grid_size: int) -> int:

    p_moves = get_valid_moves(board, player,   grid_size)
    o_moves = get_valid_moves(board, opponent, grid_size)

    # Terminal: neither can move
    if not p_moves and not o_moves:
        p_discs = sum(1 for r in range(grid_size) for c in range(grid_size)
                      if board[r][c] == player)
        o_discs = sum(1 for r in range(grid_size) for c in range(grid_size)
                      if board[r][c] == opponent)
        if p_discs > o_discs:
            return _SCORE_WIN + depth
        if o_discs > p_discs:
            return -(_SCORE_WIN + depth)
        return 0

    if depth == 0:
        return _evaluate(board, player, opponent, grid_size)

    if maximizing:
        if not p_moves:
            # Player must pass -- switch turn without making a move
            return _minimax(board, depth - 1, alpha, beta, False,
                            player, opponent, grid_size)
        ordered = _order_moves(p_moves, board, player, opponent, grid_size)
        value   = -math.inf
        for row, col in ordered:
            new_board, _ = apply_move(board, row, col, player, grid_size)
            child = _minimax(new_board, depth - 1, alpha, beta, False,
                             player, opponent, grid_size)
            if child > value:
                value = child
            if value > alpha:
                alpha = value
            if alpha >= beta:
                break
        return value
    else:
        if not o_moves:
            # Opponent must pass
            return _minimax(board, depth - 1, alpha, beta, True,
                            player, opponent, grid_size)
        ordered = _order_moves(o_moves, board, opponent, player, grid_size)
        value   = math.inf
        for row, col in ordered:
            new_board, _ = apply_move(board, row, col, opponent, grid_size)
            child = _minimax(new_board, depth - 1, alpha, beta, True,
                             player, opponent, grid_size)
            if child < value:
                value = child
            if value < beta:
                beta = value
            if alpha >= beta:
                break
        return value


class MinimaxAlphaBetaEngine(ReversiAIEngine):

    def get_name(self) -> str:
        return "Minimax Alpha-Beta (depth " + str(SEARCH_DEPTH) + ")"

    def reset(self) -> None:
        logger.debug("MinimaxAlphaBetaEngine reset")

    def _compute_next_move(self,
                           board: "list[list[int]]",
                           player: int,
                           grid_size: int) -> "tuple[int, int]":
        opponent = OTHER_PLAYER[player]
        valid    = get_valid_moves(board, player, grid_size)
        if not valid:
            return (0, 0)

        ordered    = _order_moves(valid, board, player, opponent, grid_size)
        best_move  = ordered[0]
        best_score = -math.inf

        for row, col in ordered:
            new_board, _ = apply_move(board, row, col, player, grid_size)
            score = _minimax(new_board, SEARCH_DEPTH - 1, -math.inf, math.inf,
                             False, player, opponent, grid_size)
            logger.debug("AI move=(%d,%d) score=%d", row, col, score)
            if score > best_score:
                best_score = score
                best_move  = (row, col)

        logger.debug("AI chose (%d,%d) (score=%d)", best_move[0], best_move[1], best_score)
        return best_move


def create() -> MinimaxAlphaBetaEngine:
    return MinimaxAlphaBetaEngine()
