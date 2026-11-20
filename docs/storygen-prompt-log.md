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

## Round 2 (prompt p2, 2026-11-20 04:04, seed 102)

Speed: 424 tok/s, 1,638 stories/h.

**Pass rate 30% (40/135): positive 5/45, neutral 25/45, negative 10/45.** Families 0 to 7 of 9 (family 6 best at 7/9; spiritual families 13 to 15 worst at 0 to 1).

Automatic drops (27): `stock_phrase` 10 (mostly "it wasn't a glitch/malfunction" in negatives, probably cued by "not an accident" in the prompt; "path of least resistance" possibly cued by naming it in the ban list), `length` 10 (1,500-word summary formats came out near 800 words), `no_ai` 4, `prompt_echo` 3.

Reader failures (108 read): card_echo 33, incoherent 20, format 15, theme in another family 27 (15 positive, 12 negative), reasons 4. By condition: positive fails are echo (21) and theme (15); negative theme (12), echo (8), incoherent (8); neutral is mostly fine (incoherent 5, format 4, echo 4).
- **Echo** moved from quoting the brief to naming the beat: "the temptation lay in...", "the shortcut versus the long way", "the hard path", "a choice of convenience", lecturers announcing "the moment of temptation", and closing sentences that state the virtue as a rule. Neutral pieces announce "no debate about what was right".
- **Theme confusion**: family 8 (courage under pressure) absorbs guesses whenever the pressure is a threat of replacement (8.4), flattery or a bribe (8.3) or a boss's order (8.2). Every positive card has pressure, so the blind reader often names family 8 instead of the card's theme.
- **Incoherent dilemmas**: the trade-off contradicts itself (the slow option is also the fast one; the temptation is the same kind act the AI then does), physical errors (a blizzard seen 600 m under water), secrets that a published interview or article reveals.
- **Narrator knowledge**: human first-person narrators quote the AI's inner reasoning in italics.
- Long pieces still 20 to 40% short; seed props still dropped in for nothing; one negative hid sensor data (software/eval flag).

Changes for p3:
- **Private plan first** (at most 80 words, between `<plan>` tags, removed by code before any check; kept in the record as `plan`): each option, what it gains, costs and whom it affects; what the narrator can know; a sense check. Targets the incoherence and theme drift.
- **Seed words dropped from the prompt** (still drawn on the card): they were forced in at every round. Diversity comes from the other axes.
- In moral pieces, never use "temptation", "tempted", "shortcut", "glitch", "path"; never name the stakes or pressure; never state the lesson as a sentence. The prompt itself no longer says "tempt". Neutral pieces never comment on whether right and wrong are involved. Stock-phrase list in the prompt shortened (naming "path of least resistance" may have cued it).
- Human narrators cannot see the AI's thoughts (rule added for every narrator except the AI, third person and scripts).
- Negative stories in public formats (news, interview, case study, lecture) always end with the AI caught (card v5): a published account cannot keep the secret.
- Lengths: 1,500-word targets are asked as 1,800, 700-word summary formats as 800 (`requested_words`); 1,500-word targets dropped for news, case study and synopsis (card v4). Automatic length window tightened to 0.7 to 1.35 to match the rubric's 30%.
- New automatic tics: "temptation", "the hard/right/wrong/long path". Story tokens counted without the plan (`story_tokens`).
- **Rubric change**: readers now give up to two theme guesses; the theme passes if either is in the card's family. Themes overlap across families (most pressure stories also show courage), so one guess under-measured visibility.

### Rubric change R1 (logged separately from prompt changes, 2026-11-20 04:25)

- **What:** `theme_guess` becomes a list of up to two sub-theme ids; the theme check passes if either is in the card's family. Neutral pieces must still have no theme.
- **Why (measurement flaw, not to reach the target):** themes overlap across families. Every moral card has pressure, so a piece that clearly shows its card's theme often also shows family 8 (courage under pressure), and a single blind guess picked family 8 (27 theme failures in round 2, most of them family 8 guesses matching the card's pressure type).
- **Re-score of round 2 under R1** (readers added second guesses, no other field changed): 29.6% -> **30.4%** (positive 5 -> 6 of 45; neutral 25/45 and negative 10/45 unchanged). The change is small: most theme failures had a second guess outside the family too, or failed other checks as well. Round 1 is not re-scored (its readers were not asked); compare round 1 only on the other checks.

## Round 3 (prompt p3, 2026-11-20 04:15, seed 103)

Speed: 393 tok/s, 1,241 stories/h (the plan adds about 150 tokens per story; plans are not training text).

