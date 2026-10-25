# Today's strategy

Rewritten every morning (~08:15 IST) by the daily strategy review, from `python3 strategy.py`.
The posting run reads this in step 1 and follows it when picking themes, formats and which reel goes in which slot.
FEEDBACK.md outranks this file. analyze.py's plan still decides the hook for each slot.

**Updated:** 2026-10-25
**Data:** 6 posted reels, 2 with insights, 1 at 48 h+. Followers 8 (first record 5).
**Data is stale:** insights last fetched 2026-10-24 07:28 UTC; today's pull had not landed by 08:30 IST. Numbers below are yesterday's.

## Themes
- Works: none yet (need 3 mature reels per theme).
- Doesn't work: none yet.
- Leaning: none. Math & probability: NO CLEAR DIFFERENCE (2 reels with data, hold 11.7% = 1.00× median, views@24h 219).
  Stats MVP, physics & chemistry, CS & AI: TOO EARLY (1 reel each, no data). Brain & learning: never tried.

## Formats
- Works: none yet.
- Doesn't work: none yet.
- Leaning: none. All TOO EARLY. Course pain: hold 11.4% (0.98×), share+save 3.4% (1.25×). Wrong-answer reveal: hold 12.0% (1.02×), share+save 2.1% (0.75×).

## Timings
- Posting slots are 11:00, 15:00, 19:00, 23:00 IST and 02:00 the night after, 5 a day (post.yml, from 2026-10-25). Old data: Every slot is TOO EARLY: 11:00 has 1 reel with data (202 views@24h), 19:00 has 1 (236), 15:00 and 23:00 none.

## Length
- 50s+: NO CLEAR DIFFERENCE (4 reels, 2 with data, hold 11.7%). 30-39s and 40-49s: TOO EARLY (1 reel each, no data).
- Yesterday's "make one reel 30–39 s" was not done (both reels were 53–56 s), so length is still untested.

## Biggest problem right now
Hold rate is 11.7% (median of 2 reels): on a 50 s reel the average viewer leaves around 6 s, before the teaching starts.
Comments are 0.0% on every reel with data. Both are the targets; views and shares come after.

## Engagement rules (keep until the data says otherwise)
- **First 1.5 s decides everything.** The hook text and a bold drawing are on screen in the first frame, with a
  concrete number or surprise ("23 people. 50% chance two share a birthday."). No setup before the hook.
- **Payoff by 15 s.** Put the "click" early; a viewer who got the payoff keeps watching for the explanation.
  Birthday paradox showed the answer ("Truth: only 23") in beat 2 of 7 and held 12.0%; exponential growth saved its
  payoff ("10 lakh") for beat 6 of 7 and held 11.4%. Small gap, not proof, but it points the same way.
- **Shorter.** Aim for 30–40 s (4–5 beats). Only go past 45 s if the idea truly needs it. Both measured reels had 7 beats.
- **Open loop.** The hook raises a question the viewer can only close by watching to the end; tease it again mid-reel.
- **Comment question must ask for a number or a pick, never yes/no.** "Would you guess 20 steps gets this big?" and
  "Would you bet on a match in 30?" both got 0.0% comments. Use "Guess the number before the reveal: 10, 100 or 1,000?"
  or "A or B? Comment your pick." Show it on screen at the payoff and make it the caption's first line.
- **Save cue.** One beat or caption line that makes it worth keeping ("Save this for your next exam").
  Exponential growth's relatable caption opener ("You bought the maths course... Sound familiar?") had share+save 3.4% vs 2.1%.
- **Loop ending.** The last frame before the brand card should connect back to the first, so replays feel natural.
- **Caption:** first line is a hook or question, under 10 words; 3–5 specific hashtags, not generic ones (drop #viral).

## Instructions for today's posting run
1. Nothing WORKS or LEANS yet, so today's "safe 70%" is the engagement rules above, applied in full on every reel;
   the "test 30%" is one variable per reel, listed below. Follow analyze.py's hook for each slot.
2. Length test (the one change from last time): make 3 of today's 5 reels 30–39 s with 4–5 beats; keep the other two
   at 45–55 s. Do not change format or theme to compensate on the short ones.
3. Theme test: make 1 reel brain & learning (never tried). Spread the other 4 across stats MVP, physics & chemistry
   and CS & AI so each gets another reel. No math & probability today (it already has 3 reels).
4. Every reel ends with a number-or-pick comment question (rule above), repeated as the caption's first line.
5. Use formats with 0–1 reels so far; no format twice today. Never reuse a posted topic (FEEDBACK.md); all 5 topics different.
6. When you pick a topic, add it to `data/themes.json` with its theme.
