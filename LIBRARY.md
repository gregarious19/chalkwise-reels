# Component library

Generated from `components.py` by `python3 library/gen_doc.py`. Do not edit by hand.

Use a component in a brief's `show` list as `{"component": "<name>", ...args}`. Times are handled by
`make.py`; you only give content and positions. Canvas is 1080 x 1920; keep board content in
x 60-1000, y 560-1500. Captions are added by the beat, not by components.

Visual reference: `library/gallery.png` (every component) and the icon page of `library/gallery.json`.

## Components

### `icon`

Hand-drawn icon. args: name, at [x,y] (centre), size (half-width px, default 70), color, w, d.

### `person`

Stick figure with optional name. args: at [x,y] (feet centre), size (height px, default 260), color, label, label_color, mood ('happy'|'sad'|'neutral').

### `hook`

Opening card (a brief's top-level "hook", not a show item). args: text (caption, max ~7 words), highlight,
sub (smaller grey line), until (default: long enough to read, min 3.5 s),
big (large handwritten word or symbol in the middle), big_color, big_size, circle (bool, default true),
icon (icon name instead of big), clear (bool, default true: wipe board at until).

### `outro`

Brand card (a brief's top-level "outro"; make.py adds it and its timing automatically), the last ~10 s. args: until (reel end), line1 (default
'no courses. no syllabus.'), line2 (default 'just ask. it draws + explains.'), caption, highlight,
caption2, highlight2, cta (pill text), clear (bool, default true).

### `captions`

A run of captions, timed automatically (caption_hold: 0.55 s per word, min 2.5 s) unless a line has "hold".
args: lines: [str | {text, highlight, hold, size}], y (default 330), size (default 70), gap (default 0).
In briefs, prefer one caption per beat; use this only for extra captions inside a beat.

### `formula`

Handwritten formula or key line. args: text, at [x,y] (centre if align center, default), size (default 64),
color, mark (substring to highlight), box (bool: draw a box round it), box_color, d.

### `numberline`

Number line with dots for a data set. args: id, y, values, color, label (written at left), x0 (default 290),
x1 (default 1000), min, max, ticks, dy (dot offset above line, default -40), r (dot radius, default 14),
stagger (s between dots, default 0.45), dots_at (start time of dots, default t+1.4).

### `dots`

Dots popping onto an existing numberline. args: on (numberline id), values, color, stagger (default 0.45),
dy (default -40), r (default 14).

### `bar_chart`

Bars growing from a baseline. args: bars [{label, value, color}], base (baseline y, default 1350),
x0, x1 (default 140..940), height (px for max value, default 600), max (default max value),
show_values (bool, default true), fmt (python format for values, default '{:g}'), suffix, stagger (default 0.7).

### `plot`

Axes with a plotted function. args: box [x0,y0,x1,y1] (plot area, default [140,700,960,1350]), expr (numpy in u,
e.g. 'exp(-u**2/2)'), u0, u1 (domain, default -3..3), ymax (expr value at top of box, default 1), color,
xlabel, ylabel, curve_at (start of curve, default t+1.2), curve_d (default 2.2).

### `flow`

Boxes joined by arrows, top to bottom (or left to right with direction 'row'). args: items [str],
at [x,y] (centre of first box, default [540,700]), gap (centre to centre, default 230), box_w (default 640),
box_h (default 130), size (text, default 52), colors (list), direction ('column'|'row'), step (s per box, default 1.8).

### `checklist`

List with ticks or crosses. args: items [str | {text, mark: 'check'|'cross'|'none', color}], at [x,y] (left, first row),
gap (default 120), size (default 54), mark (default 'check'), step (default 1.8).

### `vs`

Split board for comparisons. args: left, right (headers), left_color, right_color, y (header, default 640),
line_to (bottom of divider, default 1450).

### `progress`

Progress bar, e.g. 'Course: 12% complete'. args: pct (0-100), at [x,y] (left, centre line, default [140,900]),
w (default 800), h (default 70), color (fill, default red), label (written above), fill_d (default 1.6).

### `bubble`

Speech bubble with text. args: text, box [x0,y0,x1,y1], tail [x,y] (point the tail aims at), size (default 50), color.

### `reveal`

Wrong-answer reveal: cross out a wrong line, write the right one under it. args: wrong, right, at [x,y]
(centre of wrong line, default [540,850]), size (default 64), gap (default 170), pause (s before cross-out, default 2.5).

## Icons

For `{"component": "icon", "name": ...}` (and `hook`'s `icon`):

`battery`, `bolt`, `book`, `brain`, `calendar`, `cap`, `chai`, `chat`, `check`, `clock`, `coin`, `cross`, `dice`, `heart`, `lightbulb`, `lock`, `magnifier`, `phone`, `play`, `question`, `stack`, `star`, `target`, `trend_up`, `warning`

## Sound effects

Raw event `{"type": "sfx", "name": ...}` (most components already add their own):

`ding`, `whoosh`, `tick`, `success`, `thud`, `pop`, `swoosh_up`

## Raw events

Anything not covered by a component can be a raw event in `show` (see SPEC_FORMAT.md for fields):
`write`, `line`, `polyline`, `arrow`, `circle`, `ellipse`, `rect`, `underline`, `highlight`, `dot`, `curve`,
`bar`, `hbar`, `count`, `sfx`, `clear`. Its `t` is relative to when the item starts (usually leave it out).

## Pacing constants

- caption hold: 0.55 s per word (+0.12 s per digit), minimum 2.5 s
- handwriting: 0.09 s per character (max 3 s per line)
- rest after each beat's drawing: 1.2 s

## Adding a component

When a script needs a visual the library can't make, and it would be useful again:
1. Add `def c_<name>(a):` to `components.py`, returning a list of raw events, with a docstring listing its args and defaults.
2. Register it in `COMPONENTS`.
3. Run `python3 library/gen_doc.py` to refresh this file.
4. Use it in the brief and check the sheet from `make.py`.
If it's a one-off, use raw events in the brief instead.
