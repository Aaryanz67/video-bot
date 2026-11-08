import cairo, math, os, subprocess, sys
import numpy as np

W, H, FPS = 1080, 1920, 30

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def prog(t, t0, t1): return clamp((t - t0) / (t1 - t0))
def e_out(x): return 1 - (1 - x) ** 3
def e_io(x): return 3 * x * x - 2 * x ** 3
def lerp(a, b, k): return a + (b - a) * k

def new_ctx():
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(s)
    c.set_antialias(cairo.ANTIALIAS_BEST)
    return s, c

def text_center(c, lines, cx, y, size, family, bold, rgb, alpha=1.0, lh=1.25):
    c.select_font_face(family, cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    for i, ln in enumerate(lines):
        if not ln: continue
        ext = c.text_extents(ln)
        c.set_source_rgba(*rgb, alpha)
        c.move_to(cx - ext.width / 2 - ext.x_bearing, y + i * size * lh)
        c.show_text(ln)

# ---------------- Scene A: minimalistic ----------------
def scene_a(t):
    s, c = new_ctx()
    c.set_source_rgb(0, 0, 0); c.paint()
    lines = ["keep going.", "it adds up."]
    total = sum(len(l) for l in lines)
    n = int(prog(t, 0.3, 2.4) * total)
    shown = []
    for l in lines:
        shown.append(l[:max(0, min(len(l), n))]); n -= len(l)
    text_center(c, shown, W / 2, 330, 72, "Inter", False, (1, 1, 1))
    bw, gap, base = 130, 40, 1520
    left = (W - (5 * bw + 4 * gap)) / 2
    hts = [220, 380, 540, 700, 860]
    c.set_line_width(4); c.set_line_join(cairo.LINE_JOIN_MITER)
    tops = []
    for i, h in enumerate(hts):
        k = e_out(prog(t, 0.5 + i * 0.35, 1.2 + i * 0.35))
        x = left + i * (bw + gap)
        hh = h * k
        if hh > 1:
            c.set_source_rgb(1, 1, 1)
            c.rectangle(x, base - hh, bw, hh); c.stroke()
        tops.append((x + bw / 2, base - h))
    # dot
    R = 26
    if t > 2.5:
        sc = e_out(prog(t, 2.5, 3.0))
        pos = tops[0]; px, py = pos[0], pos[1] - R - 3
        for i in range(4):
            h0 = 3.2 + i * 0.9
            k = prog(t, h0, h0 + 0.6)
            if k > 0:
                a = (tops[i][0], tops[i][1] - R - 3); b = (tops[i + 1][0], tops[i + 1][1] - R - 3)
                kk = e_io(k)
                px = lerp(a[0], b[0], kk)
                py = lerp(a[1], b[1], kk) - 110 * math.sin(math.pi * k)
        c.set_source_rgb(1, 1, 1)
        c.arc(px, py, R * sc, 0, 2 * math.pi); c.fill()
    return s

# ---------------- Scene B: stick figure ----------------
BG_B = (0.953, 0.933, 0.894); INK = (0.10, 0.10, 0.10)
GROUND = 1330

def stick(c, x, theta, sw, arm1, arm2):
    S = 1.35
    L, T, HR = 170 * S, 190 * S, 38
    hip_h = L * math.cos(sw)
    st, ct = math.sin(theta), math.cos(theta)
    lift = 9 * st
    def tr(px, py):
        return (x + px * ct + py * st, GROUND - lift - (-px * st + py * ct))
    c.set_line_width(14); c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_source_rgb(*INK)
    H0 = (0, hip_h); S0 = (0, hip_h + T)
    def line(a, b):
        A, B = tr(*a), tr(*b); c.move_to(*A); c.line_to(*B); c.stroke()
    line(H0, S0)
    for sgn in (1, -1):
        a = sgn * sw
        line(H0, (L * math.sin(a), hip_h - L * math.cos(a)))
    AL = 125 * S
    for ang in (arm1, arm2):
        line(S0, (AL * math.sin(ang), S0[1] - AL * math.cos(ang)))
    sx, sy = tr(*S0)
    th = theta * 0.55
    d = HR + 14
    hx, hy = sx + d * math.sin(th), sy - d * math.cos(th)
    c.set_source_rgb(*BG_B); c.arc(hx, hy, HR, 0, 2 * math.pi); c.fill_preserve()
    c.set_source_rgb(*INK); c.stroke()

def scene_b(t):
    s, c = new_ctx()
    c.set_source_rgb(*BG_B); c.paint()
    A = 0.55; f = 2 * math.pi * 1.4
    if t < 2.6:
        x = 60 + 120 * t; sw = A * math.sin(f * t); th = 0
        a1, a2 = -0.6 * sw, 0.6 * sw
    elif t < 3.3:
        k = prog(t, 2.6, 3.3)
        x = 60 + 120 * 2.6 + 60 * e_out(k)
        sw = A * math.sin(f * 2.6) * (1 - k); th = (math.pi / 2) * (k ** 2)
        a1 = lerp(0.3, 2.1, e_out(k)); a2 = a1 + 0.4
    elif t < 4.5:
        x = 60 + 120 * 2.6 + 60; sw = 0; th = math.pi / 2
        k = prog(t, 3.3, 3.8); a1 = lerp(2.1, 0.4, e_out(k)); a2 = a1 + 0.5
    elif t < 5.4:
        k = prog(t, 4.5, 5.4)
        x = 60 + 120 * 2.6 + 60; sw = 0; th = (math.pi / 2) * (1 - e_io(k))
        a1 = lerp(0.4, 0.2, k); a2 = a1 + 0.5
    else:
        tt = t - 5.4
        w = e_out(prog(t, 5.4, 5.9))
        x = 60 + 120 * 2.6 + 60 + 120 * tt
        sw = A * math.sin(f * tt) * w; th = 0
        a1, a2 = -0.6 * sw, 0.6 * sw
    # ground
    c.set_source_rgb(*INK); c.set_line_width(6); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(60, GROUND + 4); c.line_to(W - 60, GROUND + 4); c.stroke()
    stick(c, x, th, sw, a1, a2)
    text_center(c, ["fall down", "seven times."], W / 2, 330, 96, "Poppins", True, INK, e_out(prog(t, 3.0, 3.7)), 1.2)
    text_center(c, ["get up eight."], W / 2, 640, 96, "Poppins", True, (0.85, 0.33, 0.12), e_out(prog(t, 5.4, 6.1)))
    return s

# ---------------- Scene C: dot matrix sun ----------------
COLS = 54
SP = W / COLS
ROWS = int(H / SP) + 1
gx = (np.arange(COLS) + 0.5) * SP
gy = (np.arange(ROWS) + 0.5) * SP
GX, GY = np.meshgrid(gx, gy)
U, V = GX / W, GY / H

def scene_c(t):
    s, c = new_ctx()
    c.set_source_rgb(0.055, 0.05, 0.045); c.paint()
    rise = e_io(prog(t, 0.3, 6.5))
    cy = lerp(1.12, 0.50, rise) * H
    cx = W / 2
    Rr = 260
    d = np.hypot(GX - cx, GY - cy)
    b = np.clip(1 - (d - Rr) / 40, 0, 1)
    b = np.maximum(b, 0.38 * np.exp(-np.clip(d - Rr, 0, None) / 160))
    ridge_back = 0.74 + 0.05 * np.sin(U * 7 + 0.6) + 0.03 * np.sin(U * 17 + 1)
    ridge_front = 0.83 + 0.04 * np.sin(U * 9 + 2.2) + 0.03 * np.sin(U * 23)
    b = np.where(V > ridge_back, 0.20 + 0.06 * (V - 0.74) * 10, b)
    b = np.where(V > ridge_front, 0.05, b)
    b = np.clip(b + 0.015 * np.sin(t * 3 + U * 20), 0, 1)
    rad = 1.3 + (SP * 0.48 - 1.3) * np.sqrt(b)
    for r in range(ROWS):
        for col in range(COLS):
            bb = b[r, col]
            k = float(bb)
            c.set_source_rgb(lerp(0.45, 1.0, k), lerp(0.2, 0.62, k), lerp(0.1, 0.30, k))
            c.arc(GX[r, col], GY[r, col], float(rad[r, col]), 0, 2 * math.pi); c.fill()
    # text, with a soft dark band behind for legibility
    a = e_out(prog(t, 4.2, 5.2))
    if a > 0:
        text_center(c, ["start before", "you feel ready."], W / 2, 270, 84, "Poppins", True, (1, 1, 1), a, 1.2)
    return s

SCENES = {"a_minimal": (scene_a, 8.0), "b_stickman": (scene_b, 9.0), "c_dots": (scene_c, 8.0)}

def surf_bytes(s):
    s.flush(); return bytes(s.get_data())

def render(name, fn, dur):
    out = f"out/{name}.mp4"; tmp = f"out/{name}.part.mp4"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                          "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(int(dur * FPS)):
        p.stdin.write(surf_bytes(fn(i / FPS)))
    p.stdin.close()
    if p.wait() == 0: os.rename(tmp, out)
    else: sys.exit("ffmpeg failed " + name)

if __name__ == "__main__":
    os.makedirs("out", exist_ok=True)
    if sys.argv[1] == "preview":
        os.makedirs("/home/claude/prev", exist_ok=True)
        times = {"a_minimal": [], "b_stickman": [3.0, 3.9, 4.9, 8.9], "c_dots": [2.0, 4.5, 6.5, 7.8]}
        for n, (fn, d) in SCENES.items():
            for t in times[n]:
                fn(t).write_to_png(f"/home/claude/prev/{n}_{t}.png")
    else:
        for n, (fn, d) in SCENES.items():
            if len(sys.argv) > 2 and n not in sys.argv[2:]: continue
            render(n, fn, d)
