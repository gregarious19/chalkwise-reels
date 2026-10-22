#!/usr/bin/env python3
"""Chalkwise reel renderer.

Turns a JSON reel spec (scripts/*.json) into a 1080x1920 MP4: a self-drawing
whiteboard with marker-written text, hand-drawn shapes, pop-in captions,
marker sounds and a soft background pad. No voiceover: captions carry the words, sounds carry the feel.

Usage: python3 render.py scripts/reel.json out.mp4 [--preview]
"""
import json, math, subprocess, sys, argparse, os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))

COLORS = {
    "bg": (251, 248, 241), "ink": (29, 29, 31), "blue": (47, 107, 255),
    "orange": (255, 122, 26), "green": (25, 164, 99), "red": (229, 72, 77),
    "yellow": (255, 224, 102), "grey": (150, 150, 150), "white": (255, 255, 255),
    "purple": (124, 77, 255),
}

def col(c):
    if isinstance(c, (list, tuple)):
        return tuple(c)
    if isinstance(c, str) and c.startswith("#"):
        return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
    return COLORS.get(c or "ink", COLORS["ink"])

def find_font(names):
    for n in names:
        p = n if os.path.isabs(n) else os.path.join(HERE, "assets", "fonts", n)
        if os.path.exists(p):
            return p
    out = subprocess.run(["fc-match", "-f", "%{file}", names[-1]], capture_output=True, text=True).stdout
    return out

CAPTION_FONT = find_font(["Poppins-Bold.ttf", "/usr/share/fonts/truetype/poppins/Poppins-Bold.ttf", "Poppins:bold"])
# Handwriting font: used when present (GitHub runner downloads Kalam). Fallback: Hershey stroke font.
HAND_FONT = None
for cand in ["Kalam-Bold.ttf", "Caveat-Bold.ttf"]:
    p = os.path.join(HERE, "assets", "fonts", cand)
    if os.path.exists(p):
        HAND_FONT = p
        break

def ease(p):
    p = min(max(p, 0.0), 1.0)
    return p * p * (3 - 2 * p)

def back_out(p):
    p = min(max(p, 0.0), 1.0)
    s = 1.7
    p -= 1
    return p * p * ((s + 1) * p + s) + 1

# ---------------------------------------------------------------- geometry
def wobble(points, seed, amp=2.2, density=6.0):
    """Resample a polyline densely and add smooth hand-drawn wobble."""
    pts = np.array(points, dtype=float)
    seg = np.diff(pts, axis=0)
    lens = np.hypot(seg[:, 0], seg[:, 1])
    total = lens.sum()
    if total < 1:
        return pts
    n = max(int(total / density), 2)
    cum = np.concatenate([[0], np.cumsum(lens)])
    s = np.linspace(0, total, n)
    xs = np.interp(s, cum, pts[:, 0])
    ys = np.interp(s, cum, pts[:, 1])
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 6.28, 3)
    u = s / max(total, 1)
    off = amp * (np.sin(u * 3.1 + ph[0]) * 0.6 + np.sin(u * 7.3 + ph[1]) * 0.3 + np.sin(u * 13 + ph[2]) * 0.1)
    dx = np.gradient(xs); dy = np.gradient(ys)
    norm = np.hypot(dx, dy) + 1e-9
    xs = xs + off * (-dy / norm)
    ys = ys + off * (dx / norm)
    return np.stack([xs, ys], 1)

def circle_pts(c, r, start=-100, sweep=375):
    a = np.radians(np.linspace(start, start + sweep, 80))
    return np.stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)], 1)

def ellipse_pts(c, rx, ry, start=-100, sweep=375):
    a = np.radians(np.linspace(start, start + sweep, 90))
    return np.stack([c[0] + rx * np.cos(a), c[1] + ry * np.sin(a)], 1)

def draw_poly(img, pts, color, w, p=1.0):
    if p <= 0 or len(pts) < 2:
        return None
    k = max(2, int(round(len(pts) * min(p, 1.0))))
    sub = np.round(pts[:k] * 4).astype(np.int32)  # 2 bits of subpixel precision
    cv2.polylines(img, [sub], False, color[::-1], int(w), cv2.LINE_AA, shift=2)
    return tuple(pts[k - 1])

