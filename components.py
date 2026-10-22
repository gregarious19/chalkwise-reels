"""Chalkwise reel component library.

A spec event {"type": "use", "component": "<name>", "t": <start>, ...args} expands into
ordinary render events before rendering. Components are the basics most reels need; when a
script needs something new, add a component here (generic, documented in LIBRARY.md) rather
than hand-placing dozens of raw events in the spec.

Every component takes "t" (start time, seconds). Positions are canvas pixels (1080 x 1920).
"""
import math

W, H = 1080, 1920
SAFE_X0, SAFE_X1 = 60, 1000          # board content stays inside these
CAPTION_Y = 330

# Reading pace (founder feedback 2026-10-22: reels felt too fast to read and follow).
READ_S_PER_WORD = 0.55   # caption hold per word
MIN_CAPTION_S = 2.5      # no caption shorter than this
WRITE_S_PER_CHAR = 0.09  # handwriting speed
BEAT_REST_S = 1.2        # pause after a drawing finishes before the next beat

def caption_hold(text):
    """Seconds a caption must stay up to be read comfortably (numbers take longer)."""
    words = len(text.split())
    digits = sum(ch.isdigit() for ch in text)
    return max(MIN_CAPTION_S, READ_S_PER_WORD * words + 0.12 * digits)

def write_dur(text):
    return min(3.0, max(0.5, WRITE_S_PER_CHAR * len(text)))


# ---------------------------------------------------------------- helpers
def arc(cx, cy, r, a0, a1, n=28, ry=None):
    """Points along an arc, angles in degrees (0 = right, 90 = down)."""
    ry = r if ry is None else ry
    return [[cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / (n - 1))),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / (n - 1)))] for i in range(n)]

