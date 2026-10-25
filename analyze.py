#!/usr/bin/env python3
"""Performance summary for the daily run. Prints markdown; changes nothing.

    python3 analyze.py

Reads data/insights.json and scripts/posted/*.json. For each posted reel: views, hold rate,
share+save rate, comment rate. Then averages per hook_type, format, length bucket and posting slot
(only reels at least 48 h old count toward averages), and a plan for today's 5 reels (one per slot)
per the 70/30 rule in CONTENT_PLAYBOOK.md: 3 use the best hook so far, 1 explores.
"""
import datetime, glob, json, os, random

HOOKS = ["speed promise", "course pain", "prerequisite wall", "everyday mystery", "myth bust",
         "wrong-answer reveal", "curiosity jump"]
MIN_PER_VARIANT = 3
SLOTS = (11, 15, 19, 23, 2)  # IST posting hours in posting order; must match make.py and post.yml
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def slot_of(ts):
    """Posting slot (IST hour) a reel went out in: the latest slot at or before its post time."""
    h = ts.astimezone(IST).hour
    past = sorted(x for x in SLOTS if x <= h)
    return f"{past[-1] if past else max(SLOTS):02d}:00"


def load():
    db = json.load(open("data/insights.json")) if os.path.exists("data/insights.json") else {}
    rows = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for p in sorted(glob.glob("scripts/posted/*.json")):
        s = json.load(open(p))
        rec = db.get(s["id"], {})
        lat = rec.get("latest", {})
        ts = (s.get("posted") or {}).get("timestamp")
        age_h, slot = None, None
        if ts:
            try:
                t = datetime.datetime.fromisoformat(ts.replace("+0000", "+00:00"))
                age_h = (now - t).total_seconds() / 3600
                slot = slot_of(t)
            except ValueError:
                pass
        reach = lat.get("reach") or 0
        dur = s.get("duration") or 0
        awt = lat.get("ig_reels_avg_watch_time")
        rows.append({
            "id": s["id"], "topic": s.get("topic"), "hook_type": s.get("hook_type"), "format": s.get("format"),
            "duration": dur, "len_bucket": "30-39s" if dur < 40 else ("40-49s" if dur < 50 else "50s+"),
            "age_h": age_h, "slot": slot, "views": lat.get("views"), "reach": reach,
            "hold": (awt / 1000 / dur) if (awt and dur) else None,
            "share_save": ((lat.get("shares") or 0) + (lat.get("saved") or 0)) / reach if reach else None,
            "comment": (lat.get("comments") or 0) / reach if reach else None,
            "errors": [e for snap in rec.get("snapshots", [])[-1:] for e in snap.get("_errors", [])],
            "has_data": bool(lat),
        })
    acct = db.get("_account", [])
    return rows, acct


def pct(x):
    return "–" if x is None else f"{x * 100:.1f}%"


def main():
    rows, acct = load()
    print("## Reels\n")
    if not rows:
        print("No posted reels yet.\n")
    else:
        print("| reel | hook | format | len | age | views | hold | share+save | comments |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for r in rows:
            age = "–" if r["age_h"] is None else f"{r['age_h']:.0f}h"
            v = "no data yet" if not r["has_data"] else (r["views"] if r["views"] is not None else "–")
            print(f"| {r['id']} | {r['hook_type']} | {r['format']} | {r['duration']:.0f}s | {age} | {v} | {pct(r['hold'])} | "
                  f"{pct(r['share_save'])} | {pct(r['comment'])} |")
        print()
    if len(acct) >= 1:
        f0, f1 = acct[0].get("followers_count"), acct[-1].get("followers_count")
        print(f"Followers: {f1} (first record {f0}, change {f1 - f0 if None not in (f0, f1) else '–'})\n")
    errs = [(r["id"], e) for r in rows for e in r["errors"]]
    if errs:
        print("## API problems\n")
        for i, e in errs:
            print(f"- {i}: {e}")
        print()

    mature = [r for r in rows if r["has_data"] and (r["age_h"] or 0) >= 48 and r["hold"] is not None]
    print(f"## Averages (reels at least 48 h old: {len(mature)})\n")
    best = {}
    for key in ("hook_type", "format", "len_bucket", "slot"):
        groups = {}
        for r in mature:
            groups.setdefault(r[key], []).append(r)
        if not groups:
            continue
        print(f"**By {key}**\n")
        print("| value | reels | avg hold | avg share+save | avg comments |")
        print("| --- | --- | --- | --- | --- |")
        ranked = []
        for k, g in groups.items():
            avg = lambda f: sum(x[f] or 0 for x in g) / len(g)
            ranked.append((avg("hold"), k, len(g)))
            print(f"| {k} | {len(g)} | {pct(avg('hold'))} | {pct(avg('share_save'))} | {pct(avg('comment'))} |")
        print()
        ok = [x for x in ranked if x[2] >= MIN_PER_VARIANT]
        if ok:
            best[key] = max(ok)[1]
    if not mature:
        print("Not enough data yet (reels need 48 h).\n")

    print(f"## Plan for today's {len(SLOTS)} reels\n")
    recent_topics = [r["topic"] for r in rows[-28:]]
    counts = {h: sum(1 for r in rows if r["hook_type"] == h) for h in HOOKS}
    explore = sorted(HOOKS, key=lambda h: (counts[h], HOOKS.index(h)))  # least-used hooks first
    keep = (f", format **{best['format']}**" if "format" in best else "") + \
           (f", length **{best['len_bucket']}**" if "len_bucket" in best else "")
    day = datetime.date.today().toordinal()
    # About a quarter of the slots (at least 1) explore, spread out and rotated so no slot always gets the experiment
    n_explore = max(1, len(SLOTS) // 4)
    explore_slots = {SLOTS[(day + k * (len(SLOTS) // n_explore)) % len(SLOTS)] for k in range(n_explore)}
    if "hook_type" in best:
        explore = [h for h in explore if h != best["hook_type"]]
    plan = []
    for h in SLOTS:
        if "hook_type" in best and h not in explore_slots:
            plan.append(f"- **{h:02d}:00 IST** — EXPLOIT: hook **{best['hook_type']}**{keep}. Change only the topic.")
        else:
            hook = explore.pop(0)
            explore.append(hook)  # cycle if slots outnumber hooks
            plan.append(f"- **{h:02d}:00 IST** — EXPLORE: try hook **{hook}** (used {counts[hook]} times so far)"
                        + (f"; keep format **{best['format']}**" if "format" in best else "") + ".")
    print("\n".join(plan))
    if "hook_type" not in best:
        print("\n(No hook has 3+ mature reels yet, so every slot explores, cycling through the hooks.)")
    if "slot" in best:
        print(f"\nBest posting slot so far: **{best['slot']}** IST.")
    print(f"\n- {len(SLOTS)} different topics today. Don't repeat these recent topics: {', '.join(t for t in recent_topics if t) or 'none'}.")

if __name__ == "__main__":
    main()
