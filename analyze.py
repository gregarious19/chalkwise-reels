#!/usr/bin/env python3
"""Performance summary for the daily run. Prints markdown; changes nothing.

    python3 analyze.py

Reads data/insights.json and scripts/posted/*.json. For each posted reel: views, hold rate,
share+save rate, comment rate. Then averages per hook_type, format and length bucket (only reels
at least 48 h old count toward averages), and a suggestion for today's reel per the 70/30 rule
in CONTENT_PLAYBOOK.md.
"""
import datetime, glob, json, os, random

HOOKS = ["speed promise", "course pain", "prerequisite wall", "everyday mystery", "myth bust",
         "wrong-answer reveal", "curiosity jump"]
MIN_PER_VARIANT = 3


def load():
    db = json.load(open("data/insights.json")) if os.path.exists("data/insights.json") else {}
    rows = []
    now = datetime.datetime.now(datetime.timezone.utc)
    for p in sorted(glob.glob("scripts/posted/*.json")):
        s = json.load(open(p))
        rec = db.get(s["id"], {})
        lat = rec.get("latest", {})
        ts = (s.get("posted") or {}).get("timestamp")
        age_h = None
        if ts:
            try:
                age_h = (now - datetime.datetime.fromisoformat(ts.replace("+0000", "+00:00"))).total_seconds() / 3600
            except ValueError:
                pass
        reach = lat.get("reach") or 0
        dur = s.get("duration") or 0
        awt = lat.get("ig_reels_avg_watch_time")
        rows.append({
            "id": s["id"], "topic": s.get("topic"), "hook_type": s.get("hook_type"), "format": s.get("format"),
            "duration": dur, "len_bucket": "30-39s" if dur < 40 else ("40-49s" if dur < 50 else "50s+"),
            "age_h": age_h, "views": lat.get("views"), "reach": reach,
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
    for key in ("hook_type", "format", "len_bucket"):
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

    print("## Suggestion for today\n")
    recent_topics = [r["topic"] for r in rows[-14:]]
    counts = {h: sum(1 for r in rows if r["hook_type"] == h) for h in HOOKS}
    if "hook_type" in best and random.Random(datetime.date.today().toordinal()).random() < 0.7:
        print(f"- EXPLOIT (70%): use the best hook so far: **{best['hook_type']}**"
              + (f", format **{best['format']}**" if "format" in best else "")
              + (f", length **{best['len_bucket']}**" if "len_bucket" in best else "") + ".")
        print("- Change one thing only: the topic.")
    else:
        least = min(HOOKS, key=lambda h: (counts[h], HOOKS.index(h)))
        print(f"- EXPLORE: try hook **{least}** (used {counts[least]} times so far)."
              + (f" Keep the best format so far: **{best['format']}**." if "format" in best else ""))
    print(f"- Don't repeat these recent topics: {', '.join(t for t in recent_topics if t) or 'none'}.")


if __name__ == "__main__":
    main()
