"""BoardCanvas -- Tkinter canvas widget that renders the Reversi board."""

import tkinter as tk
import logging

import config_ui   as UI
import config_game as CG
from game_logic import PLAYER_1, PLAYER_2, EMPTY

log = logging.getLogger(__name__)

_NO_CELL = (-1, -1)    # sentinel: no cell highlighted


class BoardCanvas(tk.Frame):
    """
    Displays the Reversi board grid.

    Layout:
      A square canvas of grid_size x grid_size cells.
      Each cell is CELL_SIZE x CELL_SIZE pixels.
      BOARD_PADDING pixels of margin surround the grid.

    Coordinate system:
      row 0 = top, col 0 = left.

    Public API:
      set_on_cell_click(callback)       -- callback(row, col) on valid click
      set_current_player(player)        -- highlights whose turn it is
      set_enabled(True/False)           -- enable/disable user input
      set_disc(row, col, player)        -- paint disc without animation
      clear_all()                       -- reset all cells to empty
      display_board(board, grid_size)   -- paint full board state at once
      show_hints(moves)                 -- show valid-move dots
      hide_hints()                      -- remove valid-move dots
      animate_place(row, col, player, flipped, on_done)
      flash_win(cells, player, on_done)
    """

    def __init__(self, parent, grid_size: int, **kwargs):
        super().__init__(parent, bg=UI.BG_COLOR, **kwargs)
        self._grid_size      = grid_size
        self._enabled        = True
        self._current_player = PLAYER_1
        self._hover_cell     = _NO_CELL
        self._on_cell_click  = None

        self._cell_ovals  : "dict[tuple, int]" = {}    # (row,col) -> oval id
        self._hint_ovals  : "dict[tuple, int]" = {}    # (row,col) -> hint oval id
        self._canvas      : "tk.Canvas | None" = None

        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_on_cell_click(self, callback) -> None:
        """Register a callback(row, col) fired when the user clicks a valid cell."""
        self._on_cell_click = callback

    def set_current_player(self, player: int) -> None:
        self._current_player = player

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        if not enabled:
            self.hide_hints()

    def set_disc(self, row: int, col: int, player: "int | None") -> None:
        """Paint or clear the disc at (row, col).  player=None clears to empty."""
        oid = self._cell_ovals.get((row, col))
        if oid is None:
            return
        if player == PLAYER_1:
            color = UI.PLAYER_1_COLOR
        elif player == PLAYER_2:
            color = UI.PLAYER_2_COLOR
        else:
            color = UI.CELL_EMPTY_COLOR
        self._canvas.itemconfigure(oid, fill=color)

    def clear_all(self) -> None:
        """Reset every cell to the empty colour."""
        for key in self._cell_ovals:
            self._canvas.itemconfigure(self._cell_ovals[key],
                                       fill=UI.CELL_EMPTY_COLOR)
        self.hide_hints()

    def display_board(self, board: "list[list[int]]", grid_size: int) -> None:
        """Paint the full board state without animation (used after load)."""
        self.clear_all()
        for row in range(grid_size):
            for col in range(grid_size):
                v = board[row][col]
                if v != EMPTY:
                    self.set_disc(row, col, v)

    def show_hints(self, moves: "list[tuple[int,int]]") -> None:
        """Show valid-move hint dots at the given cells."""
        if not CG.SHOW_VALID_MOVE_HINTS:
            return
        self.hide_hints()
        for row, col in moves:
            oid = self._hint_ovals.get((row, col))
            if oid is not None:
                self._canvas.itemconfigure(oid, state="normal")

    def hide_hints(self) -> None:
        """Hide all valid-move hint dots."""
        for oid in self._hint_ovals.values():
            self._canvas.itemconfigure(oid, state="hidden")

    def animate_place(self, row: int, col: int, player: int,
                      flipped: "list[tuple[int,int]]",
                      on_done) -> None:
        """
        Play a pop animation for the new disc, then flip animation for
        flanked discs, then call on_done().
        If PLACE_ANIM_ENABLED is False, skip straight to flip animation.
        """
        self.hide_hints()

        if not CG.PLACE_ANIM_ENABLED:
            self.set_disc(row, col, player)
            self._start_flip_anim(flipped, player, on_done)
            return

        color    = UI.PLAYER_1_COLOR if player == PLAYER_1 else UI.PLAYER_2_COLOR
        cx, cy   = self._cell_center(row, col)
        step_r   = max(1, UI.DISC_DIAMETER // (2 * CG.PLACE_ANIM_STEPS))

        self._anim_oval = self._canvas.create_oval(
            cx - step_r, cy - step_r,
            cx + step_r, cy + step_r,
            fill=color,
            outline=UI.DISC_OUTLINE_COLOR,
            width=UI.DISC_OUTLINE_WIDTH,
            tags="anim_disc",
        )
        log.debug("animate_place row=%d col=%d player=%d flipped=%d",
                  row, col, player, len(flipped))
        self._canvas.after(
            CG.PLACE_ANIM_STEP_MS,
            lambda: self._place_step(row, col, player, flipped,
                                     1, step_r, on_done),
        )

    def flash_hint(self, row: int, col: int, on_done) -> None:
        """
        Draw a thick border rectangle around (row, col) and flash it
        HINT_FLASH_COUNT times, then remove it and call on_done().
        Any previous hint overlay is cancelled first.
        """
        self.cancel_hint()
        s   = UI
        pad = s.BOARD_PADDING
        mg  = s.HINT_BORDER_MARGIN
        bw  = s.HINT_BORDER_WIDTH
        x1  = pad + col * s.CELL_SIZE + mg
        y1  = pad + row * s.CELL_SIZE + mg
        x2  = pad + (col + 1) * s.CELL_SIZE - mg
        y2  = pad + (row + 1) * s.CELL_SIZE - mg
        rect_id = self._canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=s.HINT_FLASH_COLOR,
            width=bw,
            fill="",
            tags="hint_border",
        )
        log.debug("flash_hint row=%d col=%d rect_id=%d", row, col, rect_id)
        self._hint_flash_step(rect_id, CG.HINT_FLASH_COUNT,
                              True, CG.HINT_FLASH_INTERVAL_MS, on_done)

    def cancel_hint(self) -> None:
        """Remove any in-progress hint overlay immediately."""
        self._canvas.delete("hint_border")

    def flash_win(self, cells: "list[tuple[int,int]]",
                  player: int, on_done) -> None:
        """Flash winning cells WIN_FLASH_COUNT times, then call on_done."""
        flash_color = (UI.WIN_FLASH_COLOR_P1 if player == PLAYER_1
                       else UI.WIN_FLASH_COLOR_P2)
        disc_color  = (UI.PLAYER_1_COLOR if player == PLAYER_1
                       else UI.PLAYER_2_COLOR)
        self._flash_step(cells, disc_color, flash_color,
                         CG.WIN_FLASH_COUNT, True, CG.WIN_FLASH_INTERVAL_MS, on_done)

    # ------------------------------------------------------------------
    # Canvas construction
    # ------------------------------------------------------------------

    def _build(self) -> None:
        s     = UI
        gs    = self._grid_size
        size  = gs * s.CELL_SIZE + 2 * s.BOARD_PADDING

        self._canvas = tk.Canvas(
            self,
            width=size, height=size,
            bg=s.BG_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack()

        self._draw_board_frame(size)
        self._draw_cells()
        self._draw_hint_dots()

        self._canvas.bind("<Button-1>", self._on_mouse_click)

    def _draw_board_frame(self, size: int) -> None:
        s   = UI
        pad = s.BOARD_PADDING
        fp  = s.BOARD_FRAME_PAD
        self._canvas.create_rectangle(
            pad - fp, pad - fp,
            size - pad + fp, size - pad + fp,
            fill=s.BOARD_FRAME_COLOR,
            outline="",
        )

    def _draw_cells(self) -> None:
        s  = UI
        r  = s.DISC_DIAMETER // 2
        for row in range(self._grid_size):
            for col in range(self._grid_size):
                cx, cy = self._cell_center(row, col)
                oid = self._canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=s.CELL_EMPTY_COLOR,
                    outline=s.CELL_OUTLINE_COLOR,
                    width=s.CELL_OUTLINE_WIDTH,
                    tags=("cell_" + str(row) + "_" + str(col),),
                )
                self._cell_ovals[(row, col)] = oid

    def _draw_hint_dots(self) -> None:
        s  = UI
        r  = s.HINT_DOT_RADIUS
        for row in range(self._grid_size):
            for col in range(self._grid_size):
                cx, cy = self._cell_center(row, col)
                oid = self._canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=s.HINT_DOT_COLOR,
                    outline=s.HINT_DOT_OUTLINE_COLOR,
                    width=1,
                    state="hidden",
                    tags=("hint_" + str(row) + "_" + str(col),),
                )
                self._hint_ovals[(row, col)] = oid

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _cell_center(self, row: int, col: int) -> "tuple[int, int]":
        s  = UI
        cx = s.BOARD_PADDING + col * s.CELL_SIZE + s.CELL_SIZE // 2
        cy = s.BOARD_PADDING + row * s.CELL_SIZE + s.CELL_SIZE // 2
        return cx, cy

    def _xy_to_cell(self, x: int, y: int) -> "tuple[int, int]":
        """Convert canvas (x, y) to board (row, col). Returns _NO_CELL if out of bounds."""
        s    = UI
        pad  = s.BOARD_PADDING
        size = self._grid_size * s.CELL_SIZE
        if not (pad <= x < pad + size and pad <= y < pad + size):
            return _NO_CELL
        col = (x - pad) // s.CELL_SIZE
        row = (y - pad) // s.CELL_SIZE
        col = max(0, min(self._grid_size - 1, col))
        row = max(0, min(self._grid_size - 1, row))
        return (row, col)

    # ------------------------------------------------------------------
    # Mouse events
    # ------------------------------------------------------------------

    def _on_mouse_click(self, event: tk.Event) -> None:
        if not self._enabled:
            return
        cell = self._xy_to_cell(event.x, event.y)
        if cell == _NO_CELL:
            return
        log.debug("Board click row=%d col=%d", cell[0], cell[1])
        if self._on_cell_click:
            self._on_cell_click(cell[0], cell[1])

    # ------------------------------------------------------------------
    # Placement pop animation
    # ------------------------------------------------------------------

    def _place_step(self, row: int, col: int, player: int,
                    flipped: "list[tuple[int,int]]",
                    step: int, step_r: int, on_done) -> None:
        s  = UI
        cx, cy = self._cell_center(row, col)
        full_r = s.DISC_DIAMETER // 2
        r      = min(step * step_r, full_r)

        self._canvas.coords(
            self._anim_oval,
            cx - r, cy - r, cx + r, cy + r,
        )

        if step >= CG.PLACE_ANIM_STEPS:
            self._canvas.delete("anim_disc")
            self.set_disc(row, col, player)
            self._start_flip_anim(flipped, player, on_done)
            return

        self._canvas.after(
            CG.PLACE_ANIM_STEP_MS,
            lambda: self._place_step(row, col, player, flipped,
                                     step + 1, step_r, on_done),
        )

    # ------------------------------------------------------------------
    # Flip animation
    # ------------------------------------------------------------------

    def _start_flip_anim(self, flipped: "list[tuple[int,int]]",
                         player: int, on_done) -> None:
        if not flipped or not CG.FLIP_ANIM_ENABLED:
            if flipped:
                for fr, fc in flipped:
                    self.set_disc(fr, fc, player)
            on_done()
            return

        opponent_color = (UI.PLAYER_2_COLOR if player == PLAYER_1
                          else UI.PLAYER_1_COLOR)
        player_color   = (UI.PLAYER_1_COLOR if player == PLAYER_1
                          else UI.PLAYER_2_COLOR)

        self._flash_step(flipped, player_color, opponent_color,
                         CG.FLIP_FLASH_COUNT, True, CG.FLIP_FLASH_INTERVAL_MS, on_done)

    # ------------------------------------------------------------------
    # Generic flash step (used by flip animation and win flash)
    #
    # disc_color  -- stable end state color (set permanently when done)
    # flash_color -- alternating highlight color
    # ------------------------------------------------------------------

    def _hint_flash_step(self, rect_id: int, remaining: int,
                         visible: bool, interval_ms: int, on_done) -> None:
        """Toggle the hint border rectangle on/off; delete it when done."""
        if not self._canvas.find_withtag("hint_border"):
            on_done()
            return
        state = "normal" if visible else "hidden"
        self._canvas.itemconfigure(rect_id, state=state)
        if remaining == 0:
            self._canvas.delete("hint_border")
            on_done()
            return
        self._canvas.after(
            interval_ms,
            lambda: self._hint_flash_step(rect_id, remaining - 1,
                                          not visible, interval_ms, on_done),
        )

    def _flash_step(self, cells: "list[tuple[int,int]]",
                    disc_color: str, flash_color: str,
                    remaining: int, flash_on: bool,
                    interval_ms: int, on_done) -> None:
        color = flash_color if flash_on else disc_color
        for row, col in cells:
            oid = self._cell_ovals.get((row, col))
            if oid is not None:
                self._canvas.itemconfigure(oid, fill=color)

        if remaining == 0:
            for row, col in cells:
                oid = self._cell_ovals.get((row, col))
                if oid is not None:
                    self._canvas.itemconfigure(oid, fill=disc_color)
            on_done()
            return

        self._canvas.after(
            interval_ms,
            lambda: self._flash_step(cells, disc_color, flash_color,
                                     remaining - 1, not flash_on,
                                     interval_ms, on_done),
        )
