"""In-game statistics collector for Reversi."""
import time
import logging
from game_logic import PLAYER_1, PLAYER_2, evaluate_position, count_all_discs
import config_text as CT

logger = logging.getLogger(__name__)


class GameStats:

    def __init__(self):
        self._start_time     = time.monotonic()
        self._game_duration  = None

        self.winner            = None         # PLAYER_1 | PLAYER_2 | None (draw)
        self.game_over_reason  = None         # "win" | "draw"
        self.human_player      = None         # PLAYER_1 | PLAYER_2 | None (autoplay)

        self._move_times    : "list[float]" = []   # wall time per move (passes excluded)
        self._move_players  : "list[int]"   = []   # player per move (passes excluded)
        self._move_rows     : "list[int]"   = []   # row per move
        self._move_cols     : "list[int]"   = []   # col per move
        self._flip_counts   : "list[int]"   = []   # discs flipped per move
        self._pos_scores    : "list[int]"   = []   # position score after each move (P1 view)
        self._disc_history  : "list[tuple[int,int]]" = []  # (p1_count, p2_count) after each move
        self._pass_counts   = {PLAYER_1: 0, PLAYER_2: 0}

        self._total_moves    = 0
        self._last_move_ts   = time.monotonic()

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_move(self, player: int, row: int, col: int,
                    flipped_count: int,
                    board, grid_size: int) -> None:
        now     = time.monotonic()
        elapsed = now - self._last_move_ts
        self._last_move_ts = now

        self._move_players.append(player)
        self._move_rows.append(row)
        self._move_cols.append(col)
        self._move_times.append(elapsed)
        self._flip_counts.append(flipped_count)
        self._total_moves += 1

        score   = evaluate_position(board, PLAYER_1, grid_size)
        self._pos_scores.append(score)

        counts  = count_all_discs(board, grid_size)
        self._disc_history.append((counts[PLAYER_1], counts[PLAYER_2]))

        logger.debug(
            "Stats: move #%d player=%d (%d,%d) flipped=%d elapsed=%.2fs score=%d",
            self._total_moves, player, row, col, flipped_count, elapsed, score,
        )

    def seed_from_history(self, move_history: "list[tuple[int,int,int]]") -> None:
        """
        Pre-populate move and pass counts from a loaded game's move_history.
        Each entry is (player, row, col); passes are encoded as (player, -1, -1).
        Timing, flip, and score data are not available for historical moves and
        remain at zero for those entries.
        """
        PASS_SENTINEL = -1
        for entry in move_history:
            player, row, col = int(entry[0]), int(entry[1]), int(entry[2])
            if row == PASS_SENTINEL:
                self._pass_counts[player] = self._pass_counts.get(player, 0) + 1
            else:
                self._move_players.append(player)
                self._move_rows.append(row)
                self._move_cols.append(col)
                self._move_times.append(0.0)
                self._flip_counts.append(0)
                self._pos_scores.append(0)
                self._disc_history.append((0, 0))
                self._total_moves += 1
        logger.debug(
            "Stats seeded from history: total_moves=%d passes_p1=%d passes_p2=%d",
            self._total_moves,
            self._pass_counts.get(PLAYER_1, 0),
            self._pass_counts.get(PLAYER_2, 0),
        )

    def record_pass(self, player: int) -> None:
        self._pass_counts[player] = self._pass_counts.get(player, 0) + 1
        logger.debug("Stats: player %d passes (total passes=%d)", player,
                     self._pass_counts[player])

    def finalise(self, winner: "int | None", game_over_reason: str,
                 human_player: "int | None") -> None:
        self._game_duration   = time.monotonic() - self._start_time
        self.winner           = winner
        self.game_over_reason = game_over_reason
        self.human_player     = human_player
        self._log_summary()

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def game_duration(self) -> float:
        return self._game_duration or 0.0

    @property
    def total_moves(self) -> int:
        return self._total_moves

    @property
    def player1_moves(self) -> int:
        return sum(1 for p in self._move_players if p == PLAYER_1)

    @property
    def player2_moves(self) -> int:
        return sum(1 for p in self._move_players if p == PLAYER_2)

    def player_move_count(self, player: int) -> int:
        return sum(1 for p in self._move_players if p == player)

    def player_pass_count(self, player: int) -> int:
        return self._pass_counts.get(player, 0)

    def avg_move_time(self, player: int) -> float:
        times = [t for p, t in zip(self._move_players, self._move_times)
                 if p == player]
        return sum(times) / len(times) if times else 0.0

    def total_flipped(self, player: int) -> int:
        return sum(f for p, f in zip(self._move_players, self._flip_counts)
                   if p == player)

    def max_single_flip(self, player: int) -> int:
        flips = [f for p, f in zip(self._move_players, self._flip_counts)
                 if p == player]
        return max(flips) if flips else 0

    @property
    def position_score_trajectory(self) -> "list[int]":
        """Position score from Player 1 perspective after each disc placement."""
        return list(self._pos_scores)

    @property
    def disc_trajectory(self) -> "list[tuple[int,int]]":
        """(p1_count, p2_count) after each disc placement."""
        return list(self._disc_history)

    def winning_move_number(self) -> "int | None":
        if self.game_over_reason == "win" and self._total_moves > 0:
            return self._total_moves
        return None

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    def _log_summary(self) -> None:
        dur     = self.game_duration
        m, s    = divmod(int(dur), 60)
        dur_str = str(m) + "m" + str(s).zfill(2) + "s" if m else str(s) + "s"

        if self.winner == PLAYER_1:
            w_str = "Player 1 (" + CT.PLAYER_1_NAME + ")"
        elif self.winner == PLAYER_2:
            w_str = "Player 2 (" + CT.PLAYER_2_NAME + ")"
        else:
            w_str = "Draw"

        p1_flipped = self.total_flipped(PLAYER_1)
        p2_flipped = self.total_flipped(PLAYER_2)

        logger.info("=== GAME SUMMARY ===")
        logger.info(
            "[OUTCOME] result=%s reason=%s duration=%s",
            w_str, self.game_over_reason, dur_str,
        )
        logger.info(
            "[MOVES] total=%d p1=%d p2=%d  p1_passes=%d p2_passes=%d",
            self._total_moves, self.player1_moves, self.player2_moves,
            self.player_pass_count(PLAYER_1), self.player_pass_count(PLAYER_2),
        )
        logger.info(
            "[FLIPS] p1_total=%d p1_max=%d  p2_total=%d p2_max=%d",
            p1_flipped, self.max_single_flip(PLAYER_1),
            p2_flipped, self.max_single_flip(PLAYER_2),
        )
        logger.info(
            "[TIMING] avg_p1=%.2fs avg_p2=%.2fs",
            self.avg_move_time(PLAYER_1),
            self.avg_move_time(PLAYER_2),
        )
        if self._disc_history:
            last = self._disc_history[-1]
            logger.info("[FINAL_DISCS] p1=%d p2=%d", last[0], last[1])
