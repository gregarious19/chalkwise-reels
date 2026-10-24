# Today's strategy

Rewritten every morning (~08:15 IST) by the daily strategy review, from `python3 strategy.py`.
The posting run reads this in step 1 and follows it when picking themes, formats and which reel goes in which slot.
FEEDBACK.md outranks this file. analyze.py's plan still decides the hook for each slot.

**Updated:** 2026-10-25 (initial version, set up by hand)
**Data:** 6 posted reels, 2 with insights, 1 at 48 h+. Followers 8.

## Themes
- Works: none yet (need 3 mature reels per theme).
- Doesn't work: none yet.
- Leaning: none yet. Math & probability is the only theme with data (2 reels), and it sits right at the account median.

## Formats
- Works: none yet.
- Doesn't work: none yet.
- Leaning: none yet. Course pain and wrong-answer reveal each have one reel with data.

## Timings
- Posting slots stay 11:00, 15:00, 19:00, 23:00 IST (set in post.yml). No slot has enough data yet.

## Length
- 5 of 6 reels are 49 s or longer; only one is in 30–39 s, and it has no data. Lengths are untested.

## Biggest problem right now
Hold rate is ~11–12%: on a 50 s reel the average viewer leaves after about 6 s, before the teaching starts.
Comments are 0% on every reel. Fix those two before anything else.

## Engagement rules (keep until the data says otherwise)
- **First 1.5 s decides everything.** The hook text and a bold drawing are on screen in the first frame, with a
  concrete number or surprise ("23 people. 50% chance two share a birthday."). No setup before the hook.
- **Payoff by 15 s.** Put the "click" early; a viewer who got the payoff keeps watching for the explanation.
- **Shorter.** Aim for 30–40 s (4–5 beats). Only go past 45 s if the idea truly needs it.
- **Open loop.** The hook raises a question the viewer can only close by watching to the end; tease it again mid-reel
  ("the answer surprises everyone, wait for it").
- **One comment question** at the payoff, easy to answer in one word or a number ("Guess first: A or B?"). Repeat it
  as the first line of the post caption.
- **Save cue.** One beat or caption line that makes it worth keeping ("Save this for your next exam").
- **Loop ending.** The last frame before the brand card should connect back to the first, so replays feel natural.
- **Caption:** first line is a hook or question, under 10 words; 3–5 specific hashtags, not generic ones.

## Instructions for today's posting run
1. Spread today's 4 reels across 4 different themes so every theme collects data: stats MVP, physics & chemistry, CS & AI, brain & learning (brain & learning has never been tried).
2. Use formats that have 0–1 reels so far, and avoid repeating a format within today.
3. Make at least one reel 30–39 s, so length gets tested.
4. When you pick a topic, add it to `data/themes.json` with its theme.
