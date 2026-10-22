# Daily run (Claude)

Run once a day, ideally in the morning IST, after the 08:00 insights pull.

**Hard rule: never post, and never set `"approved": true`, unless the founder has explicitly approved that specific reel in conversation.** New specs are always written with `"approved": false`.

1. **Read** `CONTENT_PLAYBOOK.md`, `SPEC_FORMAT.md`, `LEARNINGS.md`, `FEEDBACK.md`, `data/insights.json`, and list `scripts/queue/` and `scripts/posted/`.
2. **Analyze.** For every posted reel at least 48 h old, compute hold rate, share+save rate, comment rate and views (definitions in the playbook) with a short Python script. Group by `hook_type`, `format`, topic area and duration. Note anything in `FEEDBACK.md` from the founder; it outranks the numbers.
3. **Update `LEARNINGS.md`.** Add one dated entry: yesterday's numbers in one line, any conclusion that now has enough evidence (≥3 reels per variant), and what today's reel tests. Keep the "Current best" section at the top accurate. Roll entries older than 30 days into a one-paragraph monthly summary.
4. **Decide today's reel.** If two or more reels are already queued and not on hold, don't write another; skip to step 8. Otherwise pick hook family, format, topic and length per the 70/30 rule in the playbook. Don't repeat a topic posted in the last 14 days.
5. **Write the spec** in `scripts/queue/<YYYY-MM-DD>-<slug>.json` with `"approved": false` and `post_after` = tomorrow 13:00 UTC. Write the caption sequence first (it sets the pacing: ~0.4 s per word, min 1.5 s each), then the board events. No voiceover.
6. **Check it.** Recompute every on-screen number in Python. Render locally (`python3 render.py <spec> out/<id>.mp4 --preview`), build a contact sheet of ~10 preview frames, look at it, and fix overlaps, off-screen text, or empty stretches.
7. **Commit and push** to `main` (message: `Queue <id>`). The render workflow builds the final video with the handwriting font.
8. **Tell the founder** (SendUserMessage + SendUserFile of the local render, status proactive): one line on yesterday's results, one line on what was learned, today's reel topic and hook, and ask for approval (it posts at the next 19:00 IST slot only once approved). Also list any older reels still waiting for approval. Keep it under 8 lines.

If the Instagram token or anything else is broken (failed workflow runs, `_errors` in insights), say so plainly in step 8 with the fix.
