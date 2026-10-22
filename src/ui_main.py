"""Main application window and controller for Reversi."""

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import logging

import config_game   as CG
import config_text   as CT
import config_ui     as UI
import ai_engine     as AE
from game_logic       import (GameState, PLAYER_1, PLAYER_2,
                               PHASE_PLAYER1_TURN, PHASE_PLAYER2_TURN, PHASE_DONE,
                               get_valid_moves)
from game_persistence import save_game, load_game
from game_stats       import GameStats
from hint_explain     import explain_hint
from ui_board         import BoardCanvas
from ui_panel         import LivePanel
from ui_stats         import StatsWindow

log = logging.getLogger(__name__)

_FIRST_HUMAN = "human"
_FIRST_AI    = "ai"


# ---------------------------------------------------------------------------
# Start screen
# ---------------------------------------------------------------------------

class StartScreen(tk.Frame):
    """
    Initial screen shown at launch and after New Game.
    Offers a board-size dropdown, who-goes-first selector, and four buttons:
    Start, Load, Auto Play, Quit.
    """

    def __init__(self, parent, on_start, on_load, on_quit, on_autoplay):
        """
        on_start(grid_size, first_player)  -- first_player is "human" or "ai"
        on_load()                          -- triggers open-file dialog in App
        on_quit()                          -- exits the application
        on_autoplay(grid_size)             -- starts a fully automated game
        """
        super().__init__(parent, bg=UI.BG_COLOR)
        self._on_start       = on_start
        self._on_load        = on_load
        self._on_quit        = on_quit
        self._on_autoplay_cb = on_autoplay
        self._build()

    def _build(self) -> None:
        s = UI

        tk.Label(self, text=CT.START_TITLE,
                 font=s.START_TITLE_FONT, fg=s.START_TITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_TITLE_PADY, 0))

        tk.Label(self, text=CT.START_SUBTITLE,
                 font=s.START_SUBTITLE_FONT, fg=s.START_SUBTITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_SUBTITLE_PADY, 0))

        tk.Label(self,
                 text=CT.START_ENGINE_LABEL + "  " + AE.get_name(),
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_ENGINE_PADY, 0))

        # Board-size dropdown
        grid_frame = tk.Frame(self, bg=s.BG_COLOR)
        grid_frame.pack(pady=(s.START_SECTION_PADY, 0))

        grid_values = [
            str(v) for v in range(CG.GRID_SIZE_MIN,
                                   CG.GRID_SIZE_MAX + 1,
                                   CG.GRID_SIZE_STEP)
        ]
        self._grid_var = tk.StringVar(value=str(CG.GRID_SIZE_DEFAULT))

        tk.Label(grid_frame, text=CT.START_GRID_LABEL,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 anchor="e",
                 ).grid(row=0, column=0, sticky="e", padx=(0, 8), pady=3)

        om = tk.OptionMenu(grid_frame, self._grid_var, *grid_values)
        om.config(
            bg=s.BTN_BG, fg=s.BTN_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            highlightthickness=0, font=s.BTN_FONT,
            relief=s.BTN_RELIEF, bd=s.MENU_BD, width=5,
        )
        om["menu"].config(
            bg=s.BTN_BG, fg=s.BTN_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
        )
        om.grid(row=0, column=1, sticky="w", pady=3)
        self._grid_var.trace_add("write", lambda *_: self._update_hint())

        # Who goes first
        tk.Label(self, text=CT.START_WHO_FIRST,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_WHO_FIRST_PADY, 0))

        radio_frame = tk.Frame(self, bg=s.BG_COLOR)
        radio_frame.pack()

        self._first_var = tk.StringVar(
            value=_FIRST_HUMAN if CG.DEFAULT_FIRST_PLAYER == _FIRST_HUMAN else _FIRST_AI
        )
        for value, text in ((_FIRST_HUMAN, CT.START_FIRST_HUMAN),
                             (_FIRST_AI,    CT.START_FIRST_AI)):
            tk.Radiobutton(
                radio_frame, text=text,
                variable=self._first_var, value=value,
                font=s.BTN_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                activebackground=s.BG_COLOR, selectcolor=s.BG_COLOR,
                indicatoron=True,
            ).pack(side="left", padx=s.START_BTN_PADX)

        # Rules hint (auto-updated)
        self._hint_var = tk.StringVar()
        tk.Label(self, textvariable=self._hint_var,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.START_RULES_PADY, 0))
        self._update_hint()

        # Buttons
        for label, cmd in (
            (CT.BTN_START,    self._on_start_clicked),
            (CT.BTN_LOAD_GAME, self._on_load),
            (CT.BTN_AUTOPLAY, self._on_autoplay_clicked),
            (CT.BTN_QUIT,     self._on_quit),
        ):
            tk.Button(
                self, text=label,
                font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                relief=s.BTN_RELIEF, bd=s.BTN_BD,
                padx=s.BTN_PADX, pady=s.BTN_PADY,
                command=cmd,
            ).pack(pady=(s.START_BOTTOM_ROW_PADY // 2, 0),
                   padx=s.START_BTN_PADX, fill="x", ipadx=10)

    def _update_hint(self) -> None:
        try:
            self._hint_var.set(CT.make_rules_hint(int(self._grid_var.get())))
        except (ValueError, tk.TclError):
            pass

    def _on_start_clicked(self) -> None:
        try:
            self._on_start(int(self._grid_var.get()), self._first_var.get())
        except (ValueError, tk.TclError) as exc:
            log.error("Start screen bad input: %s", exc)

    def _on_autoplay_clicked(self) -> None:
        try:
            self._on_autoplay_cb(int(self._grid_var.get()))
        except (ValueError, tk.TclError) as exc:
            log.error("Auto play bad input: %s", exc)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class App(tk.Tk):
    """
    Top-level Tkinter window. Manages the start screen and game screen,
    drives game phase transitions (including pass handling), and owns
    the AI background thread.
    """

    def __init__(self):
        super().__init__()
        self.title(CT.WINDOW_TITLE)
        self.configure(bg=UI.BG_COLOR)
        self.resizable(False, False)

        # Game state (None when on start screen)
        self._gs           : "GameState | None" = None
        self._human_player : "int | None"       = None
        self._stats        : "GameStats | None" = None

        # Frame pointers
        self._start_frame  : "StartScreen | None" = None
        self._game_frame   : "tk.Frame | None"    = None

        # Board canvas, live panel, and status label (alive only during a game)
        self._board_canvas : "BoardCanvas | None" = None
        self._live_panel   : "LivePanel | None"   = None
        self._status_label : "tk.Label | None"    = None
        self._last_flip    : "dict[int, int]"     = {}

        # Hint AI: independent engine instance used only for Get Hint
        self._hint_ai   : "object | None"    = None
        self._hint_btn  : "tk.Button | None" = None
        self._hint_busy : bool               = False

        # Autoplay: two independent engine instances, one per player
        self._autoplay_engines : "dict[int, object]" = {}
        self._autoplay         = False

        # Generation counter -- incremented per new game to discard stale results
        self._game_id = 0

        self._min_width = 0

        self._build_menu()
        self._show_start()

    # ------------------------------------------------------------------
    # Screen management
    # ------------------------------------------------------------------

    def _show_start(self) -> None:
        log.debug("Navigating to start screen")
        self._min_width = 0
        self._teardown_game()
        if self._start_frame:
            self._start_frame.destroy()
        self._start_frame = StartScreen(
            self,
            self._on_start_normal,
            self._on_load_game,
            self.quit,
            self._on_start_autoplay,
        )
        self._start_frame.pack(fill="both", expand=True,
                               padx=UI.BOARD_PADDING, pady=UI.BOARD_PADDING)
        self.after(UI.LAYOUT_INIT_DELAY_MS, self._fit_window)

    def _show_game(self, state: GameState, human_player: "int | None") -> None:
        log.debug("Navigating to game screen (human_player=%s, autoplay=%s)",
                  human_player, self._autoplay)
        if self._start_frame:
            self._start_frame.pack_forget()
            self._start_frame.destroy()
            self._start_frame = None
        self._teardown_game()

        self._gs           = state
        self._human_player = human_player
        self._stats        = GameStats()
        self._stats.seed_from_history(state.move_history)
        self._game_id     += 1

        if self._autoplay:
            self._autoplay_engines = {
                PLAYER_1: AE.create_fresh_instance(),
                PLAYER_2: AE.create_fresh_instance(),
            }
            log.debug("Autoplay engines created for both players")
            self._hint_ai = None
        else:
            self._autoplay_engines = {}
            AE.reset()
            if human_player is not None:
                self._hint_ai = AE.create_fresh_instance()
                log.debug("Hint AI engine created")
            else:
                self._hint_ai = None

        self._hint_btn  = None
        self._hint_busy = False

        self._min_width  = UI.MIN_WINDOW_WIDTH
        self._game_frame = tk.Frame(self, bg=UI.BG_COLOR)
        self._game_frame.pack(fill="both", expand=True)

        self._build_status_bar(self._game_frame)

        content = tk.Frame(self._game_frame, bg=UI.BG_COLOR)
        content.pack(fill="both", expand=True)

        self._board_canvas = BoardCanvas(content, state.grid_size)
        self._board_canvas.pack(side="left")
        self._board_canvas.set_on_cell_click(self._on_human_cell_click)

        self._live_panel = LivePanel(content, self._human_player)
        self._live_panel.pack(side="left", fill="y")

        self._board_canvas.display_board(state.board, state.grid_size)
        self._update_panel()

        self.after(UI.LAYOUT_INIT_DELAY_MS, self._fit_window)

        if state.game_over:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._on_loaded_game_over)
        else:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._begin_phase)

    def _teardown_game(self) -> None:
        if self._game_frame:
            self._game_frame.destroy()
            self._game_frame   = None
            self._board_canvas = None
            self._live_panel   = None
            self._status_label = None
        self._gs               = None
        self._autoplay_engines = {}
        self._last_flip        = {}
        self._hint_ai          = None
        self._hint_btn         = None
        self._hint_busy        = False

    def _build_status_bar(self, parent: tk.Frame) -> None:
        s   = UI
        bar = tk.Frame(parent, bg=s.STATUS_BG, height=s.STATUS_BAR_HEIGHT)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        # All game buttons share one frame on the right of the status bar.
        # Get Hint (human games only) is the leftmost; management buttons follow.
        btn_frame = tk.Frame(bar, bg=s.STATUS_BG)
        btn_frame.pack(side="right", padx=s.STATUS_BTN_PADX_END,
                       pady=s.STATUS_BTN_PADY)

        if self._hint_ai is not None:
            self._hint_btn = tk.Button(
                btn_frame, text=CT.BTN_GET_HINT,
                font=s.STATUS_BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                relief=s.BTN_RELIEF, bd=s.BTN_BD,
                padx=s.STATUS_BTN_PADX, pady=s.STATUS_BTN_PADY,
                command=self._on_get_hint,
                state="disabled",
            )
            self._hint_btn.pack(side="left", padx=s.STATUS_BTN_PADX // 2)

        for label, cmd in (
            (CT.BTN_NEW_GAME,  self._on_new_game),
            (CT.BTN_SAVE_GAME, self._on_save_game),
            (CT.BTN_LOAD_GAME, self._on_load_game),
            (CT.BTN_QUIT,      self.quit),
        ):
            tk.Button(
                btn_frame, text=label,
                font=s.STATUS_BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                relief=s.BTN_RELIEF, bd=s.BTN_BD,
                padx=s.STATUS_BTN_PADX, pady=s.STATUS_BTN_PADY,
                command=cmd,
            ).pack(side="left", padx=s.STATUS_BTN_PADX // 2)

        self._status_label = tk.Label(
            bar, text="",
            font=s.STATUS_FONT, fg=s.STATUS_COLOR, bg=s.STATUS_BG,
            anchor="w", padx=s.STATUS_LABEL_PADX,
        )
        self._status_label.pack(side="left", fill="x", expand=True)

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        s      = UI
        menubar = tk.Menu(
            self, bg=s.BG_COLOR, fg=s.MENU_FG,
            activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
            bd=s.MENU_BD,
        )

        game_menu = tk.Menu(menubar, tearoff=0, bg=s.BG_COLOR, fg=s.MENU_FG,
                            activebackground=s.BTN_ACTIVE_BG,
                            activeforeground=s.BTN_FG)
        game_menu.add_command(label=CT.MENU_NEW,  command=self._on_new_game)
        game_menu.add_command(label=CT.MENU_SAVE, command=self._on_save_game)
        game_menu.add_command(label=CT.MENU_LOAD, command=self._on_load_game)
        game_menu.add_separator()
        game_menu.add_command(label=CT.MENU_QUIT, command=self.quit)
        menubar.add_cascade(label=CT.MENU_GAME, menu=game_menu)

        help_menu = tk.Menu(menubar, tearoff=0, bg=s.BG_COLOR, fg=s.MENU_FG,
                            activebackground=s.BTN_ACTIVE_BG,
                            activeforeground=s.BTN_FG)
        help_menu.add_command(label=CT.MENU_RULES, command=self._show_rules)
        help_menu.add_command(label=CT.MENU_ABOUT, command=self._show_about)
        menubar.add_cascade(label=CT.MENU_HELP, menu=help_menu)

        self.config(menu=menubar)

    # ------------------------------------------------------------------
    # Phase management
    # ------------------------------------------------------------------

    def _begin_phase(self) -> None:
        if self._gs is None:
            return
        if self._gs.game_over:
            self._on_game_over()
            return

        player = self._gs.current_player
        self._board_canvas.set_current_player(player)
        self._update_panel()

        # Check for valid moves -- if none, the player must pass
        valid = get_valid_moves(self._gs.board, player, self._gs.grid_size)
        if not valid:
            self._handle_pass(player)
            return

        if self._autoplay:
            self._board_canvas.set_enabled(False)
            self._board_canvas.hide_hints()
            self._set_status(CT.STATUS_AI_TURN, player)
            engine = self._autoplay_engines[player]
            self.after(
                CG.AUTOPLAY_MOVE_DELAY_MS,
                lambda: self._schedule_ai_move(player, engine, self._game_id),
            )
        elif player == self._human_player:
            self._board_canvas.set_enabled(True)
            self._board_canvas.show_hints(valid)
            self._set_status(CT.STATUS_HUMAN_TURN, player)
            self._set_hint_btn_enabled(True)
        else:
            self._set_hint_btn_enabled(False)
            self._board_canvas.set_enabled(False)
            self._board_canvas.hide_hints()
            self._set_status(CT.STATUS_AI_TURN, player)
            self.after(
                CG.AI_THINK_DELAY_MS,
                lambda: self._schedule_ai_move(player, None, self._game_id),
            )

    def _handle_pass(self, player: int) -> None:
        """Called when the current player has no valid moves."""
        p_name = (CT.PLAYER_1_NAME if player == PLAYER_1 else CT.PLAYER_2_NAME)
        self._set_status(CT.make_status_pass(p_name), player)
        self._set_hint_btn_enabled(False)
        self._board_canvas.cancel_hint()
        self._board_canvas.set_enabled(False)
        self._board_canvas.hide_hints()
        log.debug("Player %d has no valid moves -- will pass", player)

        if self._stats:
            self._stats.record_pass(player)

        self.after(CG.PASS_NOTIFY_DURATION_MS, self._commit_pass)

    def _commit_pass(self) -> None:
        if self._gs is None:
            return
        self._gs.do_pass()
        self._update_panel()
        if self._gs.game_over:
            self._on_game_over()
        else:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._begin_phase)

    def _on_human_cell_click(self, row: int, col: int) -> None:
        if self._gs is None or self._gs.game_over:
            return
        if self._gs.current_player != self._human_player:
            return
        valid = get_valid_moves(self._gs.board,
                                self._gs.current_player,
                                self._gs.grid_size)
        if (row, col) not in valid:
            return
        self._set_hint_btn_enabled(False)
        self._board_canvas.cancel_hint()
        self._board_canvas.set_enabled(False)
        self._board_canvas.hide_hints()
        self._commit_move(row, col)

    def _commit_move(self, row: int, col: int) -> None:
        if self._gs is None:
            return
        player  = self._gs.current_player
        flipped = self._gs.place_disc(row, col)
        self._last_flip[player] = len(flipped)

        if self._stats:
            self._stats.record_move(
                player, row, col, len(flipped),
                self._gs.board, self._gs.grid_size,
            )

        self._set_status(CT.STATUS_ANIMATING)
        self._board_canvas.animate_place(
            row, col, player, flipped,
            lambda: self._after_animation(),
        )

    def _after_animation(self) -> None:
        if self._gs is None:
            return
        if self._gs.game_over:
            self._on_game_over()
        else:
            self.after(CG.AI_INTER_MOVE_PAUSE_MS, self._begin_phase)

    # ------------------------------------------------------------------
    # AI background thread
    # ------------------------------------------------------------------

    def _schedule_ai_move(self, player: int, engine, game_id: int) -> None:
        if game_id != self._game_id:
            return
        if self._gs is None or self._gs.game_over:
            return

        board_copy = [r[:] for r in self._gs.board]
        grid_size  = self._gs.grid_size

        def _run() -> None:
            if engine is None:
                move = AE.next_move(board_copy, player, grid_size)
            else:
                move = engine.next_move(board_copy, player, grid_size)
            self.after(0, lambda: self._on_ai_result(move, player, game_id))

        t = threading.Thread(target=_run, daemon=True,
                             name="AI-P" + str(player))
        t.start()

    def _on_ai_result(self, move: "tuple[int,int]",
                      player: int, game_id: int) -> None:
        if game_id != self._game_id:
            log.debug("Discarding stale AI result (game changed)")
            return
        if self._gs is None or self._gs.game_over:
            return
        if self._gs.current_player != player:
            log.debug("Discarding stale AI result (player mismatch)")
            return
        self._commit_move(move[0], move[1])

    # ------------------------------------------------------------------
    # Live panel
    # ------------------------------------------------------------------

    def _update_panel(self) -> None:
        if self._live_panel is None or self._gs is None:
            return
        st = self._stats
        self._live_panel.update(
            board          = self._gs.board,
            grid_size      = self._gs.grid_size,
            current_player = self._gs.current_player,
            move_count_p1  = st.player_move_count(PLAYER_1) if st else 0,
            move_count_p2  = st.player_move_count(PLAYER_2) if st else 0,
            pass_count_p1  = st.player_pass_count(PLAYER_1) if st else 0,
            pass_count_p2  = st.player_pass_count(PLAYER_2) if st else 0,
            last_flip_p1   = self._last_flip.get(PLAYER_1, 0),
            last_flip_p2   = self._last_flip.get(PLAYER_2, 0),
        )

    # ------------------------------------------------------------------
    # Hint (Get Hint button)
    # ------------------------------------------------------------------

    def _set_hint_btn_enabled(self, enabled: bool) -> None:
        if self._hint_btn is not None:
            self._hint_btn.configure(
                state="normal" if (enabled and not self._hint_busy) else "disabled"
            )

    def _on_get_hint(self) -> None:
        if (self._gs is None or self._gs.game_over or
                self._hint_ai is None or self._hint_busy):
            return
        if self._gs.current_player != self._human_player:
            return

        valid = get_valid_moves(self._gs.board,
                                self._gs.current_player,
                                self._gs.grid_size)
        if not valid:
            self._set_status(CT.STATUS_HINT_NO_MOVES, self._human_player)
            return

        self._hint_busy = True
        self._set_hint_btn_enabled(False)
        self._board_canvas.set_enabled(False)
        self._board_canvas.hide_hints()
        self._set_status(CT.STATUS_HINT_THINKING, self._human_player)

        board_copy = [r[:] for r in self._gs.board]
        player     = self._gs.current_player
        grid_size  = self._gs.grid_size
        game_id    = self._game_id

        def _run() -> None:
            move   = self._hint_ai.next_move(board_copy, player, grid_size)
            reason = explain_hint(board_copy, move[0], move[1], player, grid_size)
            self.after(0, lambda: self._on_hint_result(move, reason, player, game_id))

        t = threading.Thread(target=_run, daemon=True, name="AI-Hint")
        t.start()
        log.debug("Hint AI thread started for player %d", player)

    def _on_hint_result(self, move: "tuple[int,int]", reason: str,
                        player: int, game_id: int) -> None:
        if game_id != self._game_id or self._gs is None or self._gs.game_over:
            self._hint_busy = False
            return

        valid = get_valid_moves(self._gs.board,
                                self._gs.current_player,
                                self._gs.grid_size)
        self._board_canvas.set_enabled(True)
        self._board_canvas.show_hints(valid)
        self._set_status(CT.STATUS_HINT_REASON.format(reason=reason), player)
        log.debug("Hint result: row=%d col=%d reason=%r", move[0], move[1], reason)

        self._board_canvas.flash_hint(
            move[0], move[1],
            lambda: self._after_hint(),
        )

    def _after_hint(self) -> None:
        self._hint_busy = False
        if (self._gs is not None and
                not self._gs.game_over and
                self._gs.current_player == self._human_player):
            self._set_hint_btn_enabled(True)

    # ------------------------------------------------------------------
    # Game over
    # ------------------------------------------------------------------

    def _on_game_over(self) -> None:
        if self._gs is None or self._stats is None:
            return
        winner = self._gs.winner
        reason = "win" if winner is not None else "draw"
        self._stats.finalise(winner, reason, self._human_player)

        if winner == PLAYER_1:
            msg   = (CT.GAMEOVER_HUMAN_WINS if self._human_player == PLAYER_1
                     else CT.GAMEOVER_P1_WINS)
            color = UI.TURN_COLOR_P1
        elif winner == PLAYER_2:
            if self._human_player == PLAYER_2:
                msg = CT.GAMEOVER_HUMAN_WINS
            elif self._human_player == PLAYER_1:
                msg = CT.GAMEOVER_AI_WINS
            else:
                msg = CT.GAMEOVER_P2_WINS
            color = UI.TURN_COLOR_P2
        else:
            msg   = CT.GAMEOVER_DRAW
            color = UI.TURN_COLOR_DRAW

        self._set_status(msg)
        if self._status_label:
            self._status_label.configure(fg=color)
        self._set_hint_btn_enabled(False)
        self._board_canvas.cancel_hint()
        self._board_canvas.set_enabled(False)
        log.debug("Game over: winner=%s reason=%s", winner, reason)

        counts = self._gs.disc_counts()
        log.debug(
            "Final disc counts: P1(Black)=%d P2(White)=%d",
            counts.get(PLAYER_1, 0), counts.get(PLAYER_2, 0),
        )

        if winner is not None:
            valid = [
                (r, c)
                for r in range(self._gs.grid_size)
                for c in range(self._gs.grid_size)
                if self._gs.board[r][c] == winner
            ]
            self._board_canvas.flash_win(valid, winner,
                                         lambda: self.after(0, self._show_stats))
        else:
            self.after(UI.STATS_DELAY_MS, self._show_stats)

    def _on_loaded_game_over(self) -> None:
        if self._gs is None:
            return
        winner = self._gs.winner
        if winner == PLAYER_1:
            msg, color = CT.GAMEOVER_P1_WINS, UI.TURN_COLOR_P1
        elif winner == PLAYER_2:
            msg, color = CT.GAMEOVER_P2_WINS, UI.TURN_COLOR_P2
        else:
            msg, color = CT.GAMEOVER_DRAW, UI.TURN_COLOR_DRAW
        self._set_status(msg)
        if self._status_label:
            self._status_label.configure(fg=color)
        self._board_canvas.set_enabled(False)

    def _show_stats(self) -> None:
        if self._stats is None:
            return
        if self._stats.total_moves == 0:
            log.debug("Skipping stats window (no moves recorded)")
            return
        StatsWindow(self, self._stats, self._human_player)

    # ------------------------------------------------------------------
    # Menu / button handlers
    # ------------------------------------------------------------------

    def _on_new_game(self) -> None:
        log.debug("New game requested")
        self._game_id += 1
        self._show_start()

    def _on_save_game(self) -> None:
        if self._gs is None:
            messagebox.showinfo(CT.WINDOW_TITLE, CT.MSG_NO_GAME)
            return
        path = filedialog.asksaveasfilename(
            title=CT.MENU_SAVE,
            defaultextension=".json",
            filetypes=[(CT.SAVE_FILETYPE, "*.json")],
        )
        if not path:
            return
        try:
            save_game(self._gs, self._human_player, path)
            messagebox.showinfo(CT.WINDOW_TITLE,
                                CT.MSG_SAVED.format(path=path))
        except Exception as exc:
            messagebox.showerror(CT.WINDOW_TITLE,
                                 CT.MSG_SAVE_ERROR.format(err=exc))

    def _on_load_game(self) -> None:
        path = filedialog.askopenfilename(
            title=CT.MENU_LOAD,
            filetypes=[(CT.SAVE_FILETYPE, "*.json")],
        )
        if not path:
            return
        try:
            state, human_player = load_game(path)
        except Exception as exc:
            messagebox.showerror(CT.WINDOW_TITLE,
                                 CT.MSG_LOAD_ERROR.format(err=exc))
            return
        self._autoplay = False
        self._game_id += 1
        self._show_game(state, human_player)

    def _on_start_normal(self, grid_size: int, first_player: str) -> None:
        self._autoplay = False
        self._on_start_new_game(grid_size, first_player)

    def _on_start_autoplay(self, grid_size: int) -> None:
        self._autoplay = True
        self._on_start_new_game(grid_size, _FIRST_HUMAN)

    def _on_start_new_game(self, grid_size: int, first_player: str) -> None:
        log.debug("Start new game: grid=%d first=%s autoplay=%s",
                  grid_size, first_player, self._autoplay)

        if self._autoplay:
            human_player = None
            first_pid    = PLAYER_1
        elif first_player == _FIRST_HUMAN:
            human_player = PLAYER_1
            first_pid    = PLAYER_1
        else:
            human_player = PLAYER_2
            first_pid    = PLAYER_1   # Black always starts in Reversi

        state = GameState(first_player=first_pid, grid_size=grid_size)
        self._show_game(state, human_player)

    # ------------------------------------------------------------------
    # Help dialogs
    # ------------------------------------------------------------------

    def _show_rules(self) -> None:
        s   = UI
        dlg = tk.Toplevel(self)
        dlg.title(CT.MENU_RULES)
        dlg.configure(bg=s.BG_COLOR)
        dlg.resizable(False, False)
        dlg.grab_set()
        tk.Label(dlg, text=CT.RULES_TEXT,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 wraplength=s.RULES_WRAP_WIDTH, justify="left",
                 padx=s.RULES_LABEL_PADX, pady=s.RULES_LABEL_PADY,
                 ).pack()
        tk.Button(dlg, text=CT.BTN_CLOSE,
                  font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                  activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                  relief=s.BTN_RELIEF, bd=s.BTN_BD,
                  padx=s.BTN_PADX, pady=s.BTN_PADY,
                  command=dlg.destroy,
                  ).pack(pady=(0, s.RULES_CLOSE_PADY_BOT))
        self._center_dialog(dlg)

    def _show_about(self) -> None:
        s   = UI
        dlg = tk.Toplevel(self)
        dlg.title(CT.ABOUT_TITLE)
        dlg.configure(bg=s.BG_COLOR)
        dlg.resizable(False, False)
        dlg.grab_set()

        tk.Label(dlg, text=CT.ABOUT_SUBTITLE,
                 font=s.START_TITLE_FONT, fg=s.START_TITLE_COLOR, bg=s.BG_COLOR,
                 ).pack(pady=(s.ABOUT_TITLE_PADY_TOP, 0), padx=s.ABOUT_PADX)

        tk.Frame(dlg, height=1, bg=s.PANEL_DIVIDER_COLOR).pack(
            fill="x", padx=s.ABOUT_DIVIDER_PADX,
            pady=(s.ABOUT_HEADER_DIVIDER_PADY, 0),
        )

        tk.Label(dlg, text=CT.ABOUT_BODY,
                 font=s.LABEL_FONT, fg=s.LABEL_COLOR, bg=s.BG_COLOR,
                 wraplength=s.ABOUT_WRAP_WIDTH, justify="center",
                 padx=s.ABOUT_PADX, pady=s.ABOUT_PADY,
                 ).pack()

        tk.Frame(dlg, height=1, bg=s.PANEL_DIVIDER_COLOR).pack(
            fill="x", padx=s.ABOUT_DIVIDER_PADX,
            pady=(s.ABOUT_BODY_DIVIDER_PADY, 0),
        )

        tk.Button(dlg, text=CT.BTN_CLOSE,
                  font=s.BTN_FONT, fg=s.BTN_FG, bg=s.BTN_BG,
                  activebackground=s.BTN_ACTIVE_BG, activeforeground=s.BTN_FG,
                  relief=s.BTN_RELIEF, bd=s.BTN_BD,
                  padx=s.BTN_PADX, pady=s.BTN_PADY,
                  command=dlg.destroy,
                  ).pack(pady=(s.ABOUT_CLOSE_PADY_TOP, s.ABOUT_CLOSE_PADY_BOT))

        self._center_dialog(dlg)

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def _set_status(self, text: str, player: "int | None" = None) -> None:
        if self._status_label is None:
            return
        if player == PLAYER_1:
            color = UI.TURN_COLOR_P1
        elif player == PLAYER_2:
            color = UI.TURN_COLOR_P2
        else:
            color = UI.STATUS_COLOR
        self._status_label.configure(text=text, fg=color)
        log.debug("Status: %r", text)

    def _fit_window(self) -> None:
        self.update_idletasks()
        w  = max(self.winfo_reqwidth(), self._min_width)
        h  = self.winfo_reqheight()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = max(0, (sw - w) // 2)
        y  = max(0, (sh - h) // 2)
        self.geometry(str(w) + "x" + str(h) + "+" + str(x) + "+" + str(y))

    def _center_dialog(self, dlg: tk.Toplevel) -> None:
        dlg.update_idletasks()
        pw = self.winfo_width()
        ph = self.winfo_height()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        w  = dlg.winfo_reqwidth()
        h  = dlg.winfo_reqheight()
        x  = px + (pw - w) // 2
        y  = py + (ph - h) // 2
        dlg.geometry("+" + str(x) + "+" + str(y))
