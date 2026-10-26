# Today's strategy

Rewritten every morning (~08:15 IST) by the daily strategy review, from `python3 strategy.py`.
The posting run reads this in step 1 and follows it when picking themes, formats and which reel goes in which slot.
FEEDBACK.md outranks this file. analyze.py's plan still decides the hook for each slot.

**Updated:** 2026-10-26
**Data:** 11 posted reels, 5 with insights, 2 at 48 h+. Followers 9 (first record 5).
**Data is stale:** insights last fetched 2026-10-25 05:32 UTC; today's pull had not landed by 08:31 IST. Yesterday's 4 reels have no data yet.

## Themes
- Works: none yet. Doesn't work: none yet.
- Leaning: **math & probability LEANING +** (3 reels, all with data, 2 mature; hold 11.8% = 1.04×, share+save 2.0% = 1.94×, views@24h 219).
- CS & AI (hold 5.2%, 0.46×), physics & chemistry (hold 9.7%, 0.86×, 468 views@24h), stats MVP (4 reels, none with data): TOO EARLY. Brain & learning: never tried.

## Formats
- Works: none yet. Doesn't work: none yet.
- Leaning: **step-by-step build LEANING −** (2 reels with data; hold 12.5% = 1.10×, share+save 0.8% = 0.75×). Good hold comes from logarithms alone; how an AI learns held 5.2%.
- Everything else TOO EARLY. Course pain has the best share+save (3.4%, 3.37×, 1 reel); wrong-answer reveal hold 11.8%, share+save 2.0% (1 reel).

## Timings
- Slots are fixed in post.yml: 11:00, 15:00, 19:00, 23:00 IST and 02:00 the night after.
- Leaning: **19:00 LEANING +** (3 reels, 2 with data; hold 15.8% = 1.39×, share+save 1.2%, views@24h 236).
- 11:00, 15:00, 23:00, 02:00: TOO EARLY (0–1 reel with data each). No slot is DOESN'T WORK.

## Length
- Leaning: **50s+ LEANING +** (7 reels, 4 with data; hold 10.5% = 0.93×, share+save 1.5% = 1.47×, views@24h 236). It leans on shares, not on hold.
- 40-49s: TOO EARLY (1 reel: logarithms, hold 19.8%, the best). 30-39s: TOO EARLY (3 reels, none with data yet).

## Biggest problem right now
Hold rate is 11.3% (account median, 5 reels): on a 50 s reel the average viewer leaves around 6 s, before the teaching lands.
Comments are 0.0% on all 5 reels with data. Hold first, comments next; views and shares come after.

## Engagement rules (keep until the data says otherwise)
- **First 1.5 s decides everything.** The hook text and a bold drawing are on screen in the first frame, with a
  concrete number or surprise ("23 people. 50% chance two share a birthday."). No setup before the hook.
- **Beat 1 is a concrete number the viewer can check, not a definition.** (NEW) Logarithms opened "Count the zeros
  in 1,000" and answered in beat 2: hold 19.8%. How an AI learns opened "One neuron: it multiplies input by a dial"
  and reached its payoff in beat 4: hold 5.2%. Same format, same length band.
- **Keep the hook's promise.** (NEW) If the hook says "40 seconds", the reel is under 40 s. How an AI learns said
  "40 seconds" and ran 56 s: hold 5.2%, the worst. Otherwise drop the time from the hook.
- **Payoff by 15 s.** Put the "click" early; a viewer who got the payoff keeps watching for the explanation.
  Birthday paradox showed its answer in beat 2 of 7 (hold 11.8%); exponential growth waited to beat 6 (11.3%).
- **Short captions.** 4–6 words per beat where possible (logarithms' style: "1 crore has 7 zeros. Log is 7.").
- **Open loop.** The hook raises a question the viewer can only close by watching to the end; tease it again mid-reel.
- **Comment question must ask for a number or a pick, never yes/no.** Every end question so far got 0.0% comments.
  Use "Guess before the reveal: 10, 100 or 1,000?" or "A or B? Comment your pick." Show it on screen at the payoff
  and make it the caption's first line.
- **Save cue.** One beat or caption line that makes it worth keeping ("Save this for your next exam").
  Exponential growth's relatable caption opener had share+save 3.4%, the best.
- **Loop ending.** The last frame before the brand card should connect back to the first, so replays feel natural.
- **Caption:** first line is a hook or question, under 10 words; 3–5 specific hashtags, not generic ones (drop #viral).

## Instructions for today's posting run
1. Lean (about 70%): 2 reels math & probability (LEANING +), one of them in the 19:00 slot (LEANING +).
   Keep them 45–55 s (50s+ leans +). Follow analyze.py's hook for each slot.
2. Avoid step-by-step build today (LEANING −). Prefer course pain or wrong-answer reveal structure, or the format
   that fits analyze.py's hook.
3. Fill the other slots with 1 stats MVP reel and 1 physics & chemistry or CS & AI reel, same 45–55 s length.
4. Test (about 30%): 1 brain & learning reel (never tried), strategies only, no condition labels. Change only the
   theme: 45–55 s, number-first beat 1, pick-style end question. Don't add more 30–39 s reels until
   yesterday's three short ones report.
5. Every reel: beat 1 is a concrete number (new rule), no time promise the reel breaks, end with a number-or-pick
   question repeated as the caption's first line. Never reuse a posted topic (FEEDBACK.md); 5 different topics.
6. When you pick a topic, add it to `data/themes.json` with its theme.
