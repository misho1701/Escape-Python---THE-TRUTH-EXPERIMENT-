import pygame
import math
import time
from game import Game

WIN_W, WIN_H    = 1280, 750
MAP_W           = 480
PANEL_W         = WIN_W - MAP_W

FPS             = 60

C_BG            = (13,  17,  30)
C_MAP_BG        = (10,  14,  25)
C_PANEL_BG      = (16,  20,  35)
C_BORDER        = (30,  40,  70)

C_ROOM_DEFAULT  = (20,  35,  65)
C_ROOM_VISITED  = (25,  50,  85)
C_ROOM_CURRENT  = (180, 30,  60)
C_ROOM_BORDER   = (80, 130, 180)
C_ROOM_CUR_BDR  = (230, 80, 110)
C_ROOM_TEXT     = (210, 225, 245)
C_ROOM_CUR_TEXT = (255, 255, 255)

C_CONN          = (60,  100, 150)
C_CONN_VERT     = (100, 70,  130)

C_ACCENT        = (220, 50,  80)
C_TEXT          = (210, 220, 240)
C_TEXT_DIM      = (100, 115, 145)
C_TEXT_SYSTEM   = (240, 165,  40)
C_TEXT_GOOD     = (70,  200, 150)
C_TEXT_ROOM     = (120, 190, 220)
C_TEXT_BAD      = (220, 80,   80)
C_TEXT_PROMPT   = (180, 60,   90)

C_INPUT_BG      = (18,  25,  48)
C_INPUT_BORDER  = (50,  80, 130)
C_CURSOR        = (220, 50,  80)

C_BADGE_ITEM    = (30,  90,  70)
C_BADGE_PUZZLE  = (80,  60,  20)
C_BADGE_NPC     = (60,  30,  90)
C_BADGE_TEXT    = (200, 230, 215)

C_PARTICLE      = (220, 100, 120)

C_GLOW          = (200, 40,  70)

ROOM_W, ROOM_H  = 108, 46

ROOM_POS = {
    "Cell":               (18,  270),
    "Hall":               (170, 270),
    "Ventilation Shaft":  (170, 155),
    "Server Room":        (170, 385),
    "Laboratory":         (322, 270),
    "Exit":               (322, 155),
}

ROOM_SHORT = {
    "Cell":               "Cell",
    "Hall":               "Hall",
    "Ventilation Shaft":  "Vent Shaft",
    "Server Room":        "Server Room",
    "Laboratory":         "Laboratory",
    "Exit":               "Exit",
}

CONNECTIONS = [
    ("Cell",             "Hall",              False),
    ("Hall",             "Ventilation Shaft", True),
    ("Hall",             "Laboratory",        False),
    ("Ventilation Shaft","Server Room",       True),
    ("Server Room",      "Laboratory",        False),
    ("Laboratory",       "Exit",              False),
]

TAG_COLORS = {
    "normal":  C_TEXT,
    "dim":     C_TEXT_DIM,
    "system":  C_TEXT_SYSTEM,
    "good":    C_TEXT_GOOD,
    "room":    C_TEXT_ROOM,
    "accent":  C_ACCENT,
    "bad":     C_TEXT_BAD,
    "prompt":  C_TEXT_PROMPT,
}

MAX_OUTPUT_LINES = 300
VISIBLE_LINES    = 24
INPUT_MAX        = 80


def room_center(name):
    x, y = ROOM_POS[name]
    return x + ROOM_W // 2, y + ROOM_H // 2


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_rounded_rect(surf, color, rect, radius, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def tag_for_line(text):
    t = text.lower()
    if text.startswith("> "):
        return "prompt"
    if any(w in t for w in ["achievement unlocked", "correct!", "unlocked!", "green ✓"]):
        return "good"
    if any(w in t for w in ["wrong", "you need", "can't go", "unknown command",
                              "don't have", "not found", "rejected", "error"]):
        return "bad"
    if any(w in t for w in ["you move to", "you step", "you push"]):
        return "room"
    if any(w in t for w in ["saved", "loaded", "goodbye", "lockdown", "alarm", "security"]):
        return "system"
    if any(w in t for w in ["═", "╔", "╚", "║", "===", "---", "lock", "green", "red"]):
        return "system"
    if any(w in t for w in ["hint:", "tip:"]):
        return "dim"
    return "normal"


class Particle:
    def __init__(self, x, y):
        import random
        self.x = float(x)
        self.y = float(y)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-3, -0.5)
        self.life = 1.0
        self.decay = random.uniform(0.025, 0.06)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.08
        self.life -= self.decay
        return self.life > 0

    def draw(self, surf, offset_x):
        alpha = int(self.life * 255)
        col = (*C_PARTICLE, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, col, (self.size, self.size), self.size)
        surf.blit(s, (int(self.x) + offset_x - self.size,
                      int(self.y) - self.size))


