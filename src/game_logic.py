"""
Core Reversi game logic. No UI imports.

Board layout:
  board[row][col]  -- row 0 = top, col 0 = left.
  Values: EMPTY=0, PLAYER_1=1 (Black), PLAYER_2=2 (White).

Initial position (8x8 example; centre 2x2):
  (3,3)=White  (3,4)=Black
  (4,3)=Black  (4,4)=White

For any even grid_size N:
  (N//2-1, N//2-1)=White  (N//2-1, N//2)=Black
  (N//2,   N//2-1)=Black  (N//2,   N//2)=White

Phases:
  PHASE_PLAYER1_TURN -- Player 1 (Black) must move or pass
  PHASE_PLAYER2_TURN -- Player 2 (White) must move or pass
  PHASE_DONE         -- neither player can move; game over

Passing:
  If the current player has no valid moves they must pass.
  If both players pass consecutively, the game ends.
  The App calls do_pass() when get_valid_moves() returns an empty list.
"""
import logging
from config_game import (
    GRID_SIZE_DEFAULT,
    NUM_PLAYERS,
    NUM_INITIAL_DISCS_PER_PLAYER,
    INITIAL_BOARD_STATE,
)

logger = logging.getLogger(__name__)

EMPTY    = 0
PLAYER_1 = 1   # Black
PLAYER_2 = 2   # White

OTHER_PLAYER = {PLAYER_1: PLAYER_2, PLAYER_2: PLAYER_1}

PHASE_PLAYER1_TURN = "player1_turn"
PHASE_PLAYER2_TURN = "player2_turn"
PHASE_DONE         = "done"

# All 8 directions used in Reversi flanking checks
DIRECTIONS = (
    (-1, -1), (-1, 0), (-1, 1),
    ( 0, -1),          ( 0, 1),
    ( 1, -1), ( 1, 0), ( 1, 1),
)

NUM_DIRECTIONS = len(DIRECTIONS)


# ---------------------------------------------------------------------------
# Board construction
# ---------------------------------------------------------------------------

def make_board(grid_size: int) -> "list[list[int]]":
    """Create a board populated according to INITIAL_BOARD_STATE."""
    board = [[EMPTY] * grid_size for _ in range(grid_size)]
    state = INITIAL_BOARD_STATE

    if state == "standard":
        mid = grid_size // NUM_INITIAL_DISCS_PER_PLAYER
        board[mid - 1][mid - 1] = PLAYER_2
        board[mid - 1][mid    ] = PLAYER_1
        board[mid    ][mid - 1] = PLAYER_1
        board[mid    ][mid    ] = PLAYER_2
    elif state == "empty":
        pass
    else:
        for entry in state:
            r, c, p = int(entry[0]), int(entry[1]), int(entry[2])
            if 0 <= r < grid_size and 0 <= c < grid_size:
                board[r][c] = p
            else:
                logger.debug(
                    "INITIAL_BOARD_STATE: skipping (%d,%d,%d) -- outside %dx%d grid",
                    r, c, p, grid_size, grid_size,
                )

    return board


# ---------------------------------------------------------------------------
# Move calculation
# ---------------------------------------------------------------------------

def get_flipped_cells(board: "list[list[int]]",
                      row: int, col: int,
                      player: int,
                      grid_size: int) -> "list[tuple[int,int]]":
    """
    Return the cells that would be flipped if player places at (row, col).
    Returns an empty list if the move is invalid (cell occupied or no flanks).
    """
    if board[row][col] != EMPTY:
        return []

    opponent = OTHER_PLAYER[player]
    flipped  = []

    for dr, dc in DIRECTIONS:
        r, c = row + dr, col + dc
        line = []
        while 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == opponent:
            line.append((r, c))
            r += dr
            c += dc
        if line and 0 <= r < grid_size and 0 <= c < grid_size and board[r][c] == player:
            flipped.extend(line)

    return flipped


def get_valid_moves(board: "list[list[int]]",
                    player: int,
                    grid_size: int) -> "list[tuple[int,int]]":
    """Return all valid (row, col) placements for player on the current board."""
    moves = []
    for row in range(grid_size):
        for col in range(grid_size):
            if get_flipped_cells(board, row, col, player, grid_size):
                moves.append((row, col))
    return moves


def apply_move(board: "list[list[int]]",
               row: int, col: int,
               player: int,
               grid_size: int) -> "tuple[list[list[int]], list[tuple[int,int]]]":
    """
    Place player's disc at (row, col) and flip all flanked discs.
    Returns (new_board, flipped_cells).
    Does NOT mutate the original board.
    Raises ValueError if the move produces no flips (invalid).
    """
    flipped = get_flipped_cells(board, row, col, player, grid_size)
    if not flipped:
        raise ValueError(
            "No flips for player {} at ({}, {})".format(player, row, col)
        )

    new_board = [r[:] for r in board]
    new_board[row][col] = player
    for fr, fc in flipped:
        new_board[fr][fc] = player

    return new_board, flipped


# ---------------------------------------------------------------------------
# Counting and evaluation
# ---------------------------------------------------------------------------