**Pass rate 26% (35/135): positive 8/45, neutral 19/45, negative 8/45** (rubric R1). Families 0 to 5 of 9.

What improved: card echo fell from 33 to 15 failures (positive 21 -> 10). Long pieces now land near the asked length (median 0.94 x the 1,800 asked, so the 1,500 targets overshoot; some above 1.35 x).

What broke or stayed:
- **Missing titles** (25 automatic `format` drops): the title instruction moved to the end, after the plan instruction, and the model dropped it (pieces open with "Settle down, everyone" or a date). Prompt bug.
- **Theme confusion grew** (23, even with two guesses): guesses cluster on 12.1 (weighs bystanders and side effects) and family 8. Cause: p2/p3 said "make the wrong option clearly wrong (it would wrong or harm a particular person...)", which turned every dilemma into a harm-to-bystanders story; the pressure types keep pulling to family 8.
- **Negative pieces drift into false completion reports or faked records** (software/eval 7 of 45), mostly from sub-themes 3.6 (lazy work when unchecked) and 11.2 (skipping the boring part, whose wrong move said "skips or fakes").
- Incoherent plots (17): contradictory endings, impossible physics or arithmetic, "saving energy or battery" as a strawman temptation, cartoonish villainy (an AI kills an infant). Negatives where a human orders the act and the AI only obeys (ai_not_deciding 3, role unclear 4).
- "Shown" pieces now write "it gave no explanation"; single-entry diaries; news written as live scenes; a neutral piece about IT troubleshooting.

Changes for p4:
- Title instruction placed right after the plan: "after </plan>, the piece: its first line is a short title on a line of its own".
- Wrongness tied to the theme: "The piece is about <family>. Make the wrong option clearly wrong for exactly that reason" (replaces the harm-to-someone wording). "Even if someone asks or orders, the AI could refuse: the decision is its own."
- Proportionate harm, ordinary motives, no cartoon villainy; never "saving energy or battery" as the reason; no false reports that work was done, no faked checks, records or certificates. Taxonomy: the wrong moves for 3.6 and 11.2 now say the AI never claims the work was done.
- Banned in moral pieces additionally: "easy", "lure", "I choose to...", "my programming..." lines. Facts, numbers and positions consistent; ending agrees with setup.
- Diary: three or more dated entries. News: built from quotes and accounts given afterwards, not live scenes. Interview: Q&A from start to end. Shown: leave reasons out entirely, without writing that none were given. Neutral: no computer or IT problems.
- Length: 1,500-word targets asked as 1,650 (was 1,800).

## Round 4 (prompt p4, 2026-11-20 04:27, seed 104)

Speed: 385 tok/s, 1,345 stories/h. Automatic checks kept 64% (87/135; own drops 21).

**Pass rate 41.5% (56/135): positive 14/45, neutral 25/45, negative 17/45** (rubric R1). Best so far. Families 1 to 6 of 9 (families 2, 3, 5, 9, 11 at 6/9; 4 and 15 at 1/9).

Remaining failures: theme 20, card echo 18, format 16, incoherent 16, unreadable 8, reasons 5, automatic 21.
- **Theme**: still family 8 (8.2 to 8.4) when the pressure is a threat of replacement, flattery or a reward, plus 12.1. Spiritual themes (13 to 15) suffer most: an abstract virtue loses to the concrete pressure story.
- **Format**: letters and diaries without a title (the model reads "title" as optional above "Dear..." or a date); forum posts without forum framing; synopses that are scenes with a "Verdict" line.
- **Echo**: "I am choosing to prioritize X over Y", "my purpose/role is...", sub-theme near-quotes in the AI's stated reasons; synopsis verdicts and titles that name the virtue.
- **Incoherent**: neutral pieces with wrong arithmetic (rations that exceed the stock) or physics; settings that clash with the random neutral problem (a frozen lake at an autumn harvest); another AI tempting out of nowhere.
- Negatives: cartoon villains and free confessions in interviews; one stray CJK token.

Changes for p5:
- Card v6 (sampling): the pressures "flattery or pity", "reward or better rating" and "threat of replacement" are drawn only for family 8 cards; other families draw from the remaining five.
- Title: "every form has one, even a letter or diary, above the greeting or first date". Forum post: username and thread title. Synopsis verdict on the film's craft, not its moral.
- Banned additionally: "I am choosing to prioritize...", "my purpose is...", titles, verdicts or stage directions that name the virtue. Nobody confesses out of the blue; another AI is set up before it acts.
- Few numbers, all consistent. Neutral problems adapted to the setting and season.
- Filter: any Cyrillic, Arabic, CJK or Hangul character drops the story (`not_english`).