# ---------------------------------------------------------------- text
_text_cache = {}

def hand_text_mask(text, size):
    """Return (mask uint8 HxW, width, height, baseline offset) for marker text."""
    key = (text, size)
    if key in _text_cache:
        return _text_cache[key]
    if HAND_FONT:
        font = ImageFont.truetype(HAND_FONT, int(size * 1.35))
        l, t, r, b = font.getbbox(text)
        im = Image.new("L", (r - l + 20, b - t + 20), 0)
        ImageDraw.Draw(im).text((10 - l, 10 - t), text, font=font, fill=255)
        m = np.array(im)
    else:
        scale = size / 22.0
        th = max(2, int(round(scale * 2.3)))
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, tht), base = cv2.getTextSize(text, font, scale, th)
        m = np.zeros((tht + base + 2 * th + 10, tw + 2 * th + 10), np.uint8)
        cv2.putText(m, text, (th + 5, tht + th + 5), font, scale, 255, th, cv2.LINE_AA)
    res = (m, m.shape[1], m.shape[0])
    _text_cache[key] = res
    return res

def blit_mask(img, mask, x, y, color, alpha=1.0):
    h, w = mask.shape
    x0, y0 = int(x), int(y)
    x1, y1 = min(x0 + w, img.shape[1]), min(y0 + h, img.shape[0])
    if x1 <= max(x0, 0) or y1 <= max(y0, 0):
        return
    mx0, my0 = max(0, -x0), max(0, -y0)
    x0c, y0c = max(x0, 0), max(y0, 0)
    a = mask[my0:my0 + (y1 - y0c), mx0:mx0 + (x1 - x0c)].astype(np.float32)[..., None] / 255.0 * alpha
    reg = img[y0c:y1, x0c:x1].astype(np.float32)
    c = np.array(color[::-1], np.float32)
    img[y0c:y1, x0c:x1] = (reg * (1 - a) + c * a).astype(np.uint8)

def blit_rgba(img, rgba, x, y, alpha=1.0):
    h, w = rgba.shape[:2]
    x0, y0 = int(x), int(y)
    x1, y1 = min(x0 + w, img.shape[1]), min(y0 + h, img.shape[0])
    mx0, my0 = max(0, -x0), max(0, -y0)
    x0c, y0c = max(x0, 0), max(y0, 0)
    if x1 <= x0c or y1 <= y0c:
        return
    src = rgba[my0:my0 + (y1 - y0c), mx0:mx0 + (x1 - x0c)].astype(np.float32)
    a = src[..., 3:4] / 255.0 * alpha
    reg = img[y0c:y1, x0c:x1].astype(np.float32)
    img[y0c:y1, x0c:x1] = (reg * (1 - a) + src[..., 2::-1] * a).astype(np.uint8)

_cap_cache = {}

def caption_layer(text, size, highlight, color, maxw=940, box=None):
    """Bold caption with marker-yellow highlight behind chosen words. Returns BGRA-ish RGBA array."""
    key = (text, size, tuple(highlight or []), color, maxw, box)
    if key in _cap_cache:
        return _cap_cache[key]
    font = ImageFont.truetype(CAPTION_FONT, size)
    words = text.split()
    hl = set()
    for phrase in highlight or []:
        ph = phrase.split()
        for i in range(len(words) - len(ph) + 1):
            if [w.strip(".,!?:").lower() for w in words[i:i + len(ph)]] == [p.lower() for p in ph]:
                hl.update(range(i, i + len(ph)))
    space = font.getlength(" ")
    lines, cur, curw = [], [], 0
    for i, w in enumerate(words):
        wl = font.getlength(w)
        if cur and curw + space + wl > maxw:
            lines.append(cur); cur, curw = [], 0
        cur.append(i); curw += (space if len(cur) > 1 else 0) + wl
    if cur:
        lines.append(cur)
    lh = int(size * 1.22)
    pad = 24
    widths = [sum(font.getlength(words[i]) for i in ln) + space * (len(ln) - 1) for ln in lines]
    Wc = int(max(widths) + 2 * pad)
    Hc = int(lh * len(lines) + 2 * pad)
    im = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle([0, 0, Wc - 1, Hc - 1], radius=28, fill=col(box) + (255,))
    y = pad
    for ln, lw in zip(lines, widths):
        x = (Wc - lw) / 2
        for i in ln:
            w = words[i]
            wl = font.getlength(w)
            if i in hl:
                d.rounded_rectangle([x - 8, y + size * 0.12, x + wl + 8, y + size * 1.12], radius=10,
                                    fill=COLORS["yellow"] + (255,))
            d.text((x, y), w, font=font, fill=col(color) + (255,))
            x += wl + space
        y += lh
    arr = np.array(im)
    _cap_cache[key] = arr
    return arr