def rrect(x0, y0, x1, y1, r):
    """Rounded rectangle outline as one closed polyline."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    pts = []
    pts += arc(x1 - r, y0 + r, r, -90, 0, 8)
    pts += arc(x1 - r, y1 - r, r, 0, 90, 8)
    pts += arc(x0 + r, y1 - r, r, 90, 180, 8)
    pts += arc(x0 + r, y0 + r, r, 180, 270, 8)
    pts.append(pts[0])
    return pts

def _scale(strokes, cx, cy, s):
    out = []
    for st in strokes:
        kind = st[0]
        if kind == "line":
            out.append(("line", [[cx + x * s, cy + y * s] for x, y in st[1]]))
        elif kind == "dot":
            out.append(("dot", [cx + st[1][0] * s, cy + st[1][1] * s], st[2] * s))
    return out


# ---------------------------------------------------------------- icons
# Unit box: x, y in [-1, 1], y pointing down. ("line", points) or ("dot", [x, y], radius).
def _icons():
    I = {}
    I["lightbulb"] = [("line", arc(0, -0.25, 0.6, 130, 410)),
                      ("line", [[-0.28, 0.28], [-0.25, 0.55], [0.25, 0.55], [0.28, 0.28]]),
                      ("line", [[-0.22, 0.72], [0.22, 0.72]]), ("line", [[-0.14, 0.88], [0.14, 0.88]]),
                      ("line", [[-0.12, 0.25], [0, -0.05], [0.12, 0.25]])]
    I["brain"] = [("line", arc(-0.32, -0.05, 0.55, 90, 270, ry=0.7)),
                  ("line", arc(0.32, -0.05, 0.55, -90, 90, ry=0.7)),
                  ("line", [[-0.32, -0.75], [0.32, -0.75]]), ("line", [[-0.32, 0.65], [0.32, 0.65]]),
                  ("line", [[0, -0.75], [0.04, -0.4], [-0.04, 0], [0.04, 0.35], [0, 0.65]]),
                  ("line", arc(-0.45, -0.2, 0.22, -60, 120)), ("line", arc(0.45, 0.2, 0.22, 120, 300))]
    I["phone"] = [("line", rrect(-0.5, -0.95, 0.5, 0.95, 0.15)), ("line", [[-0.15, -0.8], [0.15, -0.8]]),
                  ("dot", [0, 0.78], 0.07)]
    I["coin"] = [("line", arc(0, 0, 0.85, -90, 275)), ("line", arc(0, 0, 0.62, -90, 275)),
                 ("line", [[-0.25, -0.3], [0.25, -0.3]]), ("line", [[-0.25, -0.1], [0.25, -0.1]]),
                 ("line", [[-0.1, -0.3], [0.12, -0.25], [0.12, -0.05], [-0.15, 0.0], [0.2, 0.4]])]
    I["clock"] = [("line", arc(0, 0, 0.85, -90, 275)), ("line", [[0, 0], [0, -0.55]]),
                  ("line", [[0, 0], [0.4, 0.2]]), ("dot", [0, 0], 0.07)]
    I["book"] = [("line", [[0, -0.55], [-0.4, -0.7], [-0.9, -0.6], [-0.9, 0.6], [-0.4, 0.5], [0, 0.65]]),
                 ("line", [[0, -0.55], [0.4, -0.7], [0.9, -0.6], [0.9, 0.6], [0.4, 0.5], [0, 0.65]]),
                 ("line", [[0, -0.55], [0, 0.65]])]
    I["stack"] = [("line", rrect(-0.85, 0.35, 0.85, 0.75, 0.06)), ("line", rrect(-0.7, -0.05, 0.75, 0.35, 0.06)),
                  ("line", rrect(-0.8, -0.45, 0.7, -0.05, 0.06)), ("line", rrect(-0.6, -0.85, 0.6, -0.45, 0.06))]
    I["question"] = [("line", arc(0, -0.35, 0.45, 190, 405)[:-4] + [[0.05, 0.05], [0, 0.35]]),
                     ("dot", [0, 0.72], 0.1)]
    I["check"] = [("line", [[-0.75, 0.05], [-0.25, 0.55], [0.8, -0.6]])]
    I["cross"] = [("line", [[-0.65, -0.65], [0.65, 0.65]]), ("line", [[0.65, -0.65], [-0.65, 0.65]])]
    star = []
    for k in range(11):
        r = 0.95 if k % 2 == 0 else 0.4
        a = math.radians(-90 + 36 * k)
        star.append([r * math.cos(a), r * math.sin(a) + 0.05])
    I["star"] = [("line", star)]
    I["heart"] = [("line", arc(-0.4, -0.25, 0.42, 160, 360) + arc(0.4, -0.25, 0.42, 180, 380) + [[0, 0.85]] +
                   [[-0.8, -0.12]])]
    I["magnifier"] = [("line", arc(-0.2, -0.2, 0.55, -90, 275)), ("line", [[0.2, 0.2], [0.85, 0.85]])]
    I["battery"] = [("line", rrect(-0.9, -0.45, 0.75, 0.45, 0.08)), ("line", [[0.78, -0.18], [0.92, -0.18], [0.92, 0.18], [0.78, 0.18]]),
                    ("line", [[-0.75, -0.28], [-0.75, 0.28], [-0.45, 0.28], [-0.45, -0.28], [-0.75, -0.28]])]
    I["dice"] = [("line", rrect(-0.8, -0.8, 0.8, 0.8, 0.15)), ("dot", [-0.4, -0.4], 0.11), ("dot", [0, 0], 0.11),
                 ("dot", [0.4, 0.4], 0.11)]
    I["cap"] = [("line", [[-1, -0.25], [0, -0.7], [1, -0.25], [0, 0.2], [-1, -0.25]]),
                ("line", [[-0.55, 0.0], [-0.55, 0.45], [0, 0.65], [0.55, 0.45], [0.55, 0.0]]),
                ("line", [[0.85, -0.2], [0.85, 0.45]])]
    I["chai"] = [("line", [[-0.65, -0.3], [-0.55, 0.65], [0.35, 0.65], [0.45, -0.3], [-0.65, -0.3]]),
                 ("line", arc(0.5, 0.15, 0.25, -80, 90)),
                 ("line", [[-0.3, -0.5], [-0.2, -0.65], [-0.3, -0.8], [-0.2, -0.95]]),
                 ("line", [[0.05, -0.5], [0.15, -0.65], [0.05, -0.8], [0.15, -0.95]])]
    I["trend_up"] = [("line", [[-0.9, -0.9], [-0.9, 0.85], [0.9, 0.85]]),
                     ("line", [[-0.7, 0.5], [-0.3, 0.1], [0.05, 0.3], [0.65, -0.45]]),
                     ("line", [[0.35, -0.45], [0.65, -0.45], [0.65, -0.15]])]
    I["target"] = [("line", arc(0, 0, 0.9, -90, 275)), ("line", arc(0, 0, 0.58, -90, 275)),
                   ("dot", [0, 0], 0.2)]
    I["lock"] = [("line", rrect(-0.65, -0.1, 0.65, 0.85, 0.1)), ("line", arc(0, -0.1, 0.42, 180, 360)),
                 ("dot", [0, 0.35], 0.1)]
    I["play"] = [("line", arc(0, 0, 0.9, -90, 275)), ("line", [[-0.25, -0.4], [0.45, 0], [-0.25, 0.4], [-0.25, -0.4]])]
    I["warning"] = [("line", [[0, -0.85], [0.9, 0.75], [-0.9, 0.75], [0, -0.85]]), ("line", [[0, -0.3], [0, 0.25]]),
                    ("dot", [0, 0.5], 0.08)]
    I["chat"] = [("line", rrect(-0.9, -0.7, 0.9, 0.45, 0.2)), ("line", [[-0.4, 0.45], [-0.55, 0.85], [-0.05, 0.45]]),
                 ("dot", [-0.4, -0.12], 0.08), ("dot", [0, -0.12], 0.08), ("dot", [0.4, -0.12], 0.08)]
    I["bolt"] = [("line", [[0.15, -0.95], [-0.45, 0.1], [0.05, 0.1], [-0.15, 0.95], [0.5, -0.15], [0.0, -0.15], [0.15, -0.95]])]
    I["calendar"] = [("line", rrect(-0.85, -0.65, 0.85, 0.85, 0.1)), ("line", [[-0.85, -0.25], [0.85, -0.25]]),
                     ("line", [[-0.4, -0.85], [-0.4, -0.5]]), ("line", [[0.4, -0.85], [0.4, -0.5]]),
                     ("line", [[-0.5, 0.25], [-0.2, 0.55], [0.45, -0.05]])]
    return I

ICONS = _icons()


def c_icon(a):
    """Hand-drawn icon. args: name, at [x,y] (centre), size (half-width px, default 70), color, w, d."""
    name = a["name"]
    if name not in ICONS:
        raise ValueError(f"unknown icon {name!r}; available: {', '.join(sorted(ICONS))}")
    strokes = _scale(ICONS[name], a["at"][0], a["at"][1], a.get("size", 70))
    d = a.get("d", 1.4)
    step = d / max(len(strokes), 1)
    ev = []
    for k, st in enumerate(strokes):
        t = a["t"] + k * step
        if st[0] == "line":
            ev.append({"type": "polyline", "t": t, "d": step * 1.05, "points": st[1], "color": a.get("color", "ink"),
                       "w": a.get("w", 7), "wobble": a.get("wobble", 1.4)})
        else:
            ev.append({"type": "dot", "t": t, "d": 0.2, "c": st[1], "r": max(st[2], 5), "color": a.get("color", "ink")})
    return ev


def c_person(a):
    """Stick figure with optional name. args: at [x,y] (feet centre), size (height px, default 260), color, label, label_color, mood ('happy'|'sad'|'neutral')."""
    x, y = a["at"]
    h = a.get("size", 260)
    col = a.get("color", "ink")
    hr = h * 0.13
    hy = y - h + hr
    t = a["t"]
    mood = a.get("mood", "happy")
    mouth = {"happy": arc(x, hy + hr * 0.05, hr * 0.5, 25, 155, 10),
             "sad": arc(x, hy + hr * 0.75, hr * 0.5, 205, 335, 10),
             "neutral": [[x - hr * 0.35, hy + hr * 0.45], [x + hr * 0.35, hy + hr * 0.45]]}[mood]
    ev = [{"type": "circle", "t": t, "d": 0.4, "c": [x, hy], "r": hr, "color": col, "w": 7},
          {"type": "dot", "t": t + 0.35, "c": [x - hr * 0.35, hy - hr * 0.15], "r": 5, "color": col},
          {"type": "dot", "t": t + 0.38, "c": [x + hr * 0.35, hy - hr * 0.15], "r": 5, "color": col},
          {"type": "polyline", "t": t + 0.4, "d": 0.2, "points": mouth, "color": col, "w": 5},
          {"type": "line", "t": t + 0.55, "d": 0.3, "points": [[x, hy + hr], [x, y - h * 0.38]], "color": col, "w": 7},
          {"type": "polyline", "t": t + 0.8, "d": 0.3, "points": [[x - h * 0.2, y - h * 0.48], [x, y - h * 0.62], [x + h * 0.2, y - h * 0.48]], "color": col, "w": 7},
          {"type": "polyline", "t": t + 1.05, "d": 0.3, "points": [[x - h * 0.16, y], [x, y - h * 0.38], [x + h * 0.16, y]], "color": col, "w": 7}]
    if a.get("label"):
        ev.append({"type": "write", "t": t + 1.3, "text": a["label"], "x": x, "y": y + 50, "size": a.get("label_size", 50),
                   "align": "center", "color": a.get("label_color", col)})
    return ev


# ---------------------------------------------------------------- scenes
def c_hook(a):
    """Opening card (a brief's top-level "hook", not a show item). args: text (caption, max ~7 words), highlight,
    sub (smaller grey line), until (default: long enough to read, min 3.5 s),
    big (large handwritten word or symbol in the middle), big_color, big_size, circle (bool, default true),
    icon (icon name instead of big), clear (bool, default true: wipe board at until)."""
    t, until = a["t"], a.get("until", a["t"] + max(3.5, caption_hold(a["text"]) + 1.0))
    # d=0.05: the hook text is on screen from the very first frame (that frame shows while the reel loads)
    ev = [{"type": "caption", "t": t, "d": 0.05, "text": a["text"], "highlight": a.get("highlight", []), "y": CAPTION_Y,
           "size": a.get("size", 80), "until": until}]
    if a.get("sub"):
        ev.append({"type": "caption", "t": t + 0.8, "text": a["sub"], "y": CAPTION_Y + 160, "size": 52,
                   "color": "#6b6b6b", "until": until})
    if a.get("big"):
        ev.append({"type": "write", "t": t + 0.3, "text": a["big"], "x": W / 2, "y": 960, "size": a.get("big_size", 190),
                   "align": "center", "color": a.get("big_color", "ink"), "d": a.get("big_d", 1.4)})
    if a.get("icon"):
        ev += c_icon({"t": t + 0.3, "name": a["icon"], "at": [W / 2, 960], "size": 180, "color": a.get("big_color", "ink"), "w": 10})
    if a.get("circle", True) and (a.get("big") or a.get("icon")):
        rx = 260
        if a.get("big"):  # fit the loop around the text (handwriting is ~0.5 x size per character)
            rx = max(260, min(500, len(a["big"]) * a.get("big_size", 190) * 0.27 + 80))
        ev.append({"type": "ellipse", "t": t + 1.6, "d": 0.8, "c": [W / 2, 960], "rx": rx, "ry": min(260, rx),
                   "color": "orange", "w": 9})
        ev.append({"type": "sfx", "t": t + 1.6, "name": "whoosh"})
    if a.get("clear", True):
        ev.append({"type": "clear", "t": until + 0.05})
    return ev


def c_outro(a):
    """Brand card (a brief's top-level "outro"; make.py adds it and its timing automatically), the last ~10 s. args: until (reel end), line1 (default
    'no courses. no syllabus.'), line2 (default 'just ask. it draws + explains.'), caption, highlight,
    caption2, highlight2, cta (pill text), clear (bool, default true)."""
    t = a["t"]
    until = a["until"]
    ev = []
    if a.get("clear", True):
        ev.append({"type": "clear", "t": t - 0.45})
    l1 = a.get("line1", "no courses. no syllabus.")
    l2 = a.get("line2", "just ask. it draws + explains.")
    ev += [{"type": "caption", "t": t, "text": a.get("caption", "That's how Chalkwise teaches."),
            "highlight": a.get("highlight", ["Chalkwise"]), "y": CAPTION_Y, "size": 72, "until": t + 4.3},
           {"type": "write", "t": t + 0.1, "text": "chalkwise", "x": W / 2, "y": 820, "size": 140, "align": "center", "d": 1.5},
           {"type": "underline", "t": t + 1.8, "d": 0.5, "x0": 230, "x1": 850, "y": 920, "color": "orange", "w": 9},
           {"type": "sfx", "t": t + 1.8, "name": "ding"},
           {"type": "write", "t": t + 2.6, "text": l1, "x": W / 2, "y": 1030, "size": 54, "align": "center", "d": write_dur(l1)},
           {"type": "write", "t": t + 4.6, "text": l2, "x": W / 2, "y": 1120, "size": 54, "align": "center", "color": "blue",
            "d": write_dur(l2)},
           {"type": "caption", "t": t + 4.4, "text": a.get("caption2", "Learn anything. We build the basics on the way."),
            "highlight": a.get("highlight2", ["anything"]), "y": CAPTION_Y + 20, "size": 60, "until": until},
           {"type": "caption", "t": min(t + 6.4, until - 3.5), "text": a.get("cta", "Follow for 1 idea a day"),
            "y": 1300, "size": 54, "box": "yellow", "until": until}]
    return ev


def c_captions(a):
    """A run of captions, timed automatically (caption_hold: 0.55 s per word, min 2.5 s) unless a line has "hold".
    args: lines: [str | {text, highlight, hold, size}], y (default 330), size (default 70), gap (default 0).
    In briefs, prefer one caption per beat; use this only for extra captions inside a beat."""
    t = a["t"]
    ev = []
    for ln in a["lines"]:
        if isinstance(ln, str):
            ln = {"text": ln}
        hold = ln.get("hold") or caption_hold(ln["text"])
        ev.append({"type": "caption", "t": t, "text": ln["text"], "highlight": ln.get("highlight", []),
                   "y": a.get("y", CAPTION_Y), "size": ln.get("size", a.get("size", 70)), "until": t + hold})
        t += hold + a.get("gap", 0)
    return ev


def c_formula(a):
    """Handwritten formula or key line. args: text, at [x,y] (centre if align center, default), size (default 64),
    color, mark (substring to highlight), box (bool: draw a box round it), box_color, d."""
    x, y = a["at"]
    size = a.get("size", 64)
    ev = [{"type": "write", "t": a["t"], "text": a["text"], "x": x, "y": y, "size": size,
           "align": a.get("align", "center"), "color": a.get("color", "ink")}]
    if "d" in a:
        ev[0]["d"] = a["d"]
    if a.get("mark"):
        ev[0]["mark"] = a["mark"]
    if a.get("box"):
        dur = a.get("d", write_dur(a["text"]))
        half = a.get("box_w") or min(500, len(a["text"]) * size * 0.27 + 40)
        ev.append({"type": "rect", "t": a["t"] + dur + 0.1, "d": 0.6,
                   "box": [x - half, y - size * 0.95, x + half, y + size * 0.95], "color": a.get("box_color", "orange"), "w": 7})
    return ev


def c_numberline(a):
    """Number line with dots for a data set. args: id, y, values, color, label (written at left), x0 (default 290),
    x1 (default 1000), min, max, ticks, dy (dot offset above line, default -40), r (dot radius, default 14),
    stagger (s between dots, default 0.45), dots_at (start time of dots, default t+1.4)."""
    x0, x1 = a.get("x0", 290), a.get("x1", 1000)
    t = a["t"]
    col = a.get("color", "blue")
    ev = []
    if a.get("label"):
        ev.append({"type": "write", "t": t, "text": a["label"], "x": x0 - 30, "y": a["y"], "size": a.get("label_size", 56),
                   "color": a.get("label_color", col), "align": "right"})
        t += 0.3
    ev.append({"type": "numberline", "t": t, "id": a["id"], "x0": x0, "x1": x1, "y": a["y"], "min": a.get("min", 0),
               "max": a.get("max", 100), "ticks": a.get("ticks", [a.get("min", 0), a.get("max", 100)])})
    ts = a.get("dots_at", t + 1.4)
    for k, v in enumerate(a.get("values", [])):
        ev.append({"type": "dot", "t": ts + k * a.get("stagger", 0.45), "on": a["id"], "v": v, "dy": a.get("dy", -40),
                   "r": a.get("r", 14), "color": col, "d": 0.3})
    return ev


def c_dots(a):
    """Dots popping onto an existing numberline. args: on (numberline id), values, color, stagger (default 0.45),
    dy (default -40), r (default 14)."""
    return [{"type": "dot", "t": a["t"] + k * a.get("stagger", 0.45), "on": a["on"], "v": v, "dy": a.get("dy", -40),
             "r": a.get("r", 14), "color": a.get("color", "blue"), "d": 0.3} for k, v in enumerate(a["values"])]


def c_bar_chart(a):
    """Bars growing from a baseline. args: bars [{label, value, color}], base (baseline y, default 1350),
    x0, x1 (default 140..940), height (px for max value, default 600), max (default max value),
    show_values (bool, default true), fmt (python format for values, default '{:g}'), suffix, stagger (default 0.7)."""
    bars = a["bars"]
    x0, x1 = a.get("x0", 140), a.get("x1", 940)
    base, hmax = a.get("base", 1350), a.get("height", 600)
    vmax = a.get("max") or max(b["value"] for b in bars)
    n = len(bars)
    slot = (x1 - x0) / n
    bw = slot * a.get("width", 0.62)
    t = a["t"]
    ev = [{"type": "line", "t": t, "d": 0.5, "points": [[x0 - 20, base], [x1 + 20, base]], "color": "ink", "w": 6}]
    for k, b in enumerate(bars):
        cx = x0 + slot * (k + 0.5)
        tb = t + 0.6 + k * a.get("stagger", 0.7)
        h = hmax * b["value"] / vmax
        col = b.get("color", "blue")
        ev.append({"type": "bar", "t": tb, "d": 0.6, "x": cx - bw / 2, "w": bw, "base": base, "h": h, "color": col})
        ev.append({"type": "sfx", "t": tb, "name": "tick"})
        ev.append({"type": "write", "t": tb + 0.1, "text": b["label"], "x": cx, "y": base + 50, "size": a.get("label_size", 44),
                   "align": "center", "color": "ink", "d": 0.5})
        if a.get("show_values", True):
            ev.append({"type": "write", "t": tb + 0.8, "text": a.get("fmt", "{:g}").format(b["value"]) + a.get("suffix", ""),
                       "x": cx, "y": base - h - 45, "size": a.get("value_size", 48), "align": "center", "color": col, "d": 0.4})
    return ev


def c_plot(a):
    """Axes with a plotted function. args: box [x0,y0,x1,y1] (plot area, default [140,700,960,1350]), expr (numpy in u,
    e.g. 'exp(-u**2/2)'), u0, u1 (domain, default -3..3), ymax (expr value at top of box, default 1), color,
    xlabel, ylabel, curve_at (start of curve, default t+1.2), curve_d (default 2.2)."""
    x0, y0, x1, y1 = a.get("box", [140, 700, 960, 1350])
    t = a["t"]
    ev = [{"type": "arrow", "t": t, "d": 0.5, "from": [x0, y1], "to": [x1 + 30, y1], "color": "ink", "w": 6, "head": 24},
          {"type": "arrow", "t": t + 0.3, "d": 0.5, "from": [x0, y1], "to": [x0, y0 - 30], "color": "ink", "w": 6, "head": 24}]
    if a.get("xlabel"):
        ev.append({"type": "write", "t": t + 0.6, "text": a["xlabel"], "x": (x0 + x1) / 2, "y": y1 + 55, "size": 44,
                   "align": "center", "color": "grey"})
    if a.get("ylabel"):
        ev.append({"type": "write", "t": t + 0.6, "text": a["ylabel"], "x": x0 + 20, "y": y0 - 60, "size": 44, "color": "grey"})
    ev.append({"type": "curve", "t": a.get("curve_at", t + 1.2), "d": a.get("curve_d", 2.2), "x0": x0 + 10, "x1": x1,
               "y": y1, "expr": a["expr"], "u0": a.get("u0", -3), "u1": a.get("u1", 3),
               "height": (y1 - y0) / a.get("ymax", 1), "color": a.get("color", "blue"), "w": a.get("w", 8)})
    return ev


def c_flow(a):
    """Boxes joined by arrows, top to bottom (or left to right with direction 'row'). args: items [str],
    at [x,y] (centre of first box, default [540,700]), gap (centre to centre, default 230), box_w (default 640),
    box_h (default 130), size (text, default 52), colors (list), direction ('column'|'row'), step (s per box, default 1.8)."""
    items = a["items"]
    x, y = a.get("at", [W / 2, 700])
    gap = a.get("gap", 230 if a.get("direction", "column") == "column" else 330)
    bw, bh = a.get("box_w", 640 if a.get("direction", "column") == "column" else 280), a.get("box_h", 130)
    cols = a.get("colors", ["ink"])
    t = a["t"]
    ev = []
    for k, txt in enumerate(items):
        cx, cy = (x, y + k * gap) if a.get("direction", "column") == "column" else (x + k * gap, y)
        col = cols[k % len(cols)]
        tk = t + k * a.get("step", 1.8)
        ev.append({"type": "rect", "t": tk, "d": 0.45, "box": [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2], "color": col, "w": 6})
        ev.append({"type": "write", "t": tk + 0.35, "text": txt, "x": cx, "y": cy, "size": a.get("size", 52), "align": "center",
                   "color": col, "d": write_dur(txt)})
        if k:
            if a.get("direction", "column") == "column":
                fr, to = [cx, cy - gap + bh / 2 + 10], [cx, cy - bh / 2 - 10]
            else:
                fr, to = [cx - gap + bw / 2 + 10, cy], [cx - bw / 2 - 10, cy]
            ev.append({"type": "arrow", "t": tk - 0.2, "d": 0.3, "from": fr, "to": to, "color": "grey", "w": 6, "head": 22})
    return ev


def c_checklist(a):
    """List with ticks or crosses. args: items [str | {text, mark: 'check'|'cross'|'none', color}], at [x,y] (left, first row),
    gap (default 120), size (default 54), mark (default 'check'), step (default 1.8)."""
    x, y = a.get("at", [140, 750])
    t = a["t"]
    ev = []
    for k, it in enumerate(a["items"]):
        if isinstance(it, str):
            it = {"text": it}
        mk = it.get("mark", a.get("mark", "check"))
        col = it.get("color", {"check": "green", "cross": "red"}.get(mk, "ink"))
        cy = y + k * a.get("gap", 120)
        tk = t + k * a.get("step", 1.8)
        ev.append({"type": "rect", "t": tk, "d": 0.35, "box": [x, cy - 32, x + 64, cy + 32], "color": "ink", "w": 5})
        ev.append({"type": "write", "t": tk + 0.3, "text": it["text"], "x": x + 100, "y": cy, "size": a.get("size", 54)})
        if mk != "none":
            ev += c_icon({"t": tk + 0.4 + write_dur(it["text"]), "name": mk, "at": [x + 34, cy - 6], "size": 44, "color": col, "w": 8, "d": 0.3})
            ev.append({"type": "sfx", "t": tk + 0.4 + write_dur(it["text"]), "name": "tick" if mk == "check" else "thud"})
    return ev


def c_vs(a):
    """Split board for comparisons. args: left, right (headers), left_color, right_color, y (header, default 640),
    line_to (bottom of divider, default 1450)."""
    t = a["t"]
    y = a.get("y", 640)
    return [{"type": "line", "t": t, "d": 0.5, "points": [[W / 2, y - 60], [W / 2, a.get("line_to", 1450)]], "color": "grey", "w": 5},
            {"type": "write", "t": t + 0.3, "text": a["left"], "x": W / 4 + 10, "y": y, "size": a.get("size", 64), "align": "center",
             "color": a.get("left_color", "blue")},
            {"type": "write", "t": t + 0.8, "text": a["right"], "x": 3 * W / 4 - 10, "y": y, "size": a.get("size", 64),
             "align": "center", "color": a.get("right_color", "orange")},
            {"type": "underline", "t": t + 1.3, "d": 0.3, "x0": W / 4 - 140, "x1": W / 4 + 160, "y": y + 50, "color": a.get("left_color", "blue"), "w": 6},
            {"type": "underline", "t": t + 1.5, "d": 0.3, "x0": 3 * W / 4 - 160, "x1": 3 * W / 4 + 140, "y": y + 50, "color": a.get("right_color", "orange"), "w": 6}]


def c_progress(a):
    """Progress bar, e.g. 'Course: 12% complete'. args: pct (0-100), at [x,y] (left, centre line, default [140,900]),
    w (default 800), h (default 70), color (fill, default red), label (written above), fill_d (default 1.6)."""
    x, y = a.get("at", [140, 900])
    w, h = a.get("w", 800), a.get("h", 70)
    t = a["t"]
    col = a.get("color", "red")
    ev = []
    if a.get("label"):
        ev.append({"type": "write", "t": t, "text": a["label"], "x": x, "y": y - h - 30, "size": a.get("label_size", 52)})
        t += write_dur(a["label"]) + 0.3
    ev.append({"type": "rect", "t": t, "d": 0.5, "box": [x, y - h / 2, x + w, y + h / 2], "color": "ink", "w": 6})
    ev.append({"type": "hbar", "t": t + 0.5, "d": a.get("fill_d", 1.6), "x": x + 8, "y": y - h / 2 + 8, "w": (w - 16) * a["pct"] / 100,
               "h": h - 16, "color": col})
    ev.append({"type": "count", "t": t + 0.5, "d": a.get("fill_d", 1.6), "from": 0, "to": a["pct"], "fmt": "{:.0f}", "suffix": "%",
               "x": x + w + 30, "y": y, "size": 56, "color": col})
    return ev


def c_bubble(a):
    """Speech bubble with text. args: text, box [x0,y0,x1,y1], tail [x,y] (point the tail aims at), size (default 50), color."""
    x0, y0, x1, y1 = a["box"]
    tx, ty = a.get("tail", [x0 + 80, y1 + 80])
    bx = min(max(tx, x0 + 60), x1 - 100)
    t = a["t"]
    outline = rrect(x0, y0, x1, y1, 40)
    return [{"type": "polyline", "t": t, "d": 0.6, "points": outline, "color": a.get("color", "ink"), "w": 6},
            {"type": "polyline", "t": t + 0.55, "d": 0.25, "points": [[bx, y1 - 2], [tx, ty], [bx + 70, y1 - 2]],
             "color": a.get("color", "ink"), "w": 6},
            {"type": "write", "t": t + 0.7, "text": a["text"], "x": (x0 + x1) / 2, "y": (y0 + y1) / 2,
             "size": a.get("size", 50), "align": "center", "color": a.get("text_color", "ink")}]


def c_reveal(a):
    """Wrong-answer reveal: cross out a wrong line, write the right one under it. args: wrong, right, at [x,y]
    (centre of wrong line, default [540,850]), size (default 64), gap (default 170), pause (s before cross-out, default 2.5)."""
    x, y = a.get("at", [W / 2, 850])
    size = a.get("size", 64)
    t = a["t"]
    half = min(480, len(a["wrong"]) * size * 0.25 + 30)
    tc = t + write_dur(a["wrong"]) + a.get("pause", 2.5)
    return [{"type": "write", "t": t, "text": a["wrong"], "x": x, "y": y, "size": size, "align": "center", "color": "grey"},
            {"type": "line", "t": tc, "d": 0.35, "points": [[x - half, y + 8], [x + half, y - 8]], "color": "red", "w": 9},
            {"type": "sfx", "t": tc, "name": "thud"},
            {"type": "write", "t": tc + 0.5, "text": a["right"], "x": x, "y": y + a.get("gap", 170), "size": size, "align": "center",
             "color": a.get("color", "green")},
            {"type": "sfx", "t": tc + 0.5 + write_dur(a["right"]), "name": "success"}]


COMPONENTS = {
    "icon": c_icon, "person": c_person, "hook": c_hook, "outro": c_outro, "captions": c_captions,
    "formula": c_formula, "numberline": c_numberline, "dots": c_dots, "bar_chart": c_bar_chart, "plot": c_plot, "flow": c_flow,
    "checklist": c_checklist, "vs": c_vs, "progress": c_progress, "bubble": c_bubble, "reveal": c_reveal,
}


def expand(events):
    """Replace every {"type": "use", ...} event (recursively) with the events its component produces."""
    out = []
    for e in events:
        if e.get("type") != "use":
            out.append(e)
            continue
        name = e.get("component")
        if name not in COMPONENTS:
            raise ValueError(f"unknown component {name!r}; available: {', '.join(sorted(COMPONENTS))}")
        out += expand(COMPONENTS[name](e))
    return out
