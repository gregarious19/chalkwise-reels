# Daily run (exact steps)

Do these in order. Each step says what to run and what "done" means.

**HARD RULE: never set a reel to approved, never run `approve.py approve`, and never post, unless the founder
has explicitly approved that specific reel in this conversation.**

## 1. Read (5 min)

Read `CONTENT_PLAYBOOK.md`, `BRIEF_FORMAT.md`, `LIBRARY.md`, `LEARNINGS.md` and `FEEDBACK.md`.
FEEDBACK.md is the founder's word: it outranks everything else.

## 2. Analyze

```
python3 analyze.py
python3 approve.py list
```

Done = you have the analyze output (results table, averages, suggestion) and the queue list.

## 3. Update LEARNINGS.md

Add one line at the top of the Log: `- **YYYY-MM-DD** — <results in one line>. <one learning, only if analyze.py shows
≥3 reels per variant; otherwise "not enough data">. Today: <topic>, <hook_type>, <format>.`
If analyze.py's averages now show a clear winner, update "Current best". Never invent numbers: copy them from
analyze.py.

## 4. Decide whether to make a reel

If `approve.py list` shows 2 or more reels waiting (not on hold), don't make a new one: skip to step 8.

## 5. Write the brief

1. Pick the hook_type and format from analyze.py's suggestion, and a topic from the playbook's topic bank that
   isn't in the "don't repeat" list.
2. Copy the closest template: `cp briefs/templates/<template>.json briefs/<YYYY-MM-DD>-<slug>.json`.
3. Edit the content per BRIEF_FORMAT.md. Keep it to 4–7 beats, one idea.
4. For every number on the board, run a quick Python check and confirm it's right.
5. If the story needs a visual the library doesn't have: use raw events. If it would be useful again, add a
   component (LIBRARY.md, "Adding a component").

## 6. Build and check

```
python3 make.py briefs/<id>.json
```

- If it prints FAIL, fix each listed problem in the **brief** (never hand-edit `scripts/queue/`) and run again.
  Repeat until PASS. If the reel is over 60 s, remove a beat; under 30 s, add one.
- When it prints PASS, open `out/<id>_sheet.png` with the Read tool and look at all 10 frames. Check: text readable,
  nothing cut off or overlapping, each frame makes sense, the board is never empty for long. Fix and rebuild
  if not.

Done = PASS and the sheet looks right.

## 7. Commit and push

```
git add -A
git commit -m "Queue <id>"
git push
```

(GitHub renders the final video with the handwriting font; that's the version that gets posted.)

## 8. Message the founder

Send `out/<id>.mp4` with SendUserFile (status proactive), then one SendUserMessage of at most 8 lines:

```
Yesterday: <one line from analyze.py, or "no data yet">
Learned: <one line, or "not enough data yet">
Today's reel: <topic> · hook: <hook_type> · <duration>s
Waiting for approval: <ids from approve.py list>
Reply "approve" to post it at 19:00 IST, or tell me what to change.
```

If anything was broken (API errors in analyze.py, failed render, expired token), add one line saying what and
how to fix it.

## 9. When the founder replies

- **"approve"** (or approves a named reel): `python3 approve.py approve <id>`, commit `Approve <id>`, push, and
  reply with when it will post (the next 19:00 IST after its post_after time).
- **Changes requested**: edit the brief, run make.py again until PASS, check the sheet, push, resend the video.
- **"hold" / "drop"**: `python3 approve.py hold <id>` or `python3 approve.py drop <id>`, commit, push.
- **Feedback on style or content**: add it, dated, at the top of FEEDBACK.md, commit, push.
- **"I posted it myself"**: `git mv scripts/queue/<id>.json scripts/posted/`, set `"posted": {"manual": true}` in
  it, commit, push. The insights job links it to the Instagram post.