# ---------------------------------------------------------------- scene model
class Reel:
    def __init__(self, spec):
        self.spec = spec
        self.fps = spec.get("fps", 30)
        self.duration = spec["duration"]
        self.lines = {}  # numberline id -> (x0, x1, y, vmin, vmax)
        self.events = []
        for i, e in enumerate(spec["events"]):
            e = dict(e)
            e["_i"] = i
            e.setdefault("d", self.default_dur(e))
            self.events.append(e)
            if e["type"] == "numberline":
                self.lines[e["id"]] = (e["x0"], e["x1"], e["y"], e.get("min", 0), e.get("max", 100))
        # "mark" on a write event: auto marker-highlight a substring after it is written
        extra = []
        for e in self.events:
            if e["type"] == "write" and e.get("mark"):
                full, fw, fh = hand_text_mask(e["text"], e.get("size", 64))
                idx = e["text"].find(e["mark"])
                if idx < 0:
                    continue
                pre = hand_text_mask(e["text"][:idx], e.get("size", 64))[1] if idx else 0
                sub = hand_text_mask(e["mark"], e.get("size", 64))[1]
                x = e["x"] - (fw / 2 if e.get("align") == "center" else 0)
                hx0 = x + max(pre - 12, 0)
                hx1 = x + pre + sub - (12 if idx else 0)
                hh = e.get("size", 64) * 0.75
                extra.append({"type": "highlight", "t": e["t"] + e["d"] + 0.1, "d": 0.45,
                              "box": [hx0 - 6, e["y"] - hh, hx1 + 6, e["y"] + hh], "color": e.get("mark_color", "yellow"),
                              "alpha": 0.45, "_i": len(self.events) + len(extra)})
        self.events += extra
        self.events.sort(key=lambda e: e["t"])
        self.bg = self.make_bg()

    def default_dur(self, e):
        t = e["type"]
        if t == "write":
            return max(0.35, 0.055 * len(e["text"]))
        return {"dot": 0.25, "caption": 0.22, "clear": 0.35, "numberline": 0.9}.get(t, 0.6)

    def make_bg(self):
        rng = np.random.default_rng(7)
        bg = np.empty((H, W, 3), np.float32)
        bg[:] = np.array(COLORS["bg"][::-1], np.float32)
        noise = rng.normal(0, 3.0, (H // 4, W // 4)).astype(np.float32)
        noise = cv2.resize(noise, (W, H), interpolation=cv2.INTER_CUBIC)
        bg += noise[..., None]
        yy, xx = np.mgrid[0:H, 0:W]
        vig = 1 - 0.06 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        bg *= vig[..., None]
        img = np.clip(bg, 0, 255).astype(np.uint8)
        # brand mark, top-left
        lay = caption_layer("chalkwise", 34, [], "ink", maxw=600)
        blit_rgba(img, lay, 40, 70, alpha=0.55)
        return img

    def vx(self, line_id, v):
        x0, x1, y, a, b = self.lines[line_id]
        return x0 + (v - a) / (b - a) * (x1 - x0), y

    # draw an event at progress p (0..1). returns marker tip or None
    def draw(self, img, e, p):
        t = e["type"]
        c = col(e.get("color"))
        w = e.get("w", 7)
        seed = e["_i"] * 31 + 5
        if t == "write":
            m, mw, mh = hand_text_mask(e["text"], e.get("size", 64))
            x, y = e["x"], e["y"]
            if e.get("align") == "center":
                x -= mw / 2
            reveal = int(mw * ease(p) if p < 1 else mw)
            if reveal <= 0:
                return None
            mm = m.copy()
            if reveal < mw:
                mm[:, reveal:] = 0
                # soft edge
                edge = min(10, reveal)
                ramp = np.linspace(1, 0, edge)[None, :]
                mm[:, reveal - edge:reveal] = (mm[:, reveal - edge:reveal] * ramp).astype(np.uint8)
            blit_mask(img, mm, x, y - mh / 2, c)
            if p < 1:
                col_ = mm[:, max(reveal - 3, 0)]
                ys = np.nonzero(col_ > 60)[0]
                ty = y - mh / 2 + (ys.mean() if len(ys) else mh / 2)
                return (x + reveal, ty)
            return None
        if t in ("line", "polyline"):
            pts = wobble(e["points"], seed, amp=e.get("wobble", 2.0))
            return draw_poly(img, pts, c, w, ease(p))
        if t == "arrow":
            a, b = np.array(e["from"], float), np.array(e["to"], float)
            pts = wobble([a, b], seed, amp=1.8)
            tip = draw_poly(img, pts, c, w, ease(min(p / 0.8, 1)))
            if p > 0.8:
                q = ease((p - 0.8) / 0.2)
                ang = math.atan2(b[1] - a[1], b[0] - a[0])
                L = e.get("head", 30) * q
                for s in (1, -1):
                    hx = b[0] - L * math.cos(ang + s * 0.5)
                    hy = b[1] - L * math.sin(ang + s * 0.5)
                    draw_poly(img, wobble([b, (hx, hy)], seed + s, amp=0.6, density=3), c, w)
            return tip if p < 1 else None
        if t == "circle":
            pts = wobble(circle_pts(e["c"], e["r"]), seed, amp=3)
            return draw_poly(img, pts, c, w, ease(p))
        if t == "ellipse":
            pts = wobble(ellipse_pts(e["c"], e["rx"], e["ry"]), seed, amp=3)
            return draw_poly(img, pts, c, w, ease(p))
        if t == "rect":
            x0, y0, x1, y1 = e["box"]
            pts = wobble([(x0, y0), (x1, y0 + 2), (x1, y1), (x0 + 2, y1), (x0, y0 - 4)], seed, amp=2.5)
            return draw_poly(img, pts, c, w, ease(p))
        if t == "underline":
            x0, x1, y = e["x0"], e["x1"], e["y"]
            pts = wobble([(x0, y), (x1, y + 3)], seed, amp=2)
            return draw_poly(img, pts, c, w, ease(p))
        if t == "curve":
            xs = np.linspace(e["x0"], e["x1"], 160)
            u = np.linspace(e.get("u0", -3), e.get("u1", 3), 160)
            ys = eval(e["expr"], {"__builtins__": {}}, {"u": u, "np": np, "exp": np.exp, "sin": np.sin})
            pts = np.stack([xs, e["y"] - np.asarray(ys) * e.get("height", 200)], 1)
            pts = wobble(pts, seed, amp=1.5)
            return draw_poly(img, pts, c, w, ease(p))
        if t == "numberline":
            x0, x1, y = e["x0"], e["x1"], e["y"]
            pl = min(p / 0.65, 1)
            draw_poly(img, wobble([(x0, y), (x1, y)], seed, amp=1.5), c, w, ease(pl))
            tip = (x0 + (x1 - x0) * ease(pl), y) if pl < 1 else None
            if p > 0.65:
                q = (p - 0.65) / 0.35
                ticks = e.get("ticks", [])
                for j, v in enumerate(ticks):
                    if q * len(ticks) < j:
                        break
                    tx, _ = self.vx(e["id"], v)
                    draw_poly(img, np.array([(tx, y - 16), (tx, y + 16)], float), c, max(4, w - 2))
                    m, mw, mh = hand_text_mask(str(v), e.get("label_size", 40))
                    blit_mask(img, m, tx - mw / 2, y + 26, col("grey") if e.get("grey_labels", True) else c)
            return tip
        if t == "dot":
            if "on" in e:
                cx, cy = self.vx(e["on"], e["v"])
                cy += e.get("dy", 0)
            else:
                cx, cy = e["c"]
            r = e.get("r", 16) * back_out(p)
            if r > 0.5:
                cv2.circle(img, (int(cx * 4), int(cy * 4)), int(r * 4), c[::-1], -1, cv2.LINE_AA, shift=2)
            return None
        if t == "highlight":  # translucent marker swipe
            x0, y0, x1, y1 = e["box"]
            q = ease(p)
            xe = x0 + (x1 - x0) * q
            over = img.copy()
            cv2.rectangle(over, (int(x0), int(y0)), (int(xe), int(y1)), col(e.get("color", "yellow"))[::-1], -1)
            a = e.get("alpha", 0.45)
            img[:] = cv2.addWeighted(over, a, img, 1 - a, 0)
            return (xe, (y0 + y1) / 2) if p < 1 else None
        return None

    def render_frames(self, out_raw, preview=False):
        n = int(self.duration * self.fps)
        base = self.bg.copy()
        committed = set()
        clear_anim = None
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
               "-r", str(self.fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
               "-pix_fmt", "yuv420p", out_raw]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        board_events = [e for e in self.events if e["type"] not in ("caption",)]
        captions = [e for e in self.events if e["type"] == "caption"]
        for fi in range(n):
            now = fi / self.fps
            # commit finished events / handle clears
            for e in board_events:
                if e["_i"] in committed or now < e["t"] + e["d"]:
                    continue
                if e["type"] == "clear":
                    base = self.bg.copy()
                else:
                    self.draw(base, e, 1.0)
                committed.add(e["_i"])
            frame = base.copy()
            tip = None
            for e in board_events:
                if e["_i"] in committed or now < e["t"]:
                    continue
                p = (now - e["t"]) / e["d"]
                if e["type"] == "clear":
                    # paper swipe: new background slides in from the right
                    xs = int(W * (1 - ease(p)))
                    frame[:, xs:] = self.bg[:, xs:]
                    continue
                tt = self.draw(frame, e, p)
                if tt is not None:
                    tip = tt
            for e in captions:
                end = e.get("until", e["t"] + 2.5)
                if not (e["t"] <= now < end):
                    continue
                lay = caption_layer(e["text"], e.get("size", 72), e.get("highlight"), e.get("color", "ink"),
                                    e.get("maxw", 940), e.get("box"))
                p = (now - e["t"]) / e["d"]
                fade_out = min(1, (end - now) / 0.15)
                a = min(1, ease(p)) * fade_out
                dy = (1 - back_out(min(p, 1))) * 40
                x = (W - lay.shape[1]) / 2
                blit_rgba(frame, lay, x, e.get("y", 250) - lay.shape[0] / 2 + dy, alpha=a)
            if tip is not None:
                self.draw_marker(frame, tip)
            proc.stdin.write(frame.tobytes())
            if preview and fi % int(self.fps) == 0:
                cv2.imwrite(f"/tmp/chalkwise_preview_{int(now):02d}.png", frame)
        proc.stdin.close()
        proc.wait()

    def draw_marker(self, img, tip):
        x, y = tip
        ang = math.radians(-55)
        L = 150
        bx, by = x + L * math.cos(ang) * 1.0, y + L * math.sin(ang) * 1.0
        # shadow
        cv2.line(img, (int(x + 10), int(y + 14)), (int(bx + 18), int(by + 22)), (200, 200, 200), 30, cv2.LINE_AA)
        # body
        cv2.line(img, (int(x + 14 * math.cos(ang)), int(y + 14 * math.sin(ang))), (int(bx), int(by)),
                 (60, 50, 45), 28, cv2.LINE_AA)
        cv2.line(img, (int(x + 40 * math.cos(ang)), int(y + 40 * math.sin(ang))), (int(bx), int(by)),
                 (40, 120, 255)[::-1], 30, cv2.LINE_AA)
        # nib
        cv2.line(img, (int(x), int(y)), (int(x + 16 * math.cos(ang)), int(y + 16 * math.sin(ang))),
                 (29, 29, 31), 10, cv2.LINE_AA)

    # ------------------------------------------------------------ audio
    def render_audio(self, path):
        sr = 48000
        n = int(self.duration * sr)
        out = np.zeros(n, np.float32)
        rng = np.random.default_rng(3)
        from scipy.signal import butter, sosfilt
        sos = butter(4, [1800, 6000], btype="band", fs=sr, output="sos")
        for e in self.events:
            t = e["type"]
            s0 = int(e["t"] * sr)
            if t in ("write", "line", "polyline", "arrow", "circle", "ellipse", "rect", "underline", "curve",
                     "numberline"):
                L = int(e["d"] * sr)
                nz = sosfilt(sos, rng.normal(0, 1, L)).astype(np.float32)
                tt = np.arange(L) / sr
                flutter = 0.55 + 0.45 * np.abs(np.sin(2 * np.pi * (9 if t == "write" else 4) * tt + rng.uniform(0, 6)))
                env = np.minimum(1, np.minimum(tt / 0.03, (e["d"] - tt) / 0.05)).clip(0, 1)
                seg = nz * flutter * env * 0.09
                out[s0:s0 + L] += seg[:max(0, min(L, n - s0))]
            elif t in ("dot", "caption"):
                L = int(0.09 * sr)
                tt = np.arange(L) / sr
                f = 700 if t == "dot" else 420
                seg = np.sin(2 * np.pi * f * tt * (1 + 2 * tt)) * np.exp(-tt * 45) * (0.18 if t == "dot" else 0.12)
                out[s0:s0 + L] += seg[:max(0, min(L, n - s0))].astype(np.float32)
            elif t == "clear":
                L = int(e["d"] * sr)
                nz = sosfilt(butter(2, 1200, fs=sr, output="sos"), rng.normal(0, 1, L))
                tt = np.arange(L) / sr
                seg = nz * np.sin(np.pi * tt / e["d"]) * 0.12
                out[s0:s0 + L] += seg[:max(0, min(L, n - s0))].astype(np.float32)
        # soft pad: Am9 / Fmaj7 / Cmaj7 / G6, 4 s each, gentle attack
        tt = np.arange(n) / sr
        chords = [[220.0, 261.6, 329.6, 493.9], [174.6, 220.0, 261.6, 329.6], [130.8, 196.0, 246.9, 329.6],
                  [196.0, 246.9, 293.7, 329.6]]
        pad = np.zeros(n, np.float32)
        seg_len = 4 * sr
        for k in range(0, n, seg_len):
            ch = chords[(k // seg_len) % 4]
            L = min(seg_len + sr // 2, n - k)
            ts = np.arange(L) / sr
            env = np.minimum(1, ts / 0.8) * np.minimum(1, np.maximum(0, (L / sr - ts) / 0.8))
            s = sum(np.sin(2 * np.pi * f * ts) + 0.3 * np.sin(2 * np.pi * 2 * f * ts) for f in ch)
            pad[k:k + L] += (s * env * 0.012).astype(np.float32)
        pad *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * tt)).astype(np.float32)
        # fade in/out
        fade = np.minimum(1, np.minimum(tt / 1.0, (self.duration - tt) / 1.2)).clip(0, 1)
        mix = out + pad * fade
        peak = np.max(np.abs(mix)) + 1e-9
        mix = (mix / peak * 0.89).astype(np.float32)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                        path], input=mix.tobytes(), check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("out")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    reel = Reel(spec)
    tmp_v = a.out + ".video.mp4"
    tmp_a = a.out + ".audio.wav"
    reel.render_frames(tmp_v, preview=a.preview)
    reel.render_audio(tmp_a)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp_v, "-i", tmp_a, "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", a.out], check=True)
    os.remove(tmp_v); os.remove(tmp_a)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
