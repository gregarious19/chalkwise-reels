#!/usr/bin/env python3
"""Change a queued reel's status. ONLY run 'approve' when the founder has explicitly approved that reel.

    python3 approve.py list                 show the queue
    python3 approve.py approve <id>         founder said "approve" -> it posts at the next 19:00 IST slot
    python3 approve.py hold <id>            keep it in the queue, don't post
    python3 approve.py unhold <id>
    python3 approve.py drop <id>            founder rejected it -> delete the spec (brief stays)

Then commit and push.
"""
import glob, json, os, sys


def path(i):
    p = f"scripts/queue/{i}.json"
    if not os.path.exists(p):
        raise SystemExit(f"no queued reel {i!r}. Queue: " + ", ".join(os.path.basename(x)[:-5] for x in sorted(glob.glob('scripts/queue/*.json'))))
    return p


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        for p in sorted(glob.glob("scripts/queue/*.json")):
            s = json.load(open(p))
            state = "HOLD" if s.get("hold") else ("APPROVED" if s.get("approved") is True else "waiting for approval")
            print(f"{s['id']}: {state}; posts after {s.get('post_after')}; {s.get('duration')}s; topic {s.get('topic')}")
        return
    cmd, i = sys.argv[1], sys.argv[2]
    p = path(i)
    if cmd == "drop":
        os.remove(p)
        print(f"removed {p}")
        return
    s = json.load(open(p))
    if cmd == "approve":
        s["approved"] = True
        s.pop("hold", None)
    elif cmd == "hold":
        s["hold"] = True
    elif cmd == "unhold":
        s.pop("hold", None)
    else:
        raise SystemExit(__doc__)
    json.dump(s, open(p, "w"), indent=1, ensure_ascii=False)
    print(f"{i}: {cmd} done. Now: git add -A && git commit -m '{cmd.capitalize()} {i}' && git push")


if __name__ == "__main__":
    main()
