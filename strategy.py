#!/usr/bin/env python3
"""Numbers for the daily strategy review. Prints markdown; changes nothing.

    python3 strategy.py

Reads data/insights.json, scripts/posted/*.json and data/themes.json (topic -> theme).
For every posted reel: views at ~24 h (so young and old reels compare fairly), latest views,
hold rate, share+save rate, comment rate, like rate. Then breakdowns by theme, format, hook_type,
posting slot and length, each with n, how many are mature (48 h+), and the gap to the account median.

Verdict labels are mechanical, so the reviewer never has to guess:
  WORKS        >= 3 mature reels and median hold AND share+save both >= 1.15x the account median
  DOESN'T WORK >= 3 mature reels and median hold AND share+save both <= 0.85x the account median
  LEANING +/-  fewer reels, or only one metric clears the bar
  TOO EARLY    fewer than 2 reels with data
"""
import datetime, glob, json, os, statistics

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SLOTS = (11, 15, 19, 23)
MIN_MATURE = 3
UP, DOWN = 1.15, 0.85


def parse(ts):
    return datetime.datetime.fromisoformat(ts.replace("+0000", "+00:00").replace("Z", "+00:00"))


def nearest_slot(t):
    h = t.astimezone(IST).hour + t.astimezone(IST).minute / 60
    return f"{min(SLOTS, key=lambda s: abs(s - h)):02d}:00"


def load():
    db = json.load(open("data/insights.json")) if os.path.exists("data/insights.json") else {}
    themes = json.load(open("data/themes.json")) if os.path.exists("data/themes.json") else {}
    now = datetime.datetime.now(datetime.timezone.utc)
    rows = []
    for p in sorted(glob.glob("scripts/posted/*.json")):
        s = json.load(open(p))
        rec = db.get(s["id"], {})
        ts = (s.get("posted") or {}).get("timestamp") or rec.get("posted")
        t = parse(ts) if ts else None
        snaps = rec.get("snapshots", [])
        lat = rec.get("latest") or (snaps[-1] if snaps else {})
        v24 = None
        if t:
            for sn in snaps:
                if sn.get("fetched") and (parse(sn["fetched"]) - t).total_seconds() / 3600 >= 18:
                    v24 = sn.get("views")
                    break
        reach = lat.get("reach") or 0
        dur = s.get("duration") or 0
        awt = lat.get("ig_reels_avg_watch_time")
        topic = s.get("topic")
        rows.append({
            "id": s["id"], "topic": topic, "theme": themes.get(topic, "UNCLASSIFIED"),
            "format": s.get("format"), "hook_type": s.get("hook_type"),
            "slot": nearest_slot(t) if t else None,
            "length": "30-39s" if dur < 40 else ("40-49s" if dur < 50 else "50s+"),
            "duration": dur, "age_h": (now - t).total_seconds() / 3600 if t else None,
            "has_data": bool(lat), "views": lat.get("views"), "views_24h": v24,
            "hold": (awt / 1000 / dur) if (awt and dur) else None,
            "share_save": ((lat.get("shares") or 0) + (lat.get("saved") or 0)) / reach if reach else None,
            "comment": (lat.get("comments") or 0) / reach if reach else None,
            "like": (lat.get("likes") or 0) / reach if reach else None,
        })
    return rows, db.get("_account", []), themes


def pct(x):
    return "–" if x is None else f"{x * 100:.1f}%"


def med(xs):
    xs = [x for x in xs if x is not None]
    return statistics.median(xs) if xs else None


def ratio(a, b):
    return None if (a is None or not b) else a / b


def verdict(g, base_hold, base_ss):
    with_data = [r for r in g if r["has_data"] and r["hold"] is not None]
    mature = [r for r in with_data if (r["age_h"] or 0) >= 48]
    if len(with_data) < 2:
        return "TOO EARLY"
    rh, rs = ratio(med(r["hold"] for r in with_data), base_hold), ratio(med(r["share_save"] for r in with_data), base_ss)
    up = sum(1 for x in (rh, rs) if x is not None and x >= UP)
    down = sum(1 for x in (rh, rs) if x is not None and x <= DOWN)
    if len(mature) >= MIN_MATURE and up == 2:
        return "WORKS"
    if len(mature) >= MIN_MATURE and down == 2:
        return "DOESN'T WORK"
    if up > down:
        return "LEANING +"
    if down > up:
        return "LEANING −"
    return "NO CLEAR DIFFERENCE"


def main():
    rows, acct, themes = load()
    data = [r for r in rows if r["has_data"] and r["hold"] is not None]
    base = {k: med(r[k] for r in data) for k in ("hold", "share_save", "comment", "like", "views_24h")}

    print(f"# Strategy numbers ({datetime.datetime.now(IST):%Y-%m-%d %H:%M} IST)\n")
    if acct:
        last = acct[-1]
        print(f"Insights last fetched: {last.get('fetched')} UTC. Followers: {last.get('followers_count')} "
              f"(first record {acct[0].get('followers_count')}).\n")
    print("## Every reel\n")
    print("| reel | theme | format | hook | slot | len | age | views@24h | views now | hold | share+save | comments | likes |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        age = "–" if r["age_h"] is None else f"{r['age_h']:.0f}h"
        vn = r["views"] if r["has_data"] else "no data yet"
        print(f"| {r['id']} | {r['theme']} | {r['format']} | {r['hook_type']} | {r['slot']} | {r['duration']:.0f}s | {age} | "
              f"{r['views_24h'] if r['views_24h'] is not None else '–'} | {vn} | {pct(r['hold'])} | {pct(r['share_save'])} | "
              f"{pct(r['comment'])} | {pct(r['like'])} |")
    print(f"\nAccount medians ({len(data)} reels with data): hold {pct(base['hold'])}, share+save {pct(base['share_save'])}, "
          f"comments {pct(base['comment'])}, likes {pct(base['like'])}, views@24h {base['views_24h'] or '–'}.\n")

    unc = sorted({r["topic"] for r in rows if r["theme"] == "UNCLASSIFIED" and r["topic"]})
    if unc:
        print(f"**Unclassified topics (add them to data/themes.json, then rerun):** {', '.join(unc)}\n")

    for key, label in (("theme", "Theme"), ("format", "Format"), ("hook_type", "Hook"),
                       ("slot", "Posting slot (IST)"), ("length", "Length")):
        groups = {}
        for r in rows:
            groups.setdefault(r[key], []).append(r)
        print(f"## By {label}\n")
        print("| value | reels | with data | mature 48h+ | med views@24h | med hold (×median) | med share+save (×median) | med comments | verdict |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for k, g in sorted(groups.items(), key=lambda kv: str(kv[0])):
            d = [r for r in g if r["has_data"] and r["hold"] is not None]
            m = [r for r in d if (r["age_h"] or 0) >= 48]
            h, s = med(r["hold"] for r in d), med(r["share_save"] for r in d)
            rh, rs = ratio(h, base["hold"]), ratio(s, base["share_save"])
            v24 = med(r["views_24h"] for r in g)
            print(f"| {k} | {len(g)} | {len(d)} | {len(m)} | {v24 if v24 is not None else '–'} | "
                  f"{pct(h)} ({'–' if rh is None else f'{rh:.2f}×'}) | {pct(s)} ({'–' if rs is None else f'{rs:.2f}×'}) | "
                  f"{pct(med(r['comment'] for r in d))} | {verdict(g, base['hold'], base['share_save'])} |")
        print()


if __name__ == "__main__":
    main()
