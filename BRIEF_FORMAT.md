# Brief format

A brief is the only file you write for a new reel: `briefs/<YYYY-MM-DD>-<slug>.json`. It holds content, not timing.
`python3 make.py briefs/<id>.json` turns it into a timed spec, checks it, and renders it.

**Start by copying a template** from `briefs/templates/` that matches the format you picked. Change the content;
keep the structure.

```json
{
  "id": "2026-10-23-mean-vs-median",
  "topic": "mean vs median",
  "hook_type": "myth bust",
  "format": "two-friends comparison",
  "caption": "Instagram caption text...\n\n#tag1 #tag2 #tag3",
  "hook": {"text": "Average salary is a lie.", "highlight": ["a lie."], "sub": "Here's why.", "big": "avg?"},
  "beats": [
    {"caption": "5 friends. 4 earn 30k.", "highlight": ["30k."],
     "show": [ {"component": "bar_chart", "bars": [{"label": "A", "value": 30}, ...]} ]},
    {"caption": "One earns 10 lakh.", "show": [ ... ], "clear_after": true}
  ],
  "outro": {}
}
```

## Fields

| Field | Rules |
| --- | --- |
| `id` | `YYYY-MM-DD-short-slug`, today's date, lowercase, hyphens. Same as the file name. |
| `topic` | The one idea taught. Must not repeat a topic from the last 14 days (`analyze.py` lists them). |
| `hook_type` | One of: speed promise, course pain, prerequisite wall, everyday mystery, myth bust, wrong-answer reveal, curiosity jump. |
| `format` | Story device, e.g. two-friends comparison, wrong-answer reveal, course pain, everyday object, step-by-step build. |
| `caption` | Instagram caption: 2–4 short paragraphs, end with "Follow for one idea a day ✏️", then 3–8 hashtags. Emoji are fine here. |
| `hook` | Opening card. `text` (max ~7 words, a promise or a question), `highlight` (exact words to put on yellow), optional `sub`, and either `big` (short handwritten text, max ~8 characters, e.g. `"SD = ?"`) or `icon` (an icon name). |
| `beats` | 4–7 beats. Each beat = one caption + what gets drawn while it's on screen. |
| `outro` | Usually `{}` (standard brand card). Optional overrides: `line1`, `line2`, `caption`, `caption2`, `cta`. |

## A beat

| Field | Rules |
| --- | --- |
| `caption` | What the viewer reads. Max ~10 words. Plain words; numbers OK. No emoji. |
| `highlight` | List of exact phrases from the caption to put on yellow (copy them exactly, including punctuation at the end). |
| `show` | List of things to draw, in order. Each is a component (`{"component": "...", ...}`, see LIBRARY.md) or a raw event (`{"type": "write", ...}`). Each item starts when the previous one finishes. |
| `show[i].with_previous` | `true` = start at the same time as the previous item instead of after it. |
| `show[i].delay` | Extra seconds to wait before this item. |
| `clear_after` | `true` = wipe the board after this beat (start a fresh page). Use when the board is full or the idea changes. |
| `min_hold` | Optional minimum seconds for this beat (for a dramatic pause). |

## Board layout rules

- Board area: **x 60–1000, y 560–1500.** Captions are above it (automatic).
- Board text: **plain ASCII only** (`~` for approximately, `x` or `*` for times, `sqrt`, `^2`). Sizes 44–70; about 0.5 × size px per character, so a 30-character line at size 46 is ~700 px wide.
- Stack lines at least 1.4 × size apart (size 60 → 85 px).
- One page holds 3–5 things. Then `clear_after`.
- Every number on the board must be computed in Python first. Write the check in your notes.

## What make.py checks (fix the brief until it prints PASS)

- id format, `approved` false, total length 30–60 s
- caption hashtags 3–8, no banned phrases ("download now", "try it today", medical claims…)
- every caption shown long enough to read; no caption over 12 words; handwriting not too fast
- board text ASCII, inside the board area, not overlapping other text on the same page
- shapes inside the board area
- the video renders

Then **look at `out/<id>_sheet.png`** yourself: is every frame readable, nothing awkward, does the story make sense?