class EscapePygameGUI:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Escape Python — The Truth Experiment")

        self.clock  = pygame.time.Clock()
        self.game   = Game()
        self.visited = {self.game.player.current_room.name}

        self._load_fonts()

        self.output_lines: list[tuple[str, str]] = []
        self.scroll_offset = 0   # lines scrolled from bottom

        self.input_text   = ""
        self.cursor_vis   = True
        self.cursor_timer = 0.0
        self.history      = []
        self.history_pos  = -1

        self.glow_t       = 0.0

        self.particles: list[Particle] = []

        self.map_surf   = pygame.Surface((MAP_W, WIN_H))
        self.panel_surf = pygame.Surface((PANEL_W, WIN_H))

        self.scrollbar_dragging = False

        self._welcome()

    def _load_fonts(self):
        try:
            self.font_ui    = pygame.font.SysFont("Courier New", 14)
            self.font_ui_b  = pygame.font.SysFont("Courier New", 14, bold=True)
            self.font_small = pygame.font.SysFont("Courier New", 11)
            self.font_map   = pygame.font.SysFont("Courier New", 11, bold=True)
            self.font_title = pygame.font.SysFont("Courier New", 16, bold=True)
            self.font_input = pygame.font.SysFont("Courier New", 15)
            self.font_badge = pygame.font.SysFont("Courier New", 9,  bold=True)
        except Exception:
            mono = pygame.font.get_default_font()
            self.font_ui    = pygame.font.Font(mono, 14)
            self.font_ui_b  = pygame.font.Font(mono, 14)
            self.font_small = pygame.font.Font(mono, 11)
            self.font_map   = pygame.font.Font(mono, 11)
            self.font_title = pygame.font.Font(mono, 16)
            self.font_input = pygame.font.Font(mono, 15)
            self.font_badge = pygame.font.Font(mono, 9)

    def _print(self, text, tag=None):
        for line in text.split("\n"):
            t = tag if tag else tag_for_line(line)
            self.output_lines.append((line, t))

        if len(self.output_lines) > MAX_OUTPUT_LINES:
            self.output_lines = self.output_lines[-MAX_OUTPUT_LINES:]

        if self.scroll_offset > 0:
            self.scroll_offset = 0

    def _divider(self):
        self._print("─" * 52, "dim")

    def _welcome(self):
        self._print("ESCAPE PYTHON  //  THE TRUTH EXPERIMENT", "accent")
        self._divider()
        self._print("")
        self._print("You slowly regain consciousness.", "dim")
        self._print("Your head hurts.", "dim")
        self._print("You don't remember who you are.", "dim")
        self._print("")
        desc = self.game.player.current_room.description.strip()
        for line in desc.split("\n"):
            self._print(line, "room")
        self._print("")
        self._print("Type 'help' to see all commands.", "dim")
        self._divider()

    def _submit(self):
        cmd = self.input_text.strip()
        self.input_text = ""
        self.history_pos = -1

        if not cmd:
            return

        if not self.history or self.history[-1] != cmd:
            self.history.append(cmd)

        self._print(f"> {cmd}", "prompt")

        result = self.game.process(cmd)
        if result:
            self._print(result)
        self._print("")

        if cmd.lower().startswith("go "):
            cx, cy = room_center(self.game.player.current_room.name)
            for _ in range(18):
                self.particles.append(Particle(cx, cy))

        self.visited.add(self.game.player.current_room.name)

        self.game.check_endings()

        if not self.game.running:
            self._print("═" * 52, "accent")
            ending = self.game.endings.show()
            tag = ("good" if self.game.endings.current == "good" else
                   "bad"  if self.game.endings.current == "bad"  else
                   "system")
            self._print(ending, tag)
            self._divider()

    def _draw_map(self):
        s = self.map_surf
        s.fill(C_MAP_BG)

        current_name = self.game.player.current_room.name

        title = self.font_title.render("FACILITY MAP", True, C_ACCENT)
        s.blit(title, (14, 14))

        pygame.draw.line(s, C_BORDER, (0, 42), (MAP_W, 42), 1)

        for src, dst, vertical in CONNECTIONS:
            sx, sy = room_center(src)
            dx, dy = room_center(dst)

            col  = C_CONN_VERT if vertical else C_CONN
            dash = 6 if vertical else 0

            if dash:
                self._draw_dashed_line(s, col, sx, sy, dx, dy, dash)
            else:
                pygame.draw.line(s, col, (sx, sy), (dx, dy), 1)

            mx, my = (sx + dx) // 2, (sy + dy) // 2
            self._draw_arrow(s, col, sx, sy, dx, dy)

        for name, (rx, ry) in ROOM_POS.items():
            self._draw_room(s, name, rx, ry, current_name)

        legend_y = WIN_H - 175
        pygame.draw.line(s, C_BORDER, (0, legend_y - 8), (MAP_W, legend_y - 8), 1)
        self._legend(s, legend_y)

        inv_y = legend_y + 30
        pygame.draw.line(s, C_BORDER, (0, inv_y - 6), (MAP_W, inv_y - 6), 1)
        self._draw_inv_ach(s, inv_y)

    def _draw_room(self, s, name, rx, ry, current_name):
        is_current = (name == current_name)
        is_visited = (name in self.visited)

        fill   = C_ROOM_CURRENT  if is_current else \
                 C_ROOM_VISITED   if is_visited  else \
                 C_ROOM_DEFAULT
        border = C_ROOM_CUR_BDR  if is_current else C_ROOM_BORDER
        text_c = C_ROOM_CUR_TEXT if is_current else C_ROOM_TEXT

        rect = pygame.Rect(rx, ry, ROOM_W, ROOM_H)

        if is_current:
            glow_alpha = int(80 + 60 * math.sin(self.glow_t * 3))
            glow_size  = 8
            glow_surf  = pygame.Surface(
                (ROOM_W + glow_size * 2, ROOM_H + glow_size * 2),
                pygame.SRCALPHA
            )
            glow_col   = (*C_GLOW, glow_alpha)
            pygame.draw.rect(
                glow_surf, glow_col,
                (0, 0, ROOM_W + glow_size * 2, ROOM_H + glow_size * 2),
                border_radius=12
            )
            s.blit(glow_surf, (rx - glow_size, ry - glow_size))

        draw_rounded_rect(s, fill, rect, 8)
        draw_rounded_rect(s, (0, 0, 0, 0), rect, 8,
                          border=2, border_color=border)

        label = ROOM_SHORT[name]
        surf  = self.font_map.render(label, True, text_c)
        lx    = rx + (ROOM_W - surf.get_width()) // 2
        ly    = ry + (ROOM_H - surf.get_height()) // 2 - 4
        s.blit(surf, (lx, ly))

        bx = rx + 4
        by = ry + ROOM_H - 14

        room_obj = self.game.rooms[name]

        if room_obj.puzzle:
            badge_text = "✓" if room_obj.puzzle.solved else "?"
            badge_col  = C_TEXT_GOOD if room_obj.puzzle.solved else C_BADGE_PUZZLE
            self._badge(s, badge_text, bx, by, badge_col)
            bx += 20

        if room_obj.items:
            self._badge(s, f"×{len(room_obj.items)}", bx, by, C_BADGE_ITEM)
            bx += 26

        if name in ("Hall", "Server Room"):
            self._badge(s, "NPC", bx, by, C_BADGE_NPC)

    def _badge(self, s, text, x, y, color):
        surf = self.font_badge.render(text, True, C_BADGE_TEXT)
        w    = surf.get_width() + 6
        h    = surf.get_height() + 2
        pygame.draw.rect(s, color, (x, y, w, h), border_radius=3)
        s.blit(surf, (x + 3, y + 1))

    def _draw_dashed_line(self, s, col, x1, y1, x2, y2, dash_len):
        dx, dy = x2 - x1, y2 - y1
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return
        steps  = int(dist / dash_len)
        for i in range(steps):
            if i % 2 == 0:
                t0 = i / steps
                t1 = (i + 1) / steps
                pygame.draw.line(
                    s, col,
                    (int(x1 + dx * t0), int(y1 + dy * t0)),
                    (int(x1 + dx * t1), int(y1 + dy * t1)),
                    1
                )

    def _draw_arrow(self, s, col, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return
        ux, uy = dx / dist, dy / dist
        # midpoint
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        size = 5
        tip  = (int(mx + ux * size), int(my + uy * size))
        l    = (int(mx - ux * size - uy * size), int(my - uy * size + ux * size))
        r    = (int(mx - ux * size + uy * size), int(my - uy * size - ux * size))
        pygame.draw.polygon(s, col, [tip, l, r])

    def _legend(self, s, y):
        items = [
            (C_ROOM_CURRENT, "Current"),
            (C_ROOM_VISITED, "Visited"),
            (C_ROOM_DEFAULT, "Unseen"),
        ]
        x = 14
        for col, label in items:
            pygame.draw.rect(s, col, (x, y + 2, 10, 10), border_radius=2)
            pygame.draw.rect(s, C_ROOM_BORDER, (x, y + 2, 10, 10), 1, border_radius=2)
            t = self.font_small.render(label, True, C_TEXT_DIM)
            s.blit(t, (x + 14, y))
            x += 14 + t.get_width() + 14

    def _draw_inv_ach(self, s, y):
        pad = 14

        inv_label = self.font_small.render("INVENTORY", True, C_ACCENT)
        s.blit(inv_label, (pad, y))

        inv = self.game.player.inventory
        if inv:
            inv_text = "  ".join(i.name for i in inv)
            col = C_TEXT
        else:
            inv_text = "Empty"
            col = C_TEXT_DIM

        max_w = MAP_W - pad * 2
        words = inv_text.split("  ")
        line = ""
        row_y = y + 16
        for word in words:
            test = (line + "  " + word).strip()
            if self.font_ui.size(test)[0] > max_w and line:
                s.blit(self.font_ui.render(line, True, col), (pad, row_y))
                row_y += 17
                line = word
            else:
                line = test
        if line:
            s.blit(self.font_ui.render(line, True, col), (pad, row_y))
        row_y += 22

        pygame.draw.line(s, C_BORDER, (pad, row_y), (MAP_W - pad, row_y), 1)
        row_y += 8

        ach_label = self.font_small.render("ACHIEVEMENTS", True, C_ACCENT)
        s.blit(ach_label, (pad, row_y))
        row_y += 16

        ach = sorted(self.game.achievements.unlocked)
        if ach:
            for achievement in ach:
                dot = self.font_ui.render("✓ " + achievement, True, C_TEXT_GOOD)
                s.blit(dot, (pad, row_y))
                row_y += 17
        else:
            none_surf = self.font_ui.render("None yet", True, C_TEXT_DIM)
            s.blit(none_surf, (pad, row_y))

    def _draw_panel(self):
        s = self.panel_surf
        s.fill(C_PANEL_BG)

        title_surf = self.font_title.render(
            "ESCAPE PYTHON  //  THE TRUTH EXPERIMENT", True, C_ACCENT
        )
        s.blit(title_surf, (16, 12))
        pygame.draw.line(s, C_BORDER, (0, 38), (PANEL_W, 38), 1)

        out_h      = WIN_H - 38 - 36 - 44  # minus title, location bar, input
        line_h     = 19
        visible    = out_h // line_h
        total      = len(self.output_lines)
        start      = max(0, total - visible - self.scroll_offset)
        end        = min(total, start + visible)
        lines_show = self.output_lines[start:end]

        oy = 44
        for text, tag in lines_show:
            col  = TAG_COLORS.get(tag, C_TEXT)
            font = self.font_ui_b if tag in ("accent", "system", "good") else self.font_ui
            if text:
                surf = font.render(text[:90], True, col)
                s.blit(surf, (16, oy))
            oy += line_h

        sb_x = PANEL_W - 10
        sb_h = WIN_H - 38 - 36 - 44
        pygame.draw.rect(s, C_BORDER, (sb_x, 44, 6, sb_h), border_radius=3)
        if total > visible:
            thumb_h  = max(20, int(sb_h * visible / total))
            max_off  = total - visible
            ratio    = 1.0 - (self.scroll_offset / max_off) if max_off > 0 else 1.0
            thumb_y  = 44 + int((sb_h - thumb_h) * ratio)
            pygame.draw.rect(s, C_TEXT_DIM, (sb_x, thumb_y, 6, thumb_h), border_radius=3)

        loc_y = WIN_H - 44 - 36
        pygame.draw.line(s, C_BORDER, (0, loc_y), (PANEL_W, loc_y), 1)
        loc_name = self.game.player.current_room.name.upper()
        loc_surf = self.font_ui_b.render(f"  LOCATION: {loc_name}", True, C_ACCENT)
        hint     = self.font_small.render(
            "  scroll: mouse wheel  |  history: ↑↓", True, C_TEXT_DIM
        )
        s.blit(loc_surf, (0, loc_y + 8))
        s.blit(hint, (loc_surf.get_width() + 10, loc_y + 10))

        # Input bar
        inp_y = WIN_H - 44
        pygame.draw.line(s, C_BORDER, (0, inp_y), (PANEL_W, inp_y), 1)
        pygame.draw.rect(s, C_INPUT_BG, (0, inp_y, PANEL_W, 44))
        pygame.draw.rect(s, C_INPUT_BORDER, (0, inp_y, PANEL_W, 44), 1)

        prompt = self.font_input.render(">", True, C_ACCENT)
        s.blit(prompt, (12, inp_y + 12))

        inp_display = self.input_text
        inp_surf    = self.font_input.render(inp_display, True, C_TEXT)
        s.blit(inp_surf, (32, inp_y + 12))

        if self.cursor_vis:
            cx = 32 + self.font_input.size(inp_display)[0]
            pygame.draw.rect(s, C_CURSOR, (cx, inp_y + 13, 2, 18))

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def _draw_particles(self):
        for p in self.particles:
            p.draw(self.screen, MAP_W)

    def run(self):
        running = True

        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.glow_t      += dt
            self.cursor_timer += dt
            if self.cursor_timer > 0.53:
                self.cursor_vis   = not self.cursor_vis
                self.cursor_timer = 0.0

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event)

                elif event.type == pygame.MOUSEWHEEL:
                    total   = len(self.output_lines)
                    visible = (WIN_H - 38 - 36 - 44) // 19
                    max_off = max(0, total - visible)
                    self.scroll_offset = max(
                        0, min(max_off, self.scroll_offset - event.y)
                    )

                elif event.type == pygame.TEXTINPUT:
                    if len(self.input_text) < INPUT_MAX:
                        self.input_text += event.text

            self._update_particles()

            self.screen.fill(C_BG)

            self._draw_map()
            self._draw_panel()

            self.screen.blit(self.map_surf,   (0, 0))
            self.screen.blit(self.panel_surf, (MAP_W, 0))

            pygame.draw.line(
                self.screen, C_BORDER,
                (MAP_W, 0), (MAP_W, WIN_H), 1
            )

            self._draw_particles()

            pygame.display.flip()

        pygame.quit()

    def _handle_key(self, event):
        if event.key == pygame.K_RETURN:
            self._submit()

        elif event.key == pygame.K_BACKSPACE:
            self.input_text = self.input_text[:-1]

        elif event.key == pygame.K_UP:
            if self.history:
                if self.history_pos == -1:
                    self.history_pos = len(self.history) - 1
                elif self.history_pos > 0:
                    self.history_pos -= 1
                self.input_text = self.history[self.history_pos]

        elif event.key == pygame.K_DOWN:
            if self.history_pos != -1:
                if self.history_pos < len(self.history) - 1:
                    self.history_pos += 1
                    self.input_text = self.history[self.history_pos]
                else:
                    self.history_pos = -1
                    self.input_text  = ""

        elif event.key == pygame.K_ESCAPE:
            self.input_text = ""

        elif event.key == pygame.K_PAGEUP:
            total   = len(self.output_lines)
            visible = (WIN_H - 38 - 36 - 44) // 19
            max_off = max(0, total - visible)
            self.scroll_offset = min(max_off, self.scroll_offset + visible // 2)

        elif event.key == pygame.K_PAGEDOWN:
            self.scroll_offset = max(0, self.scroll_offset - VISIBLE_LINES // 2)

def main():
    gui = EscapePygameGUI()
    gui.run()


if __name__ == "__main__":
    main()