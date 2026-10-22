# Chalkwise reels playbook

## The one message

Courses fail people: you buy one, start it, and never finish. Chalkwise drops the course. You start from whatever you're curious about, and it teaches the basics you need on the way, out loud, on a whiteboard that draws as it explains.

Every reel shows that, by *doing* it: teach one real idea fast, from zero background, so the viewer feels "wait, I actually get that now."

## Audience

Gen Z and millennials in India and beyond (18–34). Curious, busy, burned by courses and long lectures; many learn better by seeing and hearing than by reading. Talk like a smart friend, not a teacher. Short sentences. Indian names and everyday Indian settings are welcome (chai, cricket, exams, UPI, trains, Swiggy).

## Reel structure (30–50 s)

1. **Hook, 0–2.5 s.** On-screen text plus a bold first drawing. It must make a promise or open a question. No logo, no greeting.
2. **Setup, to ~8 s.** A concrete situation the viewer knows.
3. **Teach, to ~25 s.** One idea, drawn step by step. A new visual beat every 1.5 to 3 s; the board is never static.
4. **Payoff or question, ~25–30 s.** The "click" moment, or a question back to the viewer (the tutor asks, it doesn't lecture). Questions drive comments.
5. **Brand, last 4–6 s.** "That's how Chalkwise teaches" plus the line about no courses, and "Follow for 1 idea a day".

## Hook families (track performance by `hook_type`)

| hook_type | Pattern | Example |
| --- | --- | --- |
| speed promise | "X in 30 seconds. No [subject] course." | "Standard deviation in 30 seconds. No stats course." |
| course pain | Call out the unfinished-course feeling, then teach | "You bought the course. You watched 2 videos. Here's the part you actually needed." |
| prerequisite wall | "You don't need [scary prerequisite] to understand [cool topic]" | "You don't need calculus to understand entropy." |
| everyday mystery | A thing they see daily, explained | "Why does your phone say 'battery 20%' and die in 5 minutes?" |
| myth bust | A common wrong belief, corrected on the board | "'Average' doesn't mean 'typical'. Here's proof." |
| wrong-answer reveal | Pose a question, show the intuitive wrong answer, then the right one | "Which is more likely: HHHH or HTHT?" |
| curiosity jump | Start at a big, impressive topic | "How do brain-computer interfaces read your thoughts? 40 seconds." |

## Topic bank

Rotate: about half from the statistics MVP (it previews the real product), half curiosity topics that show the "learn anything" promise.

- **Stats MVP:** mean vs median (salary example), standard deviation, spread, normal distribution, z-score (comparing JEE vs board marks), sampling, correlation vs causation.
- **Math and probability:** logarithms as "counting zeros", exponential growth (compound interest, viral posts), birthday paradox, Monty Hall, Bayes with a medical-test-free example (spam filter).
- **Physics and chemistry:** entropy with coin flips, why ice floats, why the sky is blue, terminal velocity, half-life.
- **CS and AI:** how a neural network learns (one neuron), what "training" an AI means, binary in 30 s, how UPI keeps money safe (hashing).
- **Brain and learning (strategies only):** spaced repetition, why re-reading doesn't work, chunking, the forgetting curve.

## Rules

- **Correct first.** Every fact and number is checked; numbers are recomputed in code before queueing.
- **Honest about the product.** Chalkwise isn't public yet. Say "join the waitlist" or "follow for 1 idea a day", never "download now" or "try it today".
- **No medical or diagnostic claims, no condition labels.** Never say a reel or the app treats, fixes or diagnoses anything. Learning strategies are fine.
- **No voiceover.** Captions carry every word; audio is only our own marker sounds, pops, paper swipes and the soft pad. Write captions to be read in one glance (max ~8 words) and hold each long enough to read: about 0.4 s per word, minimum 1.5 s.
- **Original only.** No copyrighted characters, music, or other creators' content.
- **Readable on a phone.** Captions 60+ px, board text 46+ px, max ~8 words per caption.

## How performance is judged

From `data/insights.json` (pulled daily by the insights workflow), for each reel after 48 hours:

- **Hold rate** = `ig_reels_avg_watch_time` (ms) / (`duration` × 1000). The main signal for the hook and pacing.
- **Share + save rate** = (`shares` + `saved`) / `reach`. The main signal that the teaching landed.
- **Comment rate** = `comments` / `reach`. Signal for the end question.
- **Views** and follower change, for reach.

Each day: about 70% of reels use the best-performing hook family and format so far, 30% try something new (a new hook family, topic area, length, or format). Change one thing at a time so the comparison means something. Wait for at least 3 reels per variant before calling a winner. Log every conclusion in `LEARNINGS.md`.
