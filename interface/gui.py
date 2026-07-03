import pygame
import pygame.gfxdraw
import math
import random
from game import Game

WIN_W,  WIN_H  = 1536, 864
MAP_W          = 620
PANEL_W        = WIN_W - MAP_W

SCALE          = 2
RWIN_W         = WIN_W  * SCALE
RWIN_H         = WIN_H  * SCALE
RMAP_W         = MAP_W  * SCALE
RPANEL_W       = PANEL_W * SCALE

FPS            = 60

C_BG            = (22,  28,  48)
C_MAP_BG        = (18,  24,  42)
C_PANEL_BG      = (24,  30,  52)
C_BORDER        = (55,  75, 120)
C_BORDER_BRIGHT = (90, 130, 190)

C_ROOM_DEFAULT  = (35,  55,  95)
C_ROOM_VISITED  = (45,  80, 130)
C_ROOM_CURRENT  = (195, 45,  75)
C_ROOM_BORDER   = (110, 165, 220)
C_ROOM_CUR_BDR  = (255, 120, 145)
C_ROOM_TEXT     = (220, 235, 255)
C_ROOM_CUR_TEXT = (255, 255, 255)
C_ROOM_UNVIS    = (170, 190, 225)

C_CONN          = (90,  145, 210)
C_CONN_VERT     = (150, 105, 190)
C_CONN_GLOW     = (110, 175, 255)

C_ACCENT        = (255,  80, 110)
C_ACCENT_DIM    = (180,  55,  80)
C_TEXT          = (225, 235, 255)
C_TEXT_DIM      = (185, 200, 235)
C_TEXT_SYSTEM   = (255, 200,  80)
C_TEXT_GOOD     = (100, 235, 180)
C_TEXT_ROOM     = (160, 220, 255)
C_TEXT_BAD      = (255, 120, 120)
C_TEXT_PROMPT   = (235, 110, 140)

C_INPUT_BG      = (28,  36,  65)
C_INPUT_BORDER  = (90, 130, 195)
C_CURSOR        = (255,  80, 110)

C_BADGE_ITEM    = (40,  130, 100)
C_BADGE_PUZZLE  = (130, 100,  35)
C_BADGE_PUZZLE_DONE = (40, 140, 80)
C_BADGE_NPC     = (100,  50, 150)
C_BADGE_TEXT    = (230, 250, 235)

C_PARTICLE      = (255, 130, 150)
C_PARTICLE2     = (150, 200, 255)
C_GLOW          = (230,  55,  90)

ROOM_W, ROOM_H = 128, 52
ROOM_R         = 12

