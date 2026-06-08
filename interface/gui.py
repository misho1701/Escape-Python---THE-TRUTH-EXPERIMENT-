import tkinter as tk
from tkinter import font as tkfont
from game import Game

BG          = "#1a1a2e"
BG_PANEL    = "#16213e"
BG_INPUT    = "#0f3460"
ACCENT      = "#e94560"
TEXT_MAIN   = "#eaeaea"
TEXT_DIM    = "#7a7a9a"
TEXT_SYSTEM = "#f0a500"
TEXT_GOOD   = "#4ecca3"
TEXT_ROOM   = "#a8dadc"

ROOM_DEFAULT  = "#0f3460"
ROOM_CURRENT  = "#e94560"
ROOM_BORDER   = "#a8dadc"
ROOM_TEXT     = "#eaeaea"
ROOM_VISITED  = "#1a4a6b"

CONN_LINE   = "#a8dadc"
CONN_LOCKED = "#e94560"

ROOM_W, ROOM_H = 110, 44
ROOM_R          = 8

ROOM_POS = {
    "Cell":               (30,  200),
    "Hall":               (185, 200),
    "Ventilation Shaft":  (185, 100),
    "Server Room":        (185, 300),
    "Laboratory":         (340, 200),
    "Exit":               (495, 200),
}

ROOM_LABELS = {
    "Cell":              "Cell",
    "Hall":              "Hall",
    "Ventilation Shaft": "Vent Shaft",
    "Server Room":       "Server Room",
    "Laboratory":        "Laboratory",
    "Exit":              "Exit",
}

CONNECTIONS = [
    ("Cell",              "Hall",              False),
    ("Hall",              "Ventilation Shaft", True),
    ("Ventilation Shaft", "Server Room",       True),
    ("Server Room",       "Laboratory",        False),
    ("Hall",              "Laboratory",        False),
    ("Laboratory",        "Exit",              False),
]

MAP_W = 640
MAP_H = 420

def room_center(name):
    x, y = ROOM_POS[name]
    return x + ROOM_W // 2, y + ROOM_H // 2


def clamp_to_edge(x1, y1, x2, y2):
    cx, cy = x1, y1
    tx, ty = x2, y2
    dx, dy = tx - cx, ty - cy
    if abs(dx) == 0 and abs(dy) == 0:
        return cx, cy

    # half-extents
    hw, hh = ROOM_W / 2, ROOM_H / 2

    scale_x = (hw / abs(dx)) if dx != 0 else float("inf")
    scale_y = (hh / abs(dy)) if dy != 0 else float("inf")
    t = min(scale_x, scale_y)

    return cx + dx * t, cy + dy * t

class EscapePythonGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Escape Python — The Truth Experiment")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.game = Game()
        self.visited = {self.game.player.current_room.name}

        self._build_fonts()
        self._build_layout()
        self._draw_map()
        self._welcome()

    # --------------------------------------------------
    # FONTS
    # --------------------------------------------------

    def _build_fonts(self):
        self.font_mono   = tkfont.Font(family="Courier New", size=11)
        self.font_mono_b = tkfont.Font(family="Courier New", size=11, weight="bold")
        self.font_small  = tkfont.Font(family="Courier New", size=9)
        self.font_map    = tkfont.Font(family="Courier New", size=9, weight="bold")
        self.font_title  = tkfont.Font(family="Courier New", size=13, weight="bold")
        self.font_hint   = tkfont.Font(family="Courier New", size=9)

    def _build_layout(self):
        self.root.geometry("1100x680")

        left = tk.Frame(self.root, bg=BG_PANEL, width=MAP_W)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left.pack_propagate(False)

        map_title = tk.Label(
            left, text="FACILITY MAP",
            bg=BG_PANEL, fg=ACCENT,
            font=self.font_title,
            anchor="w", padx=12, pady=8
        )
        map_title.pack(fill=tk.X)

        self.canvas = tk.Canvas(
            left, width=MAP_W, height=MAP_H,
            bg=BG_PANEL, highlightthickness=0
        )
        self.canvas.pack(padx=8, pady=(0, 8))

        legend_frame = tk.Frame(left, bg=BG_PANEL)
        legend_frame.pack(fill=tk.X, padx=12, pady=(0, 6))

        for color, label in [
            (ROOM_CURRENT, "Current room"),
            (ROOM_VISITED, "Visited"),
            (ROOM_DEFAULT, "Unvisited"),
        ]:
            row = tk.Frame(legend_frame, bg=BG_PANEL)
            row.pack(side=tk.LEFT, padx=(0, 14))
            tk.Canvas(row, width=12, height=12, bg=color,
                      highlightthickness=1,
                      highlightbackground=ROOM_BORDER).pack(side=tk.LEFT, padx=(0, 4))
            tk.Label(row, text=label, fg=TEXT_DIM,
                     bg=BG_PANEL, font=self.font_hint).pack(side=tk.LEFT)

        inv_frame = tk.Frame(left, bg=BG_PANEL)
        inv_frame.pack(fill=tk.X, padx=12, pady=(4, 0))

        tk.Label(inv_frame, text="INVENTORY", fg=ACCENT,
                 bg=BG_PANEL, font=self.font_hint).pack(anchor="w")

        self.inv_label = tk.Label(
            inv_frame, text="Empty",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=self.font_hint, wraplength=580,
            justify=tk.LEFT, anchor="w"
        )
        self.inv_label.pack(anchor="w", pady=(2, 0))

        ach_frame = tk.Frame(left, bg=BG_PANEL)
        ach_frame.pack(fill=tk.X, padx=12, pady=(8, 0))

        tk.Label(ach_frame, text="ACHIEVEMENTS", fg=ACCENT,
                 bg=BG_PANEL, font=self.font_hint).pack(anchor="w")

        self.ach_label = tk.Label(
            ach_frame, text="None yet",
            fg=TEXT_DIM, bg=BG_PANEL,
            font=self.font_hint, wraplength=580,
            justify=tk.LEFT, anchor="w"
        )
        self.ach_label.pack(anchor="w", pady=(2, 0))

        right = tk.Frame(self.root, bg=BG)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True,
                   padx=(5, 10), pady=10)

        game_title = tk.Label(
            right,
            text="ESCAPE PYTHON  //  THE TRUTH EXPERIMENT",
            bg=BG, fg=ACCENT, font=self.font_title,
            anchor="w", pady=8
        )
        game_title.pack(fill=tk.X)

        out_frame = tk.Frame(right, bg=BG)
        out_frame.pack(fill=tk.BOTH, expand=True)

        self.output = tk.Text(
            out_frame,
            bg=BG, fg=TEXT_MAIN,
            font=self.font_mono,
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            padx=10, pady=8,
            cursor="arrow",
            selectbackground=BG_INPUT,
            insertbackground=TEXT_MAIN,
        )
        self.output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(out_frame, command=self.output.yview,
                                 bg=BG_PANEL, troughcolor=BG,
                                 activebackground=ACCENT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output.configure(yscrollcommand=scrollbar.set)

        # text tags
        self.output.tag_configure("system",  foreground=TEXT_SYSTEM, font=self.font_mono_b)
        self.output.tag_configure("good",    foreground=TEXT_GOOD,   font=self.font_mono_b)
        self.output.tag_configure("room",    foreground=TEXT_ROOM,   font=self.font_mono_b)
        self.output.tag_configure("dim",     foreground=TEXT_DIM)
        self.output.tag_configure("accent",  foreground=ACCENT,      font=self.font_mono_b)
        self.output.tag_configure("normal",  foreground=TEXT_MAIN)
        self.output.tag_configure("divider", foreground=TEXT_DIM)

        loc_frame = tk.Frame(right, bg=BG_PANEL, pady=4)
        loc_frame.pack(fill=tk.X, pady=(6, 0))

        tk.Label(loc_frame, text="LOCATION:", fg=TEXT_DIM,
                 bg=BG_PANEL, font=self.font_small,
                 padx=8).pack(side=tk.LEFT)

        self.loc_label = tk.Label(
            loc_frame,
            text=self.game.player.current_room.name.upper(),
            fg=ACCENT, bg=BG_PANEL,
            font=self.font_mono_b
        )
        self.loc_label.pack(side=tk.LEFT)

        tk.Label(loc_frame, text="  |  type 'help' for commands",
                 fg=TEXT_DIM, bg=BG_PANEL,
                 font=self.font_small).pack(side=tk.LEFT)

        input_frame = tk.Frame(right, bg=BG_INPUT, pady=2)
        input_frame.pack(fill=tk.X, pady=(2, 0))

        tk.Label(input_frame, text=">",
                 fg=ACCENT, bg=BG_INPUT,
                 font=self.font_mono_b, padx=8).pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame,
            bg=BG_INPUT, fg=TEXT_MAIN,
            font=self.font_mono,
            relief=tk.FLAT,
            insertbackground=TEXT_MAIN,
            selectbackground=ACCENT,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.entry.bind("<Return>", self._on_enter)
        self.entry.bind("<Up>",     self._history_up)
        self.entry.bind("<Down>",   self._history_down)
        self.entry.focus_set()

        # command history
        self.history     = []
        self.history_pos = -1

    def _draw_map(self):
        self.canvas.delete("all")
        current_name = self.game.player.current_room.name

        for src, dst, vertical in CONNECTIONS:
            sx, sy = room_center(src)
            dx, dy = room_center(dst)

            ex1, ey1 = clamp_to_edge(sx, sy, dx, dy)
            ex2, ey2 = clamp_to_edge(dx, dy, sx, sy)

            color = CONN_LOCKED if vertical else CONN_LINE
            dash  = (4, 3) if vertical else ()

            self.canvas.create_line(
                ex1, ey1, ex2, ey2,
                fill=color, width=1.5,
                dash=dash
            )

        for name, (rx, ry) in ROOM_POS.items():

            if name == current_name:
                fill = ROOM_CURRENT
            elif name in self.visited:
                fill = ROOM_VISITED
            else:
                fill = ROOM_DEFAULT

            if name == current_name:
                self.canvas.create_rectangle(
                    rx - 3, ry - 3,
                    rx + ROOM_W + 3, ry + ROOM_H + 3,
                    fill="", outline=ACCENT,
                    width=1.5
                )

            self.canvas.create_rectangle(
                rx, ry, rx + ROOM_W, ry + ROOM_H,
                fill=fill, outline=ROOM_BORDER,
                width=1
            )

            label = ROOM_LABELS[name]
            cx = rx + ROOM_W // 2
            cy = ry + ROOM_H // 2

            text_color = ACCENT if name == current_name else ROOM_TEXT

            self.canvas.create_text(
                cx, cy,
                text=label,
                fill=text_color,
                font=self.font_map,
                anchor="center"
            )

            room_obj = self.game.rooms[name]
            if room_obj.puzzle and not room_obj.puzzle.solved:
                self.canvas.create_text(
                    rx + ROOM_W - 6, ry + 6,
                    text="?", fill=TEXT_SYSTEM,
                    font=self.font_map, anchor="ne"
                )
            elif room_obj.puzzle and room_obj.puzzle.solved:
                self.canvas.create_text(
                    rx + ROOM_W - 6, ry + 6,
                    text="✓", fill=TEXT_GOOD,
                    font=self.font_map, anchor="ne"
                )

        dir_labels = [
            ("Cell",             "Hall",              "E"),
            ("Hall",             "Ventilation Shaft", "N"),
            ("Ventilation Shaft","Server Room",       "↓"),
            ("Server Room",      "Laboratory",        "E"),
            ("Hall",             "Laboratory",        "E"),
            ("Laboratory",       "Exit",              "E"),
        ]
        drawn = set()
        for src, dst, label in dir_labels:
            key = tuple(sorted([src, dst]))
            if key in drawn:
                continue
            drawn.add(key)
            sx, sy = room_center(src)
            dx, dy = room_center(dst)
            mx = (sx + dx) / 2
            my = (sy + dy) / 2
            self.canvas.create_text(
                mx, my - 8,
                text=label, fill=TEXT_DIM,
                font=self.font_small
            )

    def _print(self, text, tag="normal"):
        self.output.configure(state=tk.NORMAL)
        self.output.insert(tk.END, text + "\n", tag)
        self.output.configure(state=tk.DISABLED)
        self.output.see(tk.END)

    def _divider(self):
        self._print("─" * 44, "divider")

    def _welcome(self):
        self._print("ESCAPE PYTHON — THE TRUTH EXPERIMENT", "accent")
        self._divider()
        self._print("")
        self._print("You slowly regain consciousness.", "dim")
        self._print("Your head hurts.", "dim")
        self._print("You don't remember who you are.", "dim")
        self._print("You don't remember how you got here.", "dim")
        self._print("")
        self._print(self.game.player.current_room.description.strip(), "room")
        self._print("")
        self._print("Type 'help' to see all commands.", "dim")
        self._divider()

    def _tag_for(self, text):
        t = text.lower()
        if any(w in t for w in ["achievement unlocked", "correct!", "unlocked"]):
            return "good"
        if any(w in t for w in ["wrong", "you need", "can't", "no puzzle", "unknown"]):
            return "accent"
        if any(w in t for w in ["you move to", "location:", "exit"]):
            return "room"
        if any(w in t for w in ["saved", "loaded", "goodbye"]):
            return "system"
        return "normal"

    def _update_sidebar(self):
        inv = self.game.player.inventory
        if inv:
            self.inv_label.configure(
                text="  ".join(i.name for i in inv),
                fg=TEXT_MAIN
            )
        else:
            self.inv_label.configure(text="Empty", fg=TEXT_DIM)

        ach = self.game.achievements.unlocked
        if ach:
            self.ach_label.configure(
                text="  ".join(ach),
                fg=TEXT_GOOD
            )
        else:
            self.ach_label.configure(text="None yet", fg=TEXT_DIM)

        self.loc_label.configure(
            text=self.game.player.current_room.name.upper()
        )

    def _on_enter(self, event=None):
        cmd = self.entry.get().strip()
        if not cmd:
            return

        self.entry.delete(0, tk.END)

        if not self.history or self.history[-1] != cmd:
            self.history.append(cmd)
        self.history_pos = -1

        self._print(f"> {cmd}", "dim")

        result = self.game.process(cmd)

        if result:
            for line in result.split("\n"):
                tag = self._tag_for(line)
                self._print(line, tag)

        self._print("")

        self.visited.add(self.game.player.current_room.name)

        self._draw_map()
        self._update_sidebar()

        self.game.check_endings()

        if not self.game.running:
            self._show_ending()

    def _history_up(self, event=None):
        if not self.history:
            return
        if self.history_pos == -1:
            self.history_pos = len(self.history) - 1
        elif self.history_pos > 0:
            self.history_pos -= 1
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self.history[self.history_pos])

    def _history_down(self, event=None):
        if self.history_pos == -1:
            return
        if self.history_pos < len(self.history) - 1:
            self.history_pos += 1
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.history[self.history_pos])
        else:
            self.history_pos = -1
            self.entry.delete(0, tk.END)

    def _show_ending(self):
        self._divider()
        self._print("═" * 44, "accent")
        self._print("         ENDING REACHED", "accent")
        self._print("═" * 44, "accent")
        self._print("")

        ending_text = self.game.endings.show()
        for line in ending_text.split("\n"):
            tag = "good" if self.game.endings.current == "good" else \
                  "accent" if self.game.endings.current == "bad" else \
                  "system"
            self._print(line, tag)

        self._print("")
        self._divider()

        self.entry.configure(state=tk.DISABLED)
        self.loc_label.configure(text="GAME OVER", fg=TEXT_DIM)


def main():
    root = tk.Tk()
    app = EscapePythonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()