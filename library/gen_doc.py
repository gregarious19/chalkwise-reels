#!/usr/bin/env python3
"""Regenerate LIBRARY.md from components.py docstrings. Run after adding or changing a component."""
import os, sys, inspect
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import components as C, render as R
out = ["# Component library", "",
       "Generated from `components.py` by `python3 library/gen_doc.py`. Do not edit by hand.", "",
       "Use a component in a brief's `show` list as `{\"component\": \"<name>\", ...args}`. Times are handled by",
       "`make.py`; you only give content and positions. Canvas is 1080 x 1920; keep board content in",
       "x 60-1000, y 560-1500. Captions are added by the beat, not by components.", "",
       "Visual reference: `library/gallery.png` (every component) and the icon page of `library/gallery.json`.", "",
       "## Components", ""]
for name, fn in C.COMPONENTS.items():
    doc = inspect.getdoc(fn) or ""
    out += [f"### `{name}`", "", doc, ""]
out += ["## Icons", "", "For `{\"component\": \"icon\", \"name\": ...}` (and `hook`'s `icon`):", "",
        ", ".join(f"`{n}`" for n in sorted(C.ICONS)), "",
        "## Sound effects", "", "Raw event `{\"type\": \"sfx\", \"name\": ...}` (most components already add their own):", "",
        ", ".join(f"`{n}`" for n in R.SFX_NAMES), "",
        "## Raw events", "",
        "Anything not covered by a component can be a raw event in `show` (see SPEC_FORMAT.md for fields):",
        "`write`, `line`, `polyline`, `arrow`, `circle`, `ellipse`, `rect`, `underline`, `highlight`, `dot`, `curve`,",
        "`bar`, `hbar`, `count`, `sfx`, `clear`. Its `t` is relative to when the item starts (usually leave it out).", "",
        "## Pacing constants", "",
        f"- caption hold: {C.READ_S_PER_WORD} s per word (+0.12 s per digit), minimum {C.MIN_CAPTION_S} s",
        f"- handwriting: {C.WRITE_S_PER_CHAR} s per character (max 3 s per line)",
        f"- rest after each beat's drawing: {C.BEAT_REST_S} s", "",
        "## Adding a component", "",
        "When a script needs a visual the library can't make, and it would be useful again:",
        "1. Add `def c_<name>(a):` to `components.py`, returning a list of raw events, with a docstring listing its args and defaults.",
        "2. Register it in `COMPONENTS`.",
        "3. Run `python3 library/gen_doc.py` to refresh this file.",
        "4. Use it in the brief and check the sheet from `make.py`.",
        "If it's a one-off, use raw events in the brief instead.", ""]
open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LIBRARY.md"), "w").write("\n".join(out))
print("wrote LIBRARY.md")