ROOM_POS = {
    "Cell":               ( 20, 295),
    "Hall":               (194, 295),
    "Ventilation Shaft":  (194, 165),
    "Server Room":        (194, 425),
    "Laboratory":         (368, 295),
    "Exit":               (368, 165),
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
    ("Cell",              "Hall",              False),
    ("Hall",              "Ventilation Shaft", True),
    ("Hall",              "Laboratory",        False),
    ("Ventilation Shaft", "Server Room",       True),
    ("Server Room",       "Laboratory",        False),
    ("Laboratory",        "Exit",              False),
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

MAX_OUTPUT_LINES = 400
INPUT_MAX        = 80


def s(v):
    if isinstance(v, (int, float)):
        return int(v * SCALE)
    return tuple(int(x * SCALE) for x in v)


def room_center(name):
    x, y = ROOM_POS[name]
    return x + ROOM_W // 2, y + ROOM_H // 2


def tag_for_line(text):
    t = text.lower()
    if text.startswith("> "):
        return "prompt"
    if any(w in t for w in ["achievement unlocked", "correct!", "green ✓"]):
        return "good"
    if any(w in t for w in ["wrong", "you need", "can't go", "unknown command",
                             "don't have", "not found", "rejected", "sequence error"]):
        return "bad"
    if any(w in t for w in ["you move to", "you step", "you push"]):
        return "room"
    if any(w in t for w in ["saved", "loaded", "goodbye", "lockdown", "alarm",
                             "security", "═", "╔", "╚", "║"]):
        return "system"
    if any(w in t for w in ["hint:", "tip:"]):
        return "dim"
    return "normal"


def aa_line(surf, col, x1, y1, x2, y2):
    pygame.gfxdraw.line(surf, x1, y1, x2, y2, col)


def aa_rounded_rect(surf, col, rect, radius, alpha=255):
    w, h = rect[2], rect[3]
    tmp = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(tmp, (*col, alpha), (0, 0, w, h), border_radius=radius)
    surf.blit(tmp, (rect[0], rect[1]))


def aa_rounded_border(surf, col, rect, radius, width=2):
    pygame.draw.rect(surf, col, rect, width, border_radius=radius)


def glow_rect(surf, col, rect, radius, layers=4, max_alpha=60):
    for i in range(layers, 0, -1):
        expand = i * 4
        alpha  = int(max_alpha * (1 - i / (layers + 1)))
        glow_r = pygame.Rect(
            rect.x - expand, rect.y - expand,
            rect.w + expand * 2, rect.h + expand * 2
        )
        aa_rounded_rect(surf, col, glow_r, radius + expand, alpha)


class Particle:
    def __init__(self, x, y, color=None):
        self.x    = float(x)
        self.y    = float(y)
        self.vx   = random.uniform(-1.8, 1.8)
        self.vy   = random.uniform(-2.8, -0.4)
        self.life = 1.0
        self.decay = random.uniform(0.022, 0.055)
        self.size  = random.randint(2, 5)
        self.color = color or (random.choice([C_PARTICLE, C_PARTICLE2]))

    def update(self):
        self.x  += self.vx
        self.y  += self.vy
        self.vy += 0.07
        self.life -= self.decay
        return self.life > 0

    def draw(self, surf):
        alpha = int(self.life * 220)
        r = max(1, int(self.size * self.life))
        tmp = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
        pygame.gfxdraw.filled_circle(tmp, r + 1, r + 1, r, (*self.color, alpha))
        pygame.gfxdraw.aacircle(tmp, r + 1, r + 1, r, (*self.color, alpha))
        surf.blit(tmp, (int(self.x) - r - 1, int(self.y) - r - 1))


class EscapePygameGUI:

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Escape Python — The Truth Experiment")

        self.render_surf = pygame.Surface((RWIN_W, RWIN_H), pygame.SRCALPHA)
        self.map_surf    = pygame.Surface((RMAP_W, RWIN_H), pygame.SRCALPHA)
        self.panel_surf  = pygame.Surface((RPANEL_W, RWIN_H), pygame.SRCALPHA)

        self.clock  = pygame.time.Clock()
        self.game   = Game()
        self.visited = {self.game.player.current_room.name}

        self._load_fonts()

        self.output_lines: list[tuple[str, str]] = []
        self.scroll_offset = 0

        self.input_text   = ""
        self.cursor_vis   = True
        self.cursor_timer = 0.0
        self.history      = []
        self.history_pos  = -1

        self.glow_t  = 0.0
        self.conn_t  = 0.0
        self.particles: list[Particle] = []

        self._welcome()

    def _load_fonts(self):
        try:
            self.font_ui    = pygame.font.SysFont("Courier New", 28)
            self.font_ui_b  = pygame.font.SysFont("Courier New", 28, bold=True)
            self.font_small = pygame.font.SysFont("Courier New", 22)
            self.font_map   = pygame.font.SysFont("Courier New", 24, bold=True)
            self.font_title = pygame.font.SysFont("Courier New", 32, bold=True)
            self.font_input = pygame.font.SysFont("Courier New", 30)
            self.font_badge = pygame.font.SysFont("Courier New", 18, bold=True)
            self.font_loc   = pygame.font.SysFont("Courier New", 26, bold=True)
        except Exception:
            mono = pygame.font.get_default_font()
            self.font_ui    = pygame.font.Font(mono, 28)
            self.font_ui_b  = pygame.font.Font(mono, 28)
            self.font_small = pygame.font.Font(mono, 22)
            self.font_map   = pygame.font.Font(mono, 24)
            self.font_title = pygame.font.Font(mono, 32)
            self.font_input = pygame.font.Font(mono, 30)
            self.font_badge = pygame.font.Font(mono, 18)
            self.font_loc   = pygame.font.Font(mono, 26)

    def _print(self, text, tag=None):
        for line in text.split("\n"):
            t = tag if tag else tag_for_line(line)
            self.output_lines.append((line, t))
        if len(self.output_lines) > MAX_OUTPUT_LINES:
            self.output_lines = self.output_lines[-MAX_OUTPUT_LINES:]
        if self.scroll_offset > 0:
            self.scroll_offset = 0

    def _divider(self):
        self._print("─" * 54, "dim")

    def _welcome(self):
        self._print("ESCAPE PYTHON  //  THE TRUTH EXPERIMENT", "accent")
        self._divider()
        self._print("")
        self._print("You slowly regain consciousness.", "dim")
        self._print("Your head hurts.", "dim")
        self._print("You don't remember who you are.", "dim")
        self._print("")
        for line in self.game.player.current_room.description.strip().split("\n"):
            self._print(line, "room")
        self._print("")
        self._print("Type 'help' to see all commands.", "dim")
        self._divider()

    def _submit(self):
        cmd = self.input_text.strip()
        self.input_text  = ""
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
            for _ in range(22):
                self.particles.append(
                    Particle(cx * SCALE + RMAP_W,
                             cy * SCALE,
                             random.choice([C_PARTICLE, C_PARTICLE2, C_ACCENT]))
                )

        self.visited.add(self.game.player.current_room.name)
        self.game.check_endings()

        if not self.game.running:
            tag = ("good"   if self.game.endings.current == "good"   else
                   "bad"    if self.game.endings.current == "bad"    else
                   "system")
            self._print("═" * 54, "accent")
            self._print(self.game.endings.show(), tag)
            self._divider()

    def _draw_map(self):
        ms = self.map_surf
        ms.fill(C_MAP_BG)

        current = self.game.player.current_room.name

        t = self.font_title.render("FACILITY MAP", True, C_ACCENT)
        ms.blit(t, (s(14), s(13)))
        pygame.draw.line(ms, C_BORDER_BRIGHT, (0, s(44)), (RMAP_W, s(44)), s(1))

        for src, dst, vertical in CONNECTIONS:
            self._draw_connection(ms, src, dst, vertical)

        for name in ROOM_POS:
            self._draw_room(ms, name, current)

        legend_y = WIN_H - 185
        pygame.draw.line(ms, C_BORDER, (0, s(legend_y - 10)), (RMAP_W, s(legend_y - 10)), s(1))
        self._draw_legend(ms, legend_y)

        inv_y = legend_y + 32
        pygame.draw.line(ms, C_BORDER, (s(10), s(inv_y - 6)), (RMAP_W - s(10), s(inv_y - 6)), s(1))
        self._draw_inv_ach(ms, inv_y)

    def _draw_connection(self, ms, src, dst, vertical):
        sx, sy = room_center(src)
        dx, dy = room_center(dst)

        ex1, ey1 = self._edge(sx, sy, dx, dy)
        ex2, ey2 = self._edge(dx, dy, sx, sy)

        col = C_CONN_VERT if vertical else C_CONN

        glow_surf = pygame.Surface((RMAP_W, RWIN_H), pygame.SRCALPHA)
        alpha = int(30 + 20 * math.sin(self.conn_t * 2))
        pygame.draw.line(glow_surf, (*C_CONN_GLOW, alpha),
                         s((ex1, ey1)), s((ex2, ey2)), s(6))
        ms.blit(glow_surf, (0, 0))

        if vertical:
            self._dashed_line(ms, col, ex1, ey1, ex2, ey2, s(8), s(2))
        else:
            pygame.draw.line(ms, col, s((ex1, ey1)), s((ex2, ey2)), s(2))
            pygame.gfxdraw.line(ms, *s((ex1, ey1)), *s((ex2, ey2)), (*col, 200))

        self._arrow(ms, col, ex1, ey1, ex2, ey2)

    def _edge(self, cx, cy, tx, ty):
        dx, dy = tx - cx, ty - cy
        if dx == 0 and dy == 0:
            return cx, cy
        hw, hh = ROOM_W / 2, ROOM_H / 2
        sx = (hw / abs(dx)) if dx != 0 else float("inf")
        sy = (hh / abs(dy)) if dy != 0 else float("inf")
        t  = min(sx, sy)
        return cx + dx * t, cy + dy * t

    def _dashed_line(self, surf, col, x1, y1, x2, y2, dash, width):
        dx, dy = x2 - x1, y2 - y1
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return
        steps = int(dist * SCALE / dash)
        if steps == 0:
            return
        for i in range(steps):
            if i % 2 == 0:
                t0 = i / steps
                t1 = (i + 1) / steps
                p0 = (int((x1 + dx * t0) * SCALE), int((y1 + dy * t0) * SCALE))
                p1 = (int((x1 + dx * t1) * SCALE), int((y1 + dy * t1) * SCALE))
                pygame.draw.line(surf, col, p0, p1, width)

    def _arrow(self, surf, col, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        dist   = math.hypot(dx, dy)
        if dist == 0:
            return
        ux, uy = dx / dist, dy / dist
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        sz = 7
        tip = s((mx + ux * sz,      my + uy * sz))
        l   = s((mx - ux * sz - uy * sz, my - uy * sz + ux * sz))
        r   = s((mx - ux * sz + uy * sz, my - uy * sz - ux * sz))
        pygame.gfxdraw.filled_polygon(surf, [tip, l, r], (*col, 220))
        pygame.gfxdraw.aapolygon(surf, [tip, l, r], col)

    def _draw_room(self, ms, name, current):
        rx, ry   = ROOM_POS[name]
        is_cur   = (name == current)
        is_vis   = (name in self.visited)

        fill     = C_ROOM_CURRENT if is_cur  else \
                   C_ROOM_VISITED  if is_vis  else C_ROOM_DEFAULT
        bdr      = C_ROOM_CUR_BDR if is_cur  else C_ROOM_BORDER
        text_c   = C_ROOM_CUR_TEXT if is_cur else \
                   C_ROOM_TEXT      if is_vis else C_ROOM_UNVIS

        rrect    = pygame.Rect(s(rx), s(ry), s(ROOM_W), s(ROOM_H))
        rr       = s(ROOM_R)

        if is_cur:
            pulse = 0.5 + 0.5 * math.sin(self.glow_t * 3.2)
            glow_rect(ms, C_GLOW, rrect, rr,
                      layers=5, max_alpha=int(50 + 35 * pulse))

        aa_rounded_rect(ms, fill, rrect, rr)

        grad = pygame.Surface((s(ROOM_W), s(ROOM_H) // 3), pygame.SRCALPHA)
        grad.fill((255, 255, 255, 18))
        ms.blit(grad, (s(rx), s(ry)))

        aa_rounded_border(ms, bdr, rrect, rr, width=s(2))

        label = ROOM_SHORT[name]
        lsurf = self.font_map.render(label, True, text_c)
        lx    = s(rx) + (s(ROOM_W) - lsurf.get_width()) // 2
        ly    = s(ry) + (s(ROOM_H) - lsurf.get_height()) // 2 - s(5)
        ms.blit(lsurf, (lx, ly))

        bx = s(rx) + s(4)
        by = s(ry) + s(ROOM_H) - s(16)
        room_obj = self.game.rooms[name]

        if room_obj.puzzle:
            done = room_obj.puzzle.solved
            self._badge(ms, "✓" if done else "?",
                        bx, by,
                        C_BADGE_PUZZLE_DONE if done else C_BADGE_PUZZLE)
            bx += s(22)

        if room_obj.items:
            self._badge(ms, f"×{len(room_obj.items)}", bx, by, C_BADGE_ITEM)
            bx += s(28)

        if name in ("Hall", "Server Room"):
            self._badge(ms, "NPC", bx, by, C_BADGE_NPC)

    def _badge(self, surf, text, x, y, color):
        ts   = self.font_badge.render(text, True, C_BADGE_TEXT)
        w, h = ts.get_width() + s(6), ts.get_height() + s(2)
        aa_rounded_rect(surf, color, pygame.Rect(x, y, w, h), s(3))
        surf.blit(ts, (x + s(3), y + s(1)))

    def _draw_legend(self, ms, y):
        items = [
            (C_ROOM_CURRENT, "Current"),
            (C_ROOM_VISITED, "Visited"),
            (C_ROOM_DEFAULT, "Unseen"),
        ]
        x = s(14)
        for col, label in items:
            sq = pygame.Rect(x, s(y + 3), s(11), s(11))
            aa_rounded_rect(ms, col, sq, s(2))
            aa_rounded_border(ms, C_ROOM_BORDER, sq, s(2), width=s(1))
            t = self.font_small.render(label, True, C_TEXT_DIM)
            ms.blit(t, (x + s(15), s(y)))
            x += s(15) + t.get_width() + s(16)

    def _draw_inv_ach(self, ms, y):
        pad = s(14)
        row = s(y)

        lbl = self.font_small.render("INVENTORY", True, C_ACCENT)
        ms.blit(lbl, (pad, row))
        row += lbl.get_height() + s(2)

        inv = self.game.player.inventory
        inv_col = C_TEXT if inv else C_TEXT_DIM
        inv_items = [i.name for i in inv] if inv else ["Empty"]
        max_w = RMAP_W - pad * 2
        line_buf = ""
        for word in inv_items:
            test = (line_buf + "  " + word).strip() if line_buf else word
            if self.font_ui.size(test)[0] > max_w and line_buf:
                ms.blit(self.font_ui.render(line_buf, True, inv_col), (pad, row))
                row += self.font_ui.get_height()
                line_buf = word
            else:
                line_buf = test
        if line_buf:
            ms.blit(self.font_ui.render(line_buf, True, inv_col), (pad, row))
            row += self.font_ui.get_height() + s(8)

        pygame.draw.line(ms, C_BORDER, (pad, row), (RMAP_W - pad, row), s(1))
        row += s(8)

        lbl2 = self.font_small.render("ACHIEVEMENTS", True, C_ACCENT)
        ms.blit(lbl2, (pad, row))
        row += lbl2.get_height() + s(2)

        ach = sorted(self.game.achievements.unlocked)
        if ach:
            for a in ach:
                as_ = self.font_ui.render("✓ " + a, True, C_TEXT_GOOD)
                ms.blit(as_, (pad, row))
                row += as_.get_height() + s(1)
        else:
            ns = self.font_ui.render("None yet", True, C_TEXT_DIM)
            ms.blit(ns, (pad, row))

    def _draw_panel(self):
        ps = self.panel_surf
        ps.fill(C_PANEL_BG)

        ts = self.font_title.render(
            "ESCAPE PYTHON  //  THE TRUTH EXPERIMENT", True, C_ACCENT)
        ps.blit(ts, (s(16), s(11)))
        pygame.draw.line(ps, C_BORDER_BRIGHT, (0, s(40)), (RPANEL_W, s(40)), s(1))

        line_h  = self.font_ui.get_height() + s(2)
        out_top = s(46)
        loc_h   = s(36)
        inp_h   = s(46)
        out_h   = RWIN_H - out_top - loc_h - inp_h
        visible = max(1, out_h // line_h)

        total  = len(self.output_lines)
        start  = max(0, total - visible - self.scroll_offset)
        end    = min(total, start + visible)

        oy = out_top
        for text, tag in self.output_lines[start:end]:
            col  = TAG_COLORS.get(tag, C_TEXT)
            font = self.font_ui_b if tag in ("accent", "system", "good") else self.font_ui
            if text:
                ts2 = font.render(text[:88], True, col)
                ps.blit(ts2, (s(16), oy))
            oy += line_h

        sb_x = RPANEL_W - s(10)
        sb_h = out_h
        aa_rounded_rect(ps, C_BORDER, pygame.Rect(sb_x, out_top, s(6), sb_h), s(3))
        if total > visible:
            th    = max(s(20), int(sb_h * visible / total))
            mo    = total - visible
            ratio = 1.0 - (self.scroll_offset / mo) if mo > 0 else 1.0
            ty    = out_top + int((sb_h - th) * ratio)
            aa_rounded_rect(ps, C_TEXT_DIM, pygame.Rect(sb_x, ty, s(6), th), s(3))

        loc_y = RWIN_H - loc_h - inp_h
        pygame.draw.line(ps, C_BORDER_BRIGHT, (0, loc_y), (RPANEL_W, loc_y), s(1))
        loc_name = self.game.player.current_room.name.upper()
        loc_s = self.font_loc.render(f"  LOCATION: {loc_name}", True, C_ACCENT)
        hint_s = self.font_small.render(
            "  scroll: wheel  |  history: ↑↓  |  clear: ESC", True, C_TEXT_DIM)
        ps.blit(loc_s,  (0,  loc_y + s(8)))
        ps.blit(hint_s, (loc_s.get_width(), loc_y + s(10)))

        inp_y = RWIN_H - inp_h
        pygame.draw.line(ps, C_BORDER_BRIGHT, (0, inp_y), (RPANEL_W, inp_y), s(1))
        aa_rounded_rect(ps, C_INPUT_BG, pygame.Rect(0, inp_y, RPANEL_W, inp_h), 0)

        pr = self.font_input.render(">", True, C_ACCENT)
        ps.blit(pr, (s(12), inp_y + s(11)))

        it = self.font_input.render(self.input_text, True, C_TEXT)
        ps.blit(it, (s(34), inp_y + s(11)))

        if self.cursor_vis:
            cx = s(34) + self.font_input.size(self.input_text)[0]
            pygame.draw.rect(ps, C_CURSOR,
                             pygame.Rect(cx, inp_y + s(12), s(2), s(20)))

    def _update_particles(self):
        self.particles = [p for p in self.particles if p.update()]

    def _draw_particles(self, surf):
        for p in self.particles:
            p.draw(surf)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.glow_t      += dt
            self.conn_t      += dt
            self.cursor_timer += dt
            if self.cursor_timer > 0.52:
                self.cursor_vis   = not self.cursor_vis
                self.cursor_timer = 0.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event)
                elif event.type == pygame.MOUSEWHEEL:
                    line_h  = self.font_ui.get_height() + s(2)
                    out_h   = RWIN_H - s(46) - s(36) - s(46)
                    visible = max(1, out_h // line_h)
                    total   = len(self.output_lines)
                    max_off = max(0, total - visible)
                    self.scroll_offset = max(
                        0, min(max_off, self.scroll_offset - event.y)
                    )
                elif event.type == pygame.TEXTINPUT:
                    if len(self.input_text) < INPUT_MAX:
                        self.input_text += event.text

            self._update_particles()

            self._draw_map()
            self._draw_panel()
            self._draw_particles(self.map_surf)

            self.render_surf.fill(C_BG)
            self.render_surf.blit(self.map_surf,   (0, 0))
            self.render_surf.blit(self.panel_surf, (RMAP_W, 0))
            pygame.draw.line(self.render_surf, C_BORDER_BRIGHT,
                             (RMAP_W, 0), (RMAP_W, RWIN_H), s(1))

            scaled = pygame.transform.smoothscale(self.render_surf, (WIN_W, WIN_H))
            self.screen.blit(scaled, (0, 0))
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
            line_h  = self.font_ui.get_height() + s(2)
            out_h   = RWIN_H - s(46) - s(36) - s(46)
            visible = max(1, out_h // line_h)
            total   = len(self.output_lines)
            max_off = max(0, total - visible)
            self.scroll_offset = min(max_off, self.scroll_offset + visible // 2)
        elif event.key == pygame.K_PAGEDOWN:
            self.scroll_offset = max(0, self.scroll_offset - 5)


def main():
    gui = EscapePygameGUI()
    gui.run()


if __name__ == "__main__":
    main()