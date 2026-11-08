import math, os, sys, cairo
import numpy as np
from make_videos import (W, H, FPS, clamp, prog, e_out, e_io, lerp, new_ctx, text_center,
                         stick, BG_B, INK, GROUND, render, scene_c as _unused)
import make_videos as mv

# ---------- A: zoom-out staircase ----------
N = 10; PITCH = 90; BW = 72
def bar_h(i): return 70 + i * 80
def bar_cx(i): return i * PITCH + BW / 2
HOP0, HOPD, HOPG = 0.9, 0.4, 0.5       # first hop start, hop duration, hop spacing
def hop_start(k): return HOP0 + k * HOPG

def scene_a2(t):
    s, c = new_ctx()
    c.set_source_rgb(0, 0, 0); c.paint()
    R = 22
    # dot world position
    def top(i): return (bar_cx(i), -bar_h(i) - R - 3)
    pos = top(0)
    for k in range(N - 1):
        kk = prog(t, hop_start(k), hop_start(k) + HOPD)
        if kk > 0:
            a, b = top(k), top(k + 1)
            e = e_io(kk)
            pos = (lerp(a[0], b[0], e), lerp(a[1], b[1], e) - 70 * math.sin(math.pi * kk))
    zoom_k = e_io(prog(t, 5.6, 7.6))
    Z = lerp(2.4, 1.0, zoom_k)
    cx = lerp(pos[0], 450, zoom_k); cy = lerp(pos[1], -395, zoom_k)
    def S(wx, wy): return (540 + (wx - cx) * Z, 1130 + (wy - cy) * Z)
    c.set_line_width(4); c.set_source_rgb(1, 1, 1)
    for i in range(N):
        start = 0.15 if i == 0 else hop_start(i - 1) - 0.15
        k = e_out(prog(t, start, start + 0.3))
        if k <= 0: continue
        h = bar_h(i) * k
        x0, y0 = S(i * PITCH, -h)
        c.rectangle(x0, y0, BW * Z, h * Z); c.stroke()
    px, py = S(*pos)
    pulse = 1 + 0.25 * math.sin(math.pi * prog(t, 7.6, 8.2)) if t > 7.6 else 1
    c.arc(px, py, R * Z * pulse if Z < 1.2 else R * Z, 0, 2 * math.pi); c.fill()
    # text (screen space)
    l1, l2 = LINE_A
    n1 = int(prog(t, 0.2, 1.3) * len(l1)); n2 = int(prog(t, 5.6, 6.6) * len(l2))
    text_center(c, [l1[:n1], l2[:n2]], W / 2, 300, 72, "Inter", False, (1, 1, 1))
    return s

# ---------- B: seven falls ----------
CYC = [1.8, 1.5, 1.2, 1.0, 0.85, 0.75, 0.7]
FR = (0.30, 0.20, 0.20, 0.30)  # walk, trip, lie, getup
WALK_V = 120; FIGX = 230
A_SW = 0.55; F = 2 * math.pi * 1.4
T_END = sum(CYC)

def state_b(t):
    scroll = 0.0; t0 = 0.0; count = 0
    for D in CYC:
        w, tr, li, up = [D * f for f in FR]
        if t < t0 + D:
            lt = t - t0
            if lt < w:
                sw = A_SW * math.sin(F * lt) * e_out(prog(lt, 0, 0.12))
                return 0, sw, -0.6 * sw, 0.6 * sw, scroll + WALK_V * lt, count
            lt -= w; scroll += WALK_V * w; count += 1
            if lt < tr:
                k = lt / tr
                sw0 = A_SW * math.sin(F * w)
                a1 = lerp(0.3, 2.1, e_out(k))
                return (math.pi / 2) * k ** 2, sw0 * (1 - k), a1, a1 + 0.4, scroll + 40 * e_out(k), count
            lt -= tr; scroll += 40
            if lt < li:
                k = prog(lt, 0, li * 0.7)
                a1 = lerp(2.1, 0.4, e_out(k))
                return math.pi / 2, 0, a1, a1 + 0.5, scroll, count
            lt -= li
            k = lt / up
            return (math.pi / 2) * (1 - e_io(k)), 0, lerp(0.4, 0.2, k), lerp(0.9, 0.7, k), scroll, count
        scroll += WALK_V * w + 40; t0 += D; count += 1
    lt = t - T_END
    sw = A_SW * math.sin(F * lt) * e_out(prog(lt, 0, 0.2))
    return 0, sw, -0.6 * sw, 0.6 * sw, scroll + WALK_V * lt, 7

def scene_b2(t):
    s, c = new_ctx()
    c.set_source_rgb(*BG_B); c.paint()
    th, sw, a1, a2, scroll, count = state_b(t)
    # ground + scrolling ticks
    c.set_source_rgb(*INK); c.set_line_width(6); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(0, GROUND + 4); c.line_to(W, GROUND + 4); c.stroke()
    c.set_line_width(5)
    off = scroll % 160
    for k in range(-1, 8):
        x = k * 160 - off
        c.move_to(x, GROUND + 30); c.line_to(x + 36, GROUND + 30); c.stroke()
    stick(c, FIGX, th, sw, a1, a2)
    text_center(c, ["fall down", "seven times."], W / 2, 330, 96, "Poppins", True, INK, e_out(prog(t, 0.2, 0.7)), 1.2)
    if t < T_END + 0.2:
        shown = max(count, 0)
        if shown:
            text_center(c, [f"{shown}/7"], W / 2, 700, 130, "Poppins", True, (0.85, 0.33, 0.12))
    else:
        text_center(c, ["get up eight."], W / 2, 640, 96, "Poppins", True, (0.85, 0.33, 0.12), e_out(prog(t, T_END + 0.2, T_END + 0.8)))
    return s

# ---------- C: sun quote that matches ----------
_orig_text = mv.text_center
def scene_c2(t):
    # reuse sun field from v1, but draw our own text afterwards
    mv.text_center = lambda *a, **k: None
    s = mv.scene_c(t)
    mv.text_center = _orig_text
    c = cairo.Context(s)
    sz = min(80, 940 / (0.62 * max(len(LINE_C[0]), len(LINE_C[1]), 1)))
    text_center(c, [LINE_C[0]], W / 2, 270, sz, "Poppins", True, (1, 1, 1), e_out(prog(t, 1.2, 2.2)))
    text_center(c, [LINE_C[1]], W / 2, 270 + sz * 1.2, sz, "Poppins", True, (1, 0.72, 0.4), e_out(prog(t, 3.4, 4.4)))
    return s

LINE_A = ["keep going.", "it adds up."]
LINE_C = ["the sun doesn't wait", "to feel ready."]

SCENES2 = {"a2": (scene_a2, 9.5), "b2": (scene_b2, T_END + 2.0), "c2": (scene_c2, 8.0)}

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    if sys.argv[1] == "preview":
        os.makedirs("/home/claude/prev2", exist_ok=True)
        pt = {"a2": [1.0, 3.0, 5.0, 6.3, 7.0, 9.0],
              "b2": [0.4, 1.2, 1.9, 3.0, 4.6, 6.2, 7.6, T_END + 1.6],
              "c2": [2.0, 5.0]}
        for n, (fn, d) in SCENES2.items():
            for t in pt[n]:
                fn(t).write_to_png(f"/home/claude/prev2/{n}_{t:.1f}.png")
    else:
        for n, (fn, d) in SCENES2.items():
            render(n, fn, d)
