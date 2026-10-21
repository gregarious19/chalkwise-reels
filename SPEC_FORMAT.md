# Reel spec format

One JSON file per reel in `scripts/queue/`, named `YYYY-MM-DD-slug.json`. `render.py` turns it into a 1080×1920, 30 fps MP4.

## Top-level fields

| Field | Meaning |
| --- | --- |
| `id` | Same as the file name without `.json`. Used for the release tag `reel-<id>`. |
| `topic` | The concept taught (e.g. "standard deviation"). |
| `hook_type` | Hook family from the playbook (e.g. "speed promise", "course pain", "prerequisite wall", "myth bust", "everyday mystery"). Used to compare performance. |
| `format` | Story device (e.g. "two-friends comparison", "everyday object", "wrong-answer reveal"). |
| `post_after` | ISO time with offset. The post workflow publishes at 19:00 IST once this has passed. |
| `hold` | `true` keeps it in the queue without posting. |
| `duration` | Seconds (30 to 50). |
| `voiceover` | List of `{"t": seconds, "text": "..."}` lines. Spoken by Deepgram if `DEEPGRAM_API_KEY` is set. Each line must finish before the next `t` (about 2.6 words per second). |
| `caption` | Instagram caption, hashtags included (max 2,200 chars, max 30 hashtags; use 5 to 8). |
| `events` | The timeline (below). |

## Canvas and safe zone

- Canvas 1080 wide × 1920 tall, origin top-left.
- Instagram covers roughly y < 200 (top bar), y > 1550 (caption and username), and x > 950 between y 1000 and 1700 (like/comment buttons). Keep board content within **x 40–1000, y 560–1500**.
- Captions sit at **y ≈ 330** (one or two lines). A second caption line can go at y ≈ 480.

## Event types

Every event has `t` (start, seconds) and optionally `d` (duration; sensible defaults). Board events persist until a `clear`.

| type | fields | notes |
| --- | --- | --- |
| `caption` | `text`, `until`, `y`, `size` (60–84), `highlight` (list of exact phrases to put on yellow), `color`, `box` (background color, e.g. "yellow") | Pop-in subtitle. Not drawn on the board; disappears at `until`. |
| `write` | `text`, `x`, `y` (vertical centre), `size` (40–190), `color`, `align` ("center" makes `x` the centre), `mark` (substring to marker-highlight after writing) | Written left to right with the marker. ASCII only: use `~` not `≈`, `sqrt` not `√`, `x^2` style. Default duration 0.055 s per character. |
| `line` / `polyline` | `points` [[x,y],...], `color`, `w` | Hand-drawn wobble. |
| `arrow` | `from`, `to`, `color`, `w`, `head` | |
| `circle` | `c` [x,y], `r` | Hand-drawn loop. |
| `ellipse` | `c`, `rx`, `ry` | |
| `rect` | `box` [x0,y0,x1,y1] | |
| `underline` | `x0`, `x1`, `y` | |
| `highlight` | `box`, `color` (default yellow), `alpha` | Translucent marker swipe. |
| `numberline` | `id`, `x0`, `x1`, `y`, `min`, `max`, `ticks` | Gives an axis other events can place values on. |
| `dot` | `on` (numberline id) + `v` + `dy`, or `c` [x,y]; `r`, `color` | Pops in. |
| `curve` | `x0`, `x1`, `y` (baseline), `expr` in variable `u` (numpy; e.g. `exp(-u**2/2)`), `u0`, `u1`, `height` | Plots a function. |
| `clear` | | Fresh-paper swipe, wipes the board. |

Colors: `ink`, `blue`, `orange`, `green`, `red`, `purple`, `grey`, `yellow`, `white`, or `#rrggbb`. Use one accent color per character or idea and keep it consistent within a reel.

## Checks before queueing

1. Render locally: `python3 render.py scripts/queue/<id>.json out/<id>.mp4 --preview` and look at the frames.
2. Every number on screen recomputed in Python.
3. No caption overlaps board content; nothing in the Instagram-covered zones.