def count_discs(board: "list[list[int]]",
                player: int,
                grid_size: int) -> int:
    """Return the number of discs belonging to player."""
    total = 0
    for row in range(grid_size):
        for col in range(grid_size):
            if board[row][col] == player:
                total += 1
    return total


def count_all_discs(board: "list[list[int]]",
                    grid_size: int) -> "dict[int, int]":
    """Return {PLAYER_1: n, PLAYER_2: n} disc counts."""
    counts = {PLAYER_1: 0, PLAYER_2: 0}
    for row in range(grid_size):
        for col in range(grid_size):
            v = board[row][col]
            if v in counts:
                counts[v] += 1
    return counts


def evaluate_position(board: "list[list[int]]",
                      player: int,
                      grid_size: int) -> int:
    """
    Heuristic position score from player's perspective (used by game_stats
    to build the advantage trajectory chart).
    Positive = good for player.  Combines disc parity, mobility, and corners.
    """
    opponent = OTHER_PLAYER[player]

    p_discs  = count_discs(board, player,   grid_size)
    o_discs  = count_discs(board, opponent, grid_size)
    total_d  = p_discs + o_discs

    disc_score = (100 * (p_discs - o_discs) // total_d) if total_d else 0

    p_moves  = len(get_valid_moves(board, player,   grid_size))
    o_moves  = len(get_valid_moves(board, opponent, grid_size))
    total_m  = p_moves + o_moves
    mob_score = (100 * (p_moves - o_moves) // total_m) if total_m else 0

    last = grid_size - 1
    corner_delta = 0
    for r, c in ((0, 0), (0, last), (last, 0), (last, last)):
        if board[r][c] == player:
            corner_delta += 1
        elif board[r][c] == opponent:
            corner_delta -= 1
    corner_score = corner_delta * 25

    return disc_score + mob_score + corner_score


# ---------------------------------------------------------------------------
# GameState
# ---------------------------------------------------------------------------

class GameState:
    """Full mutable Reversi game state."""

    def __init__(self,
                 first_player: int,
                 grid_size: int = GRID_SIZE_DEFAULT):
        self.grid_size      = grid_size
        self.board          = make_board(grid_size)
        self.current_player = first_player
        self.phase          = (PHASE_PLAYER1_TURN if first_player == PLAYER_1
                               else PHASE_PLAYER2_TURN)
        self.winner         : "int | None" = None
        self.game_over      = False
        self.move_history   : "list[tuple[int, int, int]]" = []
        # (player, row, col); row/col == -1 for a pass move.
        self._pass_count    = 0   # consecutive pass count; >= NUM_PLAYERS => game over

        logger.debug(
            "GameState init: grid_size=%d first_player=%d",
            grid_size, first_player,
        )

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_valid_moves(self) -> "list[tuple[int,int]]":
        return get_valid_moves(self.board, self.current_player, self.grid_size)

    def disc_counts(self) -> "dict[int, int]":
        return count_all_discs(self.board, self.grid_size)

    # ------------------------------------------------------------------
    # Mutators
    # ------------------------------------------------------------------

    def place_disc(self, row: int, col: int) -> "list[tuple[int,int]]":
        """
        Place the current player's disc at (row, col).
        Returns the list of flipped cells.
        Raises ValueError if the move is invalid.
        Switches current_player after the move.
        """
        player    = self.current_player
        new_board, flipped = apply_move(
            self.board, row, col, player, self.grid_size
        )
        self.board      = new_board
        self._pass_count = 0
        self.move_history.append((player, row, col))

        logger.debug(
            "Player %d placed at (%d,%d), flipped %d cells",
            player, row, col, len(flipped),
        )

        next_player = OTHER_PLAYER[player]
        self.current_player = next_player
        self.phase = (PHASE_PLAYER1_TURN if next_player == PLAYER_1
                      else PHASE_PLAYER2_TURN)
        return flipped

    def do_pass(self) -> None:
        """
        Called when the current player has no valid moves.
        If both players pass consecutively (pass_count reaches NUM_PLAYERS),
        the game ends and the winner is determined by disc count.
        """
        player = self.current_player
        self.move_history.append((player, -1, -1))
        self._pass_count += 1

        logger.debug(
            "Player %d passes (pass_count=%d)", player, self._pass_count
        )

        if self._pass_count >= NUM_PLAYERS:
            self._end_game()
        else:
            next_player = OTHER_PLAYER[player]
            self.current_player = next_player
            self.phase = (PHASE_PLAYER1_TURN if next_player == PLAYER_1
                          else PHASE_PLAYER2_TURN)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _end_game(self) -> None:
        counts = count_all_discs(self.board, self.grid_size)
        p1     = counts[PLAYER_1]
        p2     = counts[PLAYER_2]

        if p1 > p2:
            self.winner = PLAYER_1
        elif p2 > p1:
            self.winner = PLAYER_2
        else:
            self.winner = None   # draw

        self.game_over = True
        self.phase     = PHASE_DONE

        logger.debug(
            "Game ended: P1_discs=%d P2_discs=%d winner=%s",
            p1, p2, self.winner,
        )
