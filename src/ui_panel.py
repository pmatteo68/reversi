"""LivePanel -- live in-game metrics shown to the right of the board."""

import tkinter as tk
import logging

import config_ui   as UI
import config_text as CT
from game_logic import PLAYER_1, PLAYER_2, count_all_discs, get_valid_moves

log = logging.getLogger(__name__)

_PLAYERS = (PLAYER_1, PLAYER_2)


class LivePanel(tk.Frame):
    """
    Two-column metrics table shown beside the board during a game.
    Column headers are derived from config_text and reflect Human vs AI roles.
    Call update() after every game-state change to refresh values.
    """

    def __init__(self, parent, human_player: "int | None"):
        super().__init__(parent, bg=UI.BG_COLOR)
        self._human_player = human_player
        self._vars: "dict[str, tk.StringVar]" = {}
        self._build()
        log.debug("LivePanel created (human_player=%s)", human_player)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(self,
               board: "list[list[int]]",
               grid_size: int,
               current_player: int,
               move_count_p1: int,
               move_count_p2: int,
               pass_count_p1: int,
               pass_count_p2: int,
               last_flip_p1: int,
               last_flip_p2: int) -> None:
        """Refresh all displayed values from the current game state."""
        counts = count_all_discs(board, grid_size)
        valid  = get_valid_moves(board, current_player, grid_size)

        self._set("discs",  PLAYER_1, str(counts[PLAYER_1]))
        self._set("discs",  PLAYER_2, str(counts[PLAYER_2]))
        self._set("moves",  PLAYER_1, str(move_count_p1))
        self._set("moves",  PLAYER_2, str(move_count_p2))
        self._set("passes", PLAYER_1, str(pass_count_p1))
        self._set("passes", PLAYER_2, str(pass_count_p2))
        self._set("valid",  PLAYER_1,
                  str(len(valid)) if current_player == PLAYER_1 else CT.PANEL_VALUE_NA)
        self._set("valid",  PLAYER_2,
                  str(len(valid)) if current_player == PLAYER_2 else CT.PANEL_VALUE_NA)
        self._set("flip",   PLAYER_1,
                  str(last_flip_p1) if last_flip_p1 > 0 else CT.PANEL_VALUE_NA)
        self._set("flip",   PLAYER_2,
                  str(last_flip_p2) if last_flip_p2 > 0 else CT.PANEL_VALUE_NA)

        log.debug(
            "LivePanel: discs=(%d,%d) moves=(%d,%d) passes=(%d,%d) valid=%d",
            counts[PLAYER_1], counts[PLAYER_2],
            move_count_p1, move_count_p2,
            pass_count_p1, pass_count_p2,
            len(valid),
        )

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def _header_text(self, player: int) -> str:
        hp         = self._human_player
        color_name = CT.PLAYER_1_NAME if player == PLAYER_1 else CT.PLAYER_2_NAME
        if hp == player:
            role = CT.PLAYER_HUMAN
        elif hp is not None:
            role = CT.PLAYER_AI
        else:
            role = None
        return (role + "\n(" + color_name + ")") if role else color_name

    def _build(self) -> None:
        s  = UI
        fr = tk.Frame(self, bg=s.BG_COLOR, padx=s.PANEL_PADX, pady=s.PANEL_PADY)
        fr.pack(fill="both", expand=True, anchor="n")

        # Title
        tk.Label(
            fr, text=CT.PANEL_TITLE,
            font=s.PANEL_TITLE_FONT,
            fg=s.PANEL_TITLE_COLOR,
            bg=s.BG_COLOR,
        ).grid(row=0, column=0, columnspan=3, sticky="ew",
               pady=(0, s.PANEL_TITLE_PADY_BOT))

        # Top divider
        tk.Frame(fr, height=1, bg=s.PANEL_DIVIDER_COLOR).grid(
            row=1, column=0, columnspan=3, sticky="ew",
            pady=(0, s.PANEL_HEADER_PADY_BOT),
        )

        # Column headers: empty label + P1 + P2
        tk.Label(fr, text="", bg=s.BG_COLOR).grid(row=2, column=0, sticky="w")
        for idx, player in enumerate(_PLAYERS):
            col      = idx + 1
            disc_col = UI.PANEL_HDR_COLOR_P1 if player == PLAYER_1 else UI.PANEL_HDR_COLOR_P2
            tk.Label(
                fr, text=self._header_text(player),
                font=s.PANEL_HDR_FONT,
                fg=disc_col,
                bg=s.BG_COLOR,
                justify="center",
                anchor="center",
                width=s.PANEL_VALUE_WIDTH,
            ).grid(row=2, column=col, sticky="ew",
                   padx=(s.PANEL_COL_PADX, 0))

        # Header divider
        tk.Frame(fr, height=1, bg=s.PANEL_DIVIDER_COLOR).grid(
            row=3, column=0, columnspan=3, sticky="ew",
            pady=(s.PANEL_HDR_DIV_PADY, s.PANEL_HDR_DIV_PADY),
        )

        # Metric rows
        _ROWS = [
            (CT.PANEL_ROW_DISCS,       "discs"),
            (CT.PANEL_ROW_MOVES,       "moves"),
            (CT.PANEL_ROW_PASSES,      "passes"),
            (CT.PANEL_ROW_VALID_MOVES, "valid"),
            (CT.PANEL_ROW_LAST_FLIP,   "flip"),
        ]
        for row_idx, (label_text, key) in enumerate(_ROWS):
            base = 4 + row_idx * 2
            tk.Label(
                fr, text=label_text,
                font=s.PANEL_ROW_LABEL_FONT,
                fg=s.PANEL_ROW_LABEL_COLOR,
                bg=s.BG_COLOR,
                anchor="w",
            ).grid(row=base, column=0, sticky="w",
                   pady=(s.PANEL_ROW_PADY, 0))

            for idx, player in enumerate(_PLAYERS):
                col = idx + 1
                var = tk.StringVar(value=CT.PANEL_VALUE_NA)
                self._vars[key + "_" + str(player)] = var
                tk.Label(
                    fr, textvariable=var,
                    font=s.PANEL_ROW_VALUE_FONT,
                    fg=s.PANEL_ROW_VALUE_COLOR,
                    bg=s.BG_COLOR,
                    anchor="center",
                    width=s.PANEL_VALUE_WIDTH,
                ).grid(row=base, column=col, sticky="ew",
                       padx=(s.PANEL_COL_PADX, 0),
                       pady=(s.PANEL_ROW_PADY, 0))

            if row_idx < len(_ROWS) - 1:
                tk.Frame(fr, height=1, bg=s.PANEL_ROW_DIVIDER_COLOR).grid(
                    row=base + 1, column=0, columnspan=3, sticky="ew",
                    pady=(s.PANEL_ROW_DIV_PADY, 0),
                )

    def _set(self, key: str, player: int, value: str) -> None:
        var = self._vars.get(key + "_" + str(player))
        if var is not None:
            var.set(value)
