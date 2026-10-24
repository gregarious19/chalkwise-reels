#!/usr/bin/env python3
"""Brief -> checked, timed spec -> rendered reel + preview sheet. The one command the daily run uses.

    python3 make.py briefs/<id>.json            build, check, render, contact sheet
    python3 make.py briefs/<id>.json --no-render  build and check only (fast)
    python3 make.py briefs/<id>.json --slot 15    post today at 15:00 IST (slots: 11, 15, 19, 23)

A brief holds only content (see BRIEF_FORMAT.md). This script works out every start time and
duration from the reading-pace rules, writes scripts/queue/<id>.json, checks layout, pacing,
text and caption rules, renders out/<id>.mp4 and out/<id>_sheet.png, and prints PASS or a list
of problems to fix in the brief. It exits non-zero on any problem.
"""
import argparse, datetime, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import components as C
import render as R

GAP_AFTER_HOOK = 0.5
OUTRO_LEN = 10.0
ITEM_LEAD = 0.4          # caption appears this long before the first drawing of a beat
MIN_DUR, MAX_DUR = 30, 60
BANNED = ["download now", "try it now", "try it today", "available now", "sign up now", "cure", "treat", "diagnos"]


IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SLOTS = (11, 15, 19, 23)  # posting times, IST. Must match the crons in .github/workflows/post.yml


def slot_time(hour):
    """Today's posting slot at <hour>:00 IST, as an ISO string."""
    d = datetime.datetime.now(IST).date()
    return datetime.datetime(d.year, d.month, d.day, hour, tzinfo=IST).isoformat()


def next_slot():
    """The next posting slot that hasn't started yet (today, or tomorrow's first)."""
    now = datetime.datetime.now(IST)
    for h in SLOTS:
        t = now.replace(hour=h, minute=0, second=0, microsecond=0)
        if t > now:
            return t.isoformat()
    t = (now + datetime.timedelta(days=1)).replace(hour=SLOTS[0], minute=0, second=0, microsecond=0)
    return t.isoformat()


def default_dur(e):
    return e.get("d", R.Reel.default_dur(None, e))


def events_end(evs):
    end = 0.0
    for e in evs:
        if e["type"] == "caption":
            continue
        end = max(end, e["t"] + default_dur(e))
    return end


def item_events(item, start):
    """One 'show' item -> absolute events. Component items carry "component"; raw events carry "type"."""
    it = {k: v for k, v in item.items() if k not in ("with_previous", "delay")}
    if "component" in it:
        it["type"] = "use"
        it["t"] = start + it.get("t", 0)
        return C.expand([it]), [it]
    ev = dict(it)
    ev["t"] = start + ev.get("t", 0)
    return C.expand([ev]), [ev]


def build(brief):
    ev = []
    hook = dict(brief["hook"])
    hook.update({"type": "use", "component": "hook", "t": 0})
    ev.append(hook)
    T = events_end(C.expand([hook])) if not hook.get("until") else hook["until"]
    T = max(T, C.expand([hook])[0]["until"]) + GAP_AFTER_HOOK
    for b in brief["beats"]:
        start = T
        cap_need = C.caption_hold(b["caption"]) if b.get("caption") else 0
        cur = start + ITEM_LEAD
        prev_start = cur
        vis_end = start
        for item in b.get("show", []):
            s = prev_start if item.get("with_previous") else cur
            s += item.get("delay", 0)
            expanded, raw = item_events(item, s)
            ev += raw
            e_end = events_end(expanded)
            vis_end = max(vis_end, e_end)
            prev_start = s
            cur = max(cur, e_end) if not item.get("with_previous") else max(cur, e_end)
        end = max(start + cap_need, vis_end + C.BEAT_REST_S, start + b.get("min_hold", 0))
        if b.get("caption"):
            ev.append({"type": "caption", "t": start, "text": b["caption"], "highlight": b.get("highlight", []),
                       "y": C.CAPTION_Y, "size": b.get("caption_size", 70 if len(b["caption"]) < 34 else 62), "until": end})
        T = end
        if b.get("clear_after"):
            ev.append({"type": "clear", "t": T})
            T += 0.5
    outro = dict(brief.get("outro", {}))
    o_start = T + 0.45
    outro.update({"type": "use", "component": "outro", "t": o_start, "until": o_start + OUTRO_LEN})
    ev.append(outro)
    duration = round(o_start + OUTRO_LEN, 2)
    spec = {"id": brief["id"], "topic": brief["topic"], "hook_type": brief["hook_type"], "format": brief["format"],
            "post_after": brief.get("post_after") or next_slot(), "approved": False,
            "duration": duration, "caption": brief["caption"], "brief": f"briefs/{brief['id']}.json", "events": ev}
    return spec


