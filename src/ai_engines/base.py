"""Abstract base class for all Reversi AI engine plugins."""
import logging
from abc import ABC, abstractmethod
from game_logic import get_valid_moves

logger = logging.getLogger(__name__)


class ReversiAIEngine(ABC):
    """
    Plugin interface for Reversi AI engines.

    Implement _compute_next_move() in your subclass and add a module-level
    factory function create().  The public next_move() wrapper validates the
    result and falls back gracefully so the game can always continue.

    Implementing a custom AI engine
    --------------------------------
    1. Create a new file under src/ai_engines/, e.g. my_engine.py.
    2. Import and subclass ReversiAIEngine from .base.
    3. Implement the three abstract methods:
         get_name()             -- short identifier (shown on start screen)
         _compute_next_move()   -- return (row, col) for best move
         reset()                -- clear internal state for a new game
    4. Add a module-level factory:
         def create() -> ReversiAIEngine:
             return MyEngine()
    5. Set AI_ENGINE = "my_engine" in config_game.py.

    Contract for _compute_next_move
    --------------------------------
    board[row][col]: 0=empty, 1=Player1(Black), 2=Player2(White)
    player: PLAYER_1 or PLAYER_2
    grid_size: board dimension (e.g. 8 for an 8x8 board)

    Must return (row, col) that produces at least one flip.
    next_move() validates this and substitutes the first valid move
    from get_valid_moves() if the engine returns an invalid cell.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Short identifier shown on the start screen and in logs."""

    def next_move(self,
                  board: "list[list[int]]",
                  player: int,
                  grid_size: int) -> "tuple[int, int]":
        """
        Public entry point -- do NOT override in subclasses.

        Validates the (row, col) returned by _compute_next_move() and
        substitutes the first valid move from get_valid_moves() if the
        engine returns an invalid cell.

        board     : board[row][col], 0=empty/1=P1/2=P2
        player    : PLAYER_1 or PLAYER_2
        grid_size : board dimension

        Returns   : (row, col) guaranteed to be a valid move
        """
        valid = get_valid_moves(board, player, grid_size)
        if not valid:
            logger.error(
                "next_move called with no valid moves for player %d -- "
                "this should not happen; returning (0,0)",
                player,
            )
            return (0, 0)

        move = self._compute_next_move(board, player, grid_size)

        if move in valid:
            return move

        logger.warning(
            "%s._compute_next_move returned invalid move %s for player %d "
            "-- substituting first valid move %s",
            self.__class__.__name__, move, player, valid[0],
        )
        return valid[0]

    @abstractmethod
    def _compute_next_move(self,
                           board: "list[list[int]]",
                           player: int,
                           grid_size: int) -> "tuple[int, int]":
        """
        Implement the move-selection algorithm here.

        Must return (row, col) that is present in get_valid_moves(board, player, grid_size).
        next_move() verifies this and auto-corrects silently if violated.

        board[row][col] -- 0=empty, 1=player1(Black), 2=player2(White)
        """

    @abstractmethod
    def reset(self) -> None:
        """Reset any internal state for a fresh game."""
