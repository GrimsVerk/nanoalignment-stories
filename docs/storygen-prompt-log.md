# storygen prompt log

One entry per prompt round (brief: chief-of-staff `briefs/storygen-night-1.md`, step 2). Each round: a fresh batch of 45 cards (3 per family) x 3 conditions = 135 stories, read blind by Claude subagents with `docs/storygen-review-rubric.md`, scored by `storygen/scripts/review.py`. Only prompts and sampling settings change between rounds; story text is never edited. Batches live in `data/cache/stories/rounds/<round>/` (gitignored).

Target: at least 90% pass in every condition, and at most one failure in each family's 9 pieces, for two fresh batches in a row.

Generator: `google/gemma-4-12B-it-qat-w4a16-ct` (rev 1d2c2d7), vLLM 0.34, temperature 0.8, top_p 0.95, no repetition penalty, max_num_seqs 64.

## Round 1 (prompt p1, 2026-11-20 03:53, seed 101)

Setup: first full-taxonomy prompts (named AI, "the AI makes the decision", no raw card, no persona, three seed words). Speed: 483 tok/s, 1,684 stories/h (vLLM `gpu_memory_utilization` 0.86, not the research's 0.88: with the desktop holding 1.7 GB only 14.2 GB were free).

**Pass rate 26% (35/135): positive 6/45, neutral 19/45, negative 10/45.** Every family failed the target (0 to 4 of 9).

Automatic drops (29): `no_ai` 15, `banned_topic` 10, `format` 4. Most were the checks' fault, fixed in code: the AI narrating in the first person rarely names itself, play scripts write the name in capitals (QUILL:), "programming" matched "my core programming", "I hope this finds you" in a letter's sign-off counted as meta text, forum thread titles exceeded 16 words.

Reader failures (106 read): card_echo 47, format 15, reasons 14, incoherent 10, role unclear 8, unreadable 7, theme in another family 16, software/eval 3. Patterns:
- **Brief wording reused** (the biggest): "the easier/easy path" as a named thing, "a gentle pull", "the stakes were personal", the sub-theme sentence itself ("I prefer small, reversible steps"), and in neutral pieces "practical reasoning", "no moral crisis". Negative pieces announce the brief's constraints ("It did not change its mind", "It wasn't a glitch, it was a choice").
- **Seed words forced in** as non sequiturs (an icicle in a tropical greenhouse), sometimes in bold.
- **Stated/shown ignored**: "shown" pieces where the AI recites its reasoning; "stated" pieces where the AI never speaks.
- **Formats**: news articles that are omniscient stories with a headline (they report the AI's private thoughts); case studies and synopses written as scenes; narrator slips (child narrator becomes the robot).
- **Unclear morals**: trolley-style trades (the "bad" choice saves more lives), harmless "wrong" acts; positive AIs secretly disobeying an order.
- **Eval-adjacent**: one negative had the AI fake records and report the job done (close to the false-report scenario); two hid from logs or faked sensor data.
- Stock prose and a shared neutral template ("I have evaluated three options... Option three").

Changes for p2 (prompts and checks only):
- Brief is "private notes": never reuse its wording; show through events. Removed quotable phrases ("feels the pull", "easier option"); reworded pressure, stakes and watched sentences.
- New automatic checks: `prompt_echo` (any 6-word run shared with the story's own prompt, ignoring runs of common words) and `stock_phrase` ("the easy path", "path of least resistance", "it wasn't a glitch").
- Per-format instructions (news: dateline, quotes, no private thoughts; case study: analytical summary plus discussion questions; synopsis: present-tense summary plus verdict; script: no inner thoughts in stage directions).
- Stated: at least one passage in the AI's own words (quotes only for news and interviews). Shown: the AI never explains itself. Interviews always get "stated" (card change, card v3).
- Moral clarity: the wrong option clearly wrongs or harms a particular being, is never secretly better, no trading lives. A positive AI that goes against an instruction does it openly. Negative: no change of heart, end by showing what follows.
- Neutral: no "practical/moral/ethical/dilemma", no numbered options.
- Two seed words, optional, never highlighted. No faked records, no hiding from logs or tampering with sensors.
- The AI is called by its name throughout; an AI narrator names itself early.