# ---------------------------------------------------------------- checks
def text_box(e):
    """Ink box of handwritten text. Measured with the local font (GitHub's Kalam is within ~5% of it);
    height is the letter body (about 0.9 x size), not the padded mask, so stacked lines don't false-alarm."""
    m, mw, mh = R.hand_text_mask(e.get("text") or "", e.get("size", 64))
    cols = (m > 60).any(axis=0).nonzero()[0]
    ink_w = (cols[-1] - cols[0] + 1) if len(cols) else 0
    pad = cols[0] if len(cols) else 0
    x = e["x"] - {"center": mw / 2, "right": mw}.get(e.get("align"), 0) + pad
    hh = e.get("size", 64) * 0.45
    return [x, e["y"] - hh, x + ink_w, e["y"] + hh]


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    return w > 8 and h > 8


def check(spec, brief):
    probs = []
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+", spec["id"]):
        probs.append(f"id {spec['id']!r} must look like YYYY-MM-DD-short-slug (replace the template's YYYY-MM-DD with today's date)")
    if spec["approved"] is not False:
        probs.append("approved must be false")
    if not (MIN_DUR <= spec["duration"] <= MAX_DUR):
        probs.append(f"reel is {spec['duration']:.1f}s; must be {MIN_DUR}-{MAX_DUR}s (add or remove beats)")
    cap = spec["caption"]
    tags = re.findall(r"#\w+", cap)
    if not 3 <= len(tags) <= 8:
        probs.append(f"Instagram caption has {len(tags)} hashtags; use 3-8")
    if len(cap) > 2200:
        probs.append("Instagram caption over 2200 characters")
    low = (cap + " " + json.dumps(brief)).lower()
    for b in BANNED:
        if b in low:
            probs.append(f"banned phrase {b!r} (Chalkwise isn't public yet / no medical claims)")
    reel = R.Reel(json.loads(json.dumps(spec)))
    probs += ["pacing: " + w for w in reel.pacing_report()]
    page = 0
    boxes = []  # (page, t0, box, text)
    for e in reel.events:
        if e["type"] == "clear":
            page += 1
            continue
        if e["type"] in ("write", "count"):
            txt = e.get("text", "")
            if any(ord(ch) > 126 for ch in txt):
                probs.append(f"{e['t']:.1f}s board text must be plain ASCII (use ~ for approx, sqrt, x^2): {txt!r}")
            bx = text_box(e) if e["type"] == "write" else text_box(dict(e, text=e.get("prefix", "") + e.get("fmt", "{:.0f}").format(e["to"]) + e.get("suffix", "")))
            txt = txt or "(counter)"
            if bx[0] < 20 or bx[2] > 1060:
                probs.append(f"{e['t']:.1f}s text runs off the side (x {bx[0]:.0f}..{bx[2]:.0f}, keep 20..1060): {txt!r}; "
                             f"shorten it, lower size, or move x")
            if bx[1] < 520 or bx[3] > 1560:
                probs.append(f"{e['t']:.1f}s text outside the board area (y {bx[1]:.0f}..{bx[3]:.0f}, keep 520..1560): {txt!r}")
            for (pg, t0, ob, otxt) in boxes:
                if pg == page and overlap(bx, ob):
                    probs.append(f"{e['t']:.1f}s text {txt!r} overlaps {otxt!r} (written at {t0:.1f}s); move one of them")
            boxes.append((page, e["t"], bx, txt))
        elif e["type"] == "caption":
            if any(ord(ch) > 0x2000 for ch in e["text"]):
                probs.append(f"{e['t']:.1f}s on-screen caption has emoji/symbols the caption font can't draw: {e['text']!r}")
        else:
            pts = []
            for k in ("points",):
                pts += e.get(k, [])
            for k in ("c", "from", "to"):
                if k in e:
                    pts.append(e[k])
            for p in pts:
                if not (20 <= p[0] <= 1060 and 500 <= p[1] <= 1580):
                    probs.append(f"{e['t']:.1f}s {e['type']} point {p} outside the board area (x 20..1060, y 500..1580)")
                    break
    return probs


