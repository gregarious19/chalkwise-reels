# Daily run (exact steps)

Do these in order. Each step says what to run and what "done" means.

**Every day: 4 reels, posted automatically at 11:00, 15:00, 19:00 and 23:00 IST the same day.** You approve each
reel yourself, but only after `make.py` prints PASS and you've looked at its contact sheet and it's right. Never
approve a reel that failed a check or that you haven't looked at. Never post by hand: post.yml does it. If the
founder has put a `PAUSED` file in the repo or held a reel, leave that alone.

Work fast: the 11:00 reel must be pushed and approved by about 10:30 so GitHub can render it in time. Do it first.

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
≥3 reels per variant; otherwise "not enough data">. Today: <4 topics with their hook_types>.`
If analyze.py's averages now show a clear winner (hook, format, length or posting slot), update "Current best".
Never invent numbers: copy them from analyze.py.

## 4. Plan today's 4 reels

Use analyze.py's "Plan for today's 4 reels": it gives one line per slot (11, 15, 19, 23) saying which hook to use,
based on how past reels performed. Follow it. Pick 4 different topics from the playbook's topic bank, none in the
"don't repeat" list.

Skip a slot only if a reel for that slot today is already in the queue (`approve.py list`).

## 5–7. For each slot, in order 11 → 15 → 19 → 23, make one reel

### Write the brief

1. Copy the closest template: `cp briefs/templates/<template>.json briefs/<YYYY-MM-DD>-<slug>.json`.
2. Edit the content per BRIEF_FORMAT.md, using that slot's hook_type from the plan. Keep it to 4–7 beats, one idea.
3. For every number on the board, run a quick Python check and confirm it's right.
4. If the story needs a visual the library doesn't have: use raw events. If it would be useful again, add a
   component (LIBRARY.md, "Adding a component").

### Build and check

```
python3 make.py briefs/<id>.json --slot <11|15|19|23>
```

- If it prints FAIL, fix each listed problem in the **brief** (never hand-edit `scripts/queue/`) and run again.
  Repeat until PASS. If the reel is over 60 s, remove a beat; under 30 s, add one.
- When it prints PASS, open `out/<id>_sheet.png` with the Read tool and look at all 10 frames. Check: text readable,
  nothing cut off or overlapping, each frame makes sense, the board is never empty for long, every number is right.
  Fix and rebuild if not.

### Approve, commit and push

Only after PASS **and** the sheet looks right:

```
python3 approve.py approve <id>
git add -A
git commit -m "Queue <id> for <HH>:00 IST"
git push
```

Push each reel as soon as it's approved, so GitHub starts rendering it (GitHub renders the final video with the
handwriting font; that's the version that gets posted). If you can't get a reel to PASS and look right within
about 20 minutes, drop it (`python3 approve.py drop <id>`), move on to the next slot, and say so in the message.

## 8. Message the founder

Send the 4 `out/<id>.mp4` files with SendUserFile (status proactive), then one SendUserMessage of at most 10 lines:

```
Yesterday: <one line from analyze.py, or "no data yet">
Learned: <one line, or "not enough data yet">
Today, posting automatically:
11:00 <topic> · <hook_type> · <duration>s
15:00 …
19:00 …
23:00 …
Reply "hold <id>" to stop one, or tell me what to change.
```

If anything was broken (API errors in analyze.py, failed render, expired token, a dropped slot), add one line saying
what and how to fix it.

## 9. When the founder replies

- **"hold <id>"** / **"drop <id>"**: `python3 approve.py hold <id>` or `python3 approve.py drop <id>`, commit, push.
  If it already posted, say so.
- **Changes requested**: edit the brief, run make.py again (same `--slot`) until PASS, check the sheet, approve, push,
  resend the video. If its slot has already passed it goes out at the next slot.
- **"pause everything"**: add an empty `PAUSED` file at the repo root, commit, push.
- **Feedback on style or content**: add it, dated, at the top of FEEDBACK.md, commit, push.
- **"I posted it myself"**: `git mv scripts/queue/<id>.json scripts/posted/`, set `"posted": {"manual": true}` in
  it, commit, push. The insights job links it to the Instagram post.
