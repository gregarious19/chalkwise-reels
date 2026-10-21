#!/usr/bin/env python3
"""Build a full-length voiceover track from a reel spec's "voiceover" lines using Deepgram Aura.

Each line starts at its "t". If a clip runs into the next line, the next line is pushed later
and a warning is printed (the script writer should shorten the line).

Usage: DEEPGRAM_API_KEY=... python3 tts.py scripts/queue/reel.json voice.wav
Exits 0 without writing anything when no API key is set (reel renders without voice).
"""
import json, os, subprocess, sys, urllib.request
import numpy as np

SR = 48000

def speak(text, key, model):
    req = urllib.request.Request(
        f"https://api.deepgram.com/v1/speak?model={model}&encoding=linear16&sample_rate={SR}&container=none",
        data=json.dumps({"text": text}).encode(),
        headers={"Authorization": f"Token {key}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        pcm = r.read()
    return np.frombuffer(pcm, dtype="<i2").astype(np.float32) / 32768.0

def main():
    spec_path, out = sys.argv[1], sys.argv[2]
    key = os.environ.get("DEEPGRAM_API_KEY")
    if not key:
        print("no DEEPGRAM_API_KEY; skipping voiceover")
        return
    spec = json.load(open(spec_path))
    lines = spec.get("voiceover", [])
    if not lines:
        print("spec has no voiceover lines")
        return
    model = os.environ.get("DEEPGRAM_VOICE") or spec.get("voice_model") or "aura-2-thalia-en"
    total = int(spec["duration"] * SR)
    track = np.zeros(total, np.float32)
    cursor = 0
    for ln in lines:
        clip = speak(ln["text"], key, model)
        start = max(int(ln["t"] * SR), cursor)
        if start > int(ln["t"] * SR) + SR // 4:
            print(f"warning: line at {ln['t']}s pushed to {start / SR:.2f}s (previous line too long)")
        end = min(start + len(clip), total)
        track[start:end] += clip[: end - start]
        cursor = start + len(clip) + int(0.12 * SR)
        if start + len(clip) > total:
            print(f"warning: voiceover runs past the reel end ({(start + len(clip)) / SR:.1f}s > {spec['duration']}s)")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", out],
                   input=track.tobytes(), check=True)
    print("wrote", out)

if __name__ == "__main__":
    main()