def contact_sheet(out_png, n_frames=10):
    import cv2, numpy as np, glob
    fs = sorted(glob.glob("/tmp/chalkwise_preview_*.png"))
    if not fs:
        return
    idx = [round(i * (len(fs) - 1) / (n_frames - 1)) for i in range(n_frames)]
    ims = [cv2.resize(cv2.imread(fs[i]), (360, 640)) for i in idx]
    for im, i in zip(ims, idx):
        cv2.putText(im, f"{i}s", (300, 625), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 1, cv2.LINE_AA)
    cv2.imwrite(out_png, np.vstack([np.hstack(ims[:5]), np.hstack(ims[5:])]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("brief")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--slot", type=int, choices=SLOTS, help="post today at this hour IST (11, 15, 19 or 23)")
    a = ap.parse_args()
    brief = json.load(open(a.brief))
    if a.slot:
        brief["post_after"] = slot_time(a.slot)
    for k in ("id", "topic", "hook_type", "format", "caption", "hook", "beats"):
        if k not in brief:
            raise SystemExit(f"FAIL: brief is missing {k!r} (see BRIEF_FORMAT.md)")
    try:
        spec = build(brief)
    except (KeyError, ValueError, TypeError) as ex:
        raise SystemExit(f"FAIL: could not build the brief: {ex!r} (check component names and args in LIBRARY.md)")
    os.makedirs(os.path.join(HERE, "scripts", "queue"), exist_ok=True)
    spec_path = os.path.join(HERE, "scripts", "queue", spec["id"] + ".json")
    json.dump(spec, open(spec_path, "w"), indent=1, ensure_ascii=False)
    probs = check(spec, brief)
    print(f"spec: scripts/queue/{spec['id']}.json  duration {spec['duration']:.1f}s  posts after {spec['post_after']}")
    if not a.no_render:
        os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
        for f in os.listdir("/tmp"):
            if f.startswith("chalkwise_preview_"):
                os.remove(os.path.join("/tmp", f))
        mp4 = os.path.join(HERE, "out", spec["id"] + ".mp4")
        r = subprocess.run([sys.executable, os.path.join(HERE, "render.py"), spec_path, mp4, "--preview"],
                           capture_output=True, text=True)
        if r.returncode:
            probs.append("render failed: " + r.stderr.strip()[-600:])
        else:
            sheet = os.path.join(HERE, "out", spec["id"] + "_sheet.png")
            contact_sheet(sheet)
            print(f"video: out/{spec['id']}.mp4\nsheet: out/{spec['id']}_sheet.png  (LOOK AT IT before pushing)")
    if probs:
        print(f"\nFAIL: {len(probs)} problem(s). Fix the brief and run make.py again:")
        for p in probs:
            print(" -", p)
        sys.exit(1)
    print("\nPASS")


if __name__ == "__main__":
    main()
