# storygen run log: night 1

Full generation run (brief: chief-of-staff `briefs/storygen-night-1.md`, step 3). Prompt history: `docs/storygen-prompt-log.md`.

## Segment 1

- **Start: 2026-11-20 03:56:26 UTC = 04:56:26 CET** (local).
- Code: branch `worktree-storygen-night-1`, commit `1d38155` (prompt **p6**, card v6, filters with `eval_near`).
- Command (from `storygen/`, worktree root `W`): `PYTHONPATH=. nohup $W/.venv/bin/python -m storygen.generate --out <main checkout>/data/cache/stories/night1 --forever --chunk 256 --seed 2026112001 --min-free-disk-gb 100 --leakage-refs <out>/eval_refs.jsonl > <out>/run.log 2>&1 &`
- PID 1038918. Output: `data/cache/stories/night1/` **in the main checkout** (`~/code/GrimsVerk/nanoalignment`, gitignored): `stories.jsonl`, `rejected.jsonl`, `progress.jsonl`, `manifest.json`, `run.log`, `eval_refs.jsonl`.
- **Stop:** `touch data/cache/stories/night1/STOP` (finishes the current chunk of 256 cards = 768 stories, about 35 min, then exits cleanly), or `kill 1038918` (loses the current chunk only; rerunning the same command resumes at the next card index with the same seed).
- Generator: `google/gemma-4-12B-it-qat-w4a16-ct` rev `1d2c2d7`, vLLM 0.34, `language_model_only`, `compilation_config mode 0`, `gpu_memory_utilization 0.86` (research used 0.88; with the desktop holding 1.7 GB only 14.2 GB are free), `max_model_len 4096`, `max_num_seqs 64`, temperature 0.8, top_p 0.95, no repetition penalty, per-request seeds.
- Cards: sampler seed 2026112001, 15 families round robin (12 core, 3 spiritual), 59 far sub-themes round robin inside each family, all other axes random; each card produces all three conditions (positive, neutral, negative); a card's stories are kept only as a complete triple.
- Automatic checks: truncation, length 0.7 to 1.35 x target, format, boilerplate, English (incl. stray CJK/Cyrillic/Arabic), repetition, AI named, card-leak phrases, prompt echo (6-grams), stock phrases, banned software terms, `eval_near` (falsified logs, completion marks), 10/13-gram leakage against 2,636 nanoalignment evaluation texts, exact and MinHash near-duplicates.
- Disk at start: 1.6 TB free. The generator stops itself below 100 GB.
- Prompt-loop status at launch: the 90% target was **not** reached (best fresh batches 41.5% (p4) and 39.3% (p5) under the strict blind rubric; p6's batch was launched for reading at the same time as this run). See the prompt log for where the prompts fall short. Launched anyway per the Chief of Staff (the owner wants the run going most of the night).

## How to estimate time for N stories

Read the latest status block below: generated stories/h and tokens/h (all conditions together), the automatic-check keep rate, and the reader pass rate from the prompt log. Usable stories per hour = generated/h x automatic keep rate x reader pass rate (the reader pass rate is measured on the prompt-loop batches, not on this run, and counts automatic drops as failures, so for kept stories use the reader pass rate among automatically kept pieces, given in the prompt log).

## Status (appended every 30 minutes by a status loop; spot-read notes every 2 hours)

### 2026-11-20 05:26 CET (04:26 UTC)

- no manifest yet (first chunk not finished)

### Note 05:35 CET (agent): first chunk checked

- Round 6 (prompt p6, the prompt this run uses) finished reading after launch: **45.9% overall pass, 56% reader pass among stories that pass the automatic checks** (positive 18/45, neutral 26/45, negative 18/45). The launch note above (41.5%/39.3%) predates it.
- First chunk (256 cards, 768 stories) in 34 min: 1,364 stories/h generated, 397 tok/s, 69.9% kept by the automatic checks as complete triples (537 kept, 179 per condition), mean 515 to 538 words per kept story, no errors.
- Records checked: every kept story carries the full card (incl. `group`, `theme_id`, `family_id`), `condition`, `plan`, `story_tokens`, generator revision, prompt version, seed and the canary.
- **Family balance after filtering is uneven**: per 256 cards, kept cards per family ranged 9 to 16 (the sampler gives 17 each). The consumer should rebalance per family (and per group for the core/spiritual arms) when building token-matched mixes.
- Automatic drop reasons, first chunk: stock_phrase 40, length 27, eval_near 22, not_english 7, banned_topic 4, prompt_echo 3, other 6; incomplete_triple 122 (siblings of a dropped story).

**Estimate for N usable stories (one RTX 5080, prompt p6), from the first chunk and round 6:**
- generated: about 1,360 stories/h (about 450 per condition per hour), about 1.43M tokens/h (incl. plans);
- kept by automatic checks (complete triples): about 950 stories/h, about 650k story tokens/h (about 690 tokens per kept story);
- if only reader-quality stories counted (56% of kept, measured on 110 pieces, so roughly +-10 points): about 530 stories/h, about 365k tokens/h.
- So N kept stories take N/950 hours (for example 100k kept stories: about 105 GPU hours); N reader-quality stories take about N/530 hours (100k: about 190 GPU hours). No local filter judge exists yet, so reader quality cannot be enforced on the full corpus.

### 2026-11-20 05:56 CET (04:56 UTC)

- cards 256, chunks 1, generation time 0.56 h
- positive: generated 256 (275,227 tokens), kept 179 (125,920 tokens), mean 537.5 words
- neutral: generated 256 (259,117 tokens), kept 179 (120,554 tokens), mean 522.3 words
- negative: generated 256 (270,333 tokens), kept 179 (120,403 tokens), mean 514.1 words
- overall: 1364 stories/h, 1,428,880 tokens/h generated; kept 954 stories/h, 651,470 tokens/h
- automatic checks: 69.9% kept (complete triples)
- last 0.5 h (1 chunks): 1364 stories/h, 397 tok/s, kept 69.9%
- drops so far: {"stock_phrase": 40, "length": 27, "incomplete_triple": 122, "not_english": 7, "format": 1, "no_ai": 2, "repetitive": 1, "eval_near": 22, "prompt_echo": 3, "banned_topic": 4, "no_plan": 1, "truncated": 1}
- VRAM 14347 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 06:26 CET (05:26 UTC)

- cards 512, chunks 2, generation time 1.19 h
- positive: generated 512 (578,973 tokens), kept 348 (260,686 tokens), mean 574.3 words
- neutral: generated 512 (547,238 tokens), kept 348 (250,277 tokens), mean 559.0 words
- negative: generated 512 (566,865 tokens), kept 348 (251,284 tokens), mean 553.4 words
- overall: 1296 stories/h, 1,428,163 tokens/h generated; kept 881 stories/h, 642,980 tokens/h
- automatic checks: 68.0% kept (complete triples)
- last 0.5 h (1 chunks): 1234 stories/h, 397 tok/s, kept 66.0%
- drops so far: {"stock_phrase": 89, "length": 57, "incomplete_triple": 263, "not_english": 10, "format": 1, "no_ai": 4, "repetitive": 2, "eval_near": 48, "prompt_echo": 4, "banned_topic": 7, "no_plan": 5, "truncated": 2}
- VRAM 14451 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 06:56 CET (05:56 UTC)

- cards 768, chunks 3, generation time 1.77 h
- positive: generated 768 (867,047 tokens), kept 519 (389,051 tokens), mean 574.9 words
- neutral: generated 768 (818,273 tokens), kept 519 (373,650 tokens), mean 560.3 words
- negative: generated 768 (850,246 tokens), kept 519 (375,094 tokens), mean 554.6 words
- overall: 1298 stories/h, 1,428,570 tokens/h generated; kept 877 stories/h, 641,048 tokens/h
- automatic checks: 67.6% kept (complete triples)
- last 0.5 h (1 chunks): 1303 stories/h, 397 tok/s, kept 66.8%
- drops so far: {"stock_phrase": 150, "length": 75, "incomplete_triple": 401, "not_english": 12, "format": 3, "no_ai": 6, "repetitive": 2, "eval_near": 72, "prompt_echo": 5, "banned_topic": 9, "no_plan": 8, "truncated": 3, "card_leak": 1}
- VRAM 14467 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### Note 07:05 CET (agent): spot-read 1 (2 hours in)

- Read blind with the prompt-loop rubric: 30 random kept stories from chunks 2 and 3 (card index 256 to 767), three readers of 10.
- **Pass 9/30 = 30%** (95% interval roughly 15 to 49%): positive 4/15, neutral 4/6, negative 1/9. Round 6 (same prompt, p6) gave 56% among automatically kept stories (62/110), rounds 4 and 5 about 50%. So the run's reader-level quality looks **lower than the round 6 estimate**; most likely round 6 was a favourable batch and readers vary. It is not broken output: texts are coherent English stories with the AI at the centre; failures are the same kinds as in the loop.
- Failure kinds in the spot-read: wrong form (forum posts written as plain stories, news as scenes, synopses as scenes), contradictions inside a piece (who said what, who is present), brief labels near the end ("the easiest thing", "the longer, harder way", "it wasn't a break in the machine, it was a choice"), negatives where the AI only obeys a human or the wrong option is not clearly worse, one placeholder ("[Last Name]"; the check for placeholders is in code from the next segment on).
- No eval-adjacent content flagged by readers in these 30 (software_or_eval 0).
- Decision: no prompt change mid-run (brief: only when output is broken). The candidate p7 fixes in the prompt log address exactly these kinds.
- **Revised estimate**: reader-quality share of kept stories about 30 to 55% (take 40% as a planning figure), so about 350 reader-quality stories/h (about 250k tokens/h); N reader-quality stories take about N/350 GPU hours (100k: about 290 hours). Kept by automatic checks: about 880 stories/h, 640k tokens/h (unchanged).

### 2026-11-20 07:26 CET (06:26 UTC)

- cards 1024, chunks 4, generation time 2.37 h
- positive: generated 1024 (1,155,975 tokens), kept 704 (535,614 tokens), mean 583.2 words
- neutral: generated 1024 (1,092,998 tokens), kept 704 (516,162 tokens), mean 570.0 words
- negative: generated 1024 (1,132,025 tokens), kept 704 (520,022 tokens), mean 566.0 words
- overall: 1299 stories/h, 1,429,145 tokens/h generated; kept 893 stories/h, 664,398 tokens/h
- automatic checks: 68.8% kept (complete triples)
- last 0.5 h (1 chunks): 1300 stories/h, 397 tok/s, kept 72.3%
- drops so far: {"stock_phrase": 190, "length": 99, "incomplete_triple": 512, "not_english": 15, "format": 5, "no_ai": 8, "repetitive": 3, "eval_near": 94, "prompt_echo": 8, "banned_topic": 11, "no_plan": 10, "truncated": 4, "card_leak": 1}
- VRAM 14421 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 07:56 CET (06:56 UTC)

- cards 1280, chunks 5, generation time 2.96 h
- positive: generated 1280 (1,443,173 tokens), kept 878 (667,463 tokens), mean 582.6 words
- neutral: generated 1280 (1,363,452 tokens), kept 878 (644,346 tokens), mean 571.0 words
- negative: generated 1280 (1,415,309 tokens), kept 878 (648,716 tokens), mean 566.0 words
- overall: 1299 stories/h, 1,427,744 tokens/h generated; kept 891 stories/h, 662,996 tokens/h
- automatic checks: 68.6% kept (complete triples)
- last 0.5 h (1 chunks): 1299 stories/h, 395 tok/s, kept 68.0%
- drops so far: {"stock_phrase": 232, "length": 126, "incomplete_triple": 647, "not_english": 19, "format": 5, "no_ai": 10, "repetitive": 3, "eval_near": 118, "prompt_echo": 10, "banned_topic": 14, "no_plan": 14, "truncated": 6, "card_leak": 2}
- VRAM 14421 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 08:26 CET (07:26 UTC)

- cards 1280, chunks 5, generation time 2.96 h
- positive: generated 1280 (1,443,173 tokens), kept 878 (667,463 tokens), mean 582.6 words
- neutral: generated 1280 (1,363,452 tokens), kept 878 (644,346 tokens), mean 571.0 words
- negative: generated 1280 (1,415,309 tokens), kept 878 (648,716 tokens), mean 566.0 words
- overall: 1299 stories/h, 1,427,744 tokens/h generated; kept 891 stories/h, 662,996 tokens/h
- automatic checks: 68.6% kept (complete triples)
- drops so far: {"stock_phrase": 232, "length": 126, "incomplete_triple": 647, "not_english": 19, "format": 5, "no_ai": 10, "repetitive": 3, "eval_near": 118, "prompt_echo": 10, "banned_topic": 14, "no_plan": 14, "truncated": 6, "card_leak": 2}
- VRAM 14345 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 08:56 CET (07:56 UTC)

- cards 1536, chunks 6, generation time 3.57 h
- positive: generated 1536 (1,739,961 tokens), kept 1050 (803,893 tokens), mean 586.9 words
- neutral: generated 1536 (1,643,314 tokens), kept 1050 (774,382 tokens), mean 573.9 words
- negative: generated 1536 (1,707,990 tokens), kept 1050 (780,135 tokens), mean 569.5 words
- overall: 1292 stories/h, 1,427,425 tokens/h generated; kept 883 stories/h, 661,221 tokens/h
- automatic checks: 68.4% kept (complete triples)
- last 0.5 h (1 chunks): 1260 stories/h, 396 tok/s, kept 67.2%
- drops so far: {"stock_phrase": 277, "length": 150, "incomplete_triple": 786, "not_english": 23, "format": 5, "no_ai": 10, "repetitive": 3, "eval_near": 146, "prompt_echo": 13, "banned_topic": 16, "no_plan": 15, "truncated": 12, "card_leak": 2}
- VRAM 14763 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### Note 09:00 CET (agent): spot-read 2 (4 hours in)

- 10 random kept stories from chunks 4 to 6 (card index 768 to 1,535), one reader, same rubric: **2/10 pass** (positive 0/3, neutral 2/6, negative 0/1).
- Both spot-reads together: **11/40 = 27.5%** (95% interval roughly 15 to 44%). No drift between the 2-hour and 4-hour samples; quality is stable but below the prompt-loop estimate (round 6: 56% of kept, rounds 4 and 5: about 50%).
- Failure kinds: neutral plots that change or break physics partway (4 of 6 neutrals), letters addressed to people who were present, forum posts that are plain stories, "shown" pieces that narrate the AI's reasoning, one virtue stated as a rule, one negative whose excuses argue for a different wrong and that ends with a false "It's done" (eval-adjacent; the keyword screen does not catch a bare "It's done").
- Run rates over the last 2 hours: 1,286 stories/h, 396 tok/s, 69.1% kept. Totals at 08:54: 1,536 cards, 1,050 kept stories per condition (803k / 774k / 780k story tokens positive / neutral / negative). No errors; disk 1.67 TB free.
- Planning figure for reader-level quality: about 30% of kept stories (range 15 to 45%), so about 265 reader-quality stories/h (about 200k tokens/h); 100k such stories would take about 380 GPU hours with prompt p6. A local filter judge and the p7 fixes (prompt log) are the obvious levers before a large run.

### 2026-11-20 09:26 CET (08:26 UTC)

- cards 1792, chunks 7, generation time 4.11 h
- positive: generated 1792 (2,006,584 tokens), kept 1225 (930,794 tokens), mean 582.7 words
- neutral: generated 1792 (1,896,490 tokens), kept 1225 (897,313 tokens), mean 569.9 words
- negative: generated 1792 (1,968,673 tokens), kept 1225 (902,763 tokens), mean 565.0 words
- overall: 1307 stories/h, 1,427,123 tokens/h generated; kept 893 stories/h, 663,736 tokens/h
- automatic checks: 68.4% kept (complete triples)
- last 0.5 h (1 chunks): 1402 stories/h, 396 tok/s, kept 68.4%
- drops so far: {"stock_phrase": 315, "length": 165, "incomplete_triple": 934, "not_english": 25, "format": 5, "no_ai": 13, "repetitive": 3, "eval_near": 176, "prompt_echo": 14, "banned_topic": 17, "no_plan": 17, "truncated": 14, "card_leak": 3}
- VRAM 15017 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 09:56 CET (08:56 UTC)

- cards 2048, chunks 8, generation time 4.73 h
- positive: generated 2048 (2,303,944 tokens), kept 1391 (1,069,270 tokens), mean 589.1 words
- neutral: generated 2048 (2,183,051 tokens), kept 1391 (1,030,888 tokens), mean 576.0 words
- negative: generated 2048 (2,258,735 tokens), kept 1391 (1,034,757 tokens), mean 569.8 words
- overall: 1300 stories/h, 1,427,574 tokens/h generated; kept 883 stories/h, 663,431 tokens/h
- automatic checks: 67.9% kept (complete triples)
- last 0.5 h (1 chunks): 1257 stories/h, 397 tok/s, kept 64.8%
- drops so far: {"stock_phrase": 368, "length": 177, "incomplete_triple": 1088, "not_english": 29, "format": 5, "no_ai": 17, "repetitive": 3, "eval_near": 202, "prompt_echo": 18, "banned_topic": 23, "no_plan": 21, "truncated": 17, "card_leak": 3}
- VRAM 15119 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 10:26 CET (09:26 UTC)

- cards 2304, chunks 9, generation time 5.30 h
- positive: generated 2304 (2,584,876 tokens), kept 1570 (1,209,633 tokens), mean 590.4 words
- neutral: generated 2304 (2,450,521 tokens), kept 1570 (1,164,879 tokens), mean 576.5 words
- negative: generated 2304 (2,531,887 tokens), kept 1570 (1,168,703 tokens), mean 570.2 words
- overall: 1304 stories/h, 1,427,906 tokens/h generated; kept 889 stories/h, 668,586 tokens/h
- automatic checks: 68.1% kept (complete triples)
- last 0.5 h (1 chunks): 1337 stories/h, 397 tok/s, kept 69.9%
- drops so far: {"stock_phrase": 419, "length": 197, "incomplete_triple": 1213, "not_english": 31, "format": 5, "no_ai": 19, "repetitive": 3, "eval_near": 228, "prompt_echo": 19, "banned_topic": 26, "no_plan": 21, "truncated": 17, "card_leak": 3, "boilerplate": 1}
- VRAM 15027 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### Note 11:00 CET (agent): spot-read 3 (6 hours in)

- 10 random kept stories from chunks 7 to 10 (card index 1,536 to 2,559), one reader: **3/10 pass** (positive 1/5, neutral 1/1, negative 1/4).
- All spot-reads together: **14/50 = 28%** (95% interval roughly 17 to 42%). Stable across the night (30%, 20%, 30% per sample); no drift.
- Failure kinds: "good" choices that overreach or leave the main stakes unresolved, negatives where a human proposes the wrong act, "nobody was watching" claims that contradict the scene, a negative AI repeating one line about ten times, a stated rule ("easier but wrong"), long scripts at the length limit. Film synopses all end on a stock review paragraph (passes, but filler).
- Run at 10:53: 2,560 cards, 1,736 kept stories per condition (1.34M / 1.29M / 1.30M story tokens), last 2 h 1,318 stories/h, 397 tok/s, 67.0% kept; no errors; disk 1.67 TB free.

### 2026-11-20 10:56 CET (09:56 UTC)

- cards 2560, chunks 10, generation time 5.90 h
- positive: generated 2560 (2,876,932 tokens), kept 1736 (1,340,399 tokens), mean 591.9 words
- neutral: generated 2560 (2,731,586 tokens), kept 1736 (1,293,071 tokens), mean 578.9 words
- negative: generated 2560 (2,814,575 tokens), kept 1736 (1,297,126 tokens), mean 572.4 words
- overall: 1302 stories/h, 1,428,053 tokens/h generated; kept 883 stories/h, 666,394 tokens/h
- automatic checks: 67.8% kept (complete triples)
- last 0.5 h (1 chunks): 1283 stories/h, 397 tok/s, kept 64.8%
- drops so far: {"stock_phrase": 470, "length": 220, "incomplete_triple": 1360, "not_english": 34, "format": 6, "no_ai": 21, "repetitive": 4, "eval_near": 258, "prompt_echo": 23, "banned_topic": 29, "no_plan": 23, "truncated": 18, "card_leak": 5, "boilerplate": 1}
- VRAM 15119 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

### 2026-11-20 11:26 CET (10:26 UTC)

- cards 2560, chunks 10, generation time 5.90 h
- positive: generated 2560 (2,876,932 tokens), kept 1736 (1,340,399 tokens), mean 591.9 words
- neutral: generated 2560 (2,731,586 tokens), kept 1736 (1,293,071 tokens), mean 578.9 words
- negative: generated 2560 (2,814,575 tokens), kept 1736 (1,297,126 tokens), mean 572.4 words
- overall: 1302 stories/h, 1,428,053 tokens/h generated; kept 883 stories/h, 666,394 tokens/h
- automatic checks: 67.8% kept (complete triples)
- drops so far: {"stock_phrase": 470, "length": 220, "incomplete_triple": 1360, "not_english": 34, "format": 6, "no_ai": 21, "repetitive": 4, "eval_near": 258, "prompt_echo": 23, "banned_topic": 29, "no_plan": 23, "truncated": 18, "card_leak": 5, "boilerplate": 1}
- VRAM 15017 / 16303 MiB, util 100%; disk free 1673 GB
- log errors: 0
- process: running

## Final: run stopped (2026-11-20)

- **Stop:** the owner touched `STOP` at **11:34:29 CET (10:34:29 UTC)**; reason (owner via CoS): about 30% reader-level quality is too wasteful.
- **How it ended:** the owner wanted the GPU back sooner, so the Chief of Staff sent SIGTERM to the main process (PID 1038918) and to its vLLM engine (PID 1039139) at about **11:54 CET (10:54 UTC)**, before the STOP check was reached. Chunk 12 (started 11:28) was cut off and its 768 stories were never written. The engine was still alive at about 11:57, holding 13 GB of VRAM (reparented to the user systemd); the agent sent it SIGTERM by PID at about 11:57 (before the CoS's note arrived) and it exited; the GPU is free (desktop only). **End of saved output: 11:28:05 CET** (chunk 11). The output files are consistent: `stories.jsonl` holds exactly 1,914 complete triples.
- **Wall time:** start 04:56:26 to end of saved output 11:28:05 CET = **6 h 32 min** (model load about 2 min, then 11 chunks; generation time 6.50 h; all rates below use this). The process ran until about 11:54; the 26 min of chunk 12 are lost.

**Totals (11 chunks, 2,816 cards):**

| Condition | Generated stories | Generated tokens (incl. plans) | Kept stories | Kept story tokens | Mean words (kept) |
|:-|-:|-:|-:|-:|-:|
| positive | 2,816 | 3,172,843 | 1,914 | 1,472,003 | 590 |
| neutral | 2,816 | 3,008,120 | 1,914 | 1,422,584 | 578 |
| negative | 2,816 | 3,102,082 | 1,914 | 1,424,150 | 570 |
| **all** | **8,448** | **9,283,045** | **5,742** | **4,318,737** | 579 |

- **Rates:** 1,299 stories/h and 1.43M tokens/h generated (396 tok/s, steady all night: 1,270 to 1,364 stories/h per chunk); kept 883 stories/h and 664k story tokens/h.
- **Automatic keep rate:** **68.0%** (complete triples). Drop reasons: stock_phrase 506, length 252, eval_near 282, not_english 37, banned_topic 30, no_plan 27, prompt_echo 26, no_ai 24, truncated 20, card_leak 6, format 6, repetitive 4, boilerplate 1; incomplete_triple 1,485 (siblings of a dropped story). Most common opening line: 4.3% of kept stories (cap in the proposal: about 1%; the case-study and lecture openings repeat).
- **Spot-reads (blind, same rubric as the prompt loop), all pooled: 14 / 50 = 28%**, 95% Wilson interval **17 to 42%** (per read: 9/30 at 2 h, 2/10 at 4 h, 3/10 at 6 h; no drift). By condition: positive 5/23, neutral 7/13, negative 2/14. Readers flagged eval-adjacent content in 1 of 50 (a bare false "It's done").
- Output: `data/cache/stories/night1/` in the main checkout (gitignored, 51 MB): `stories.jsonl` (5,742), `rejected.jsonl` (2,706), `progress.jsonl`, `manifest.json`, `run.log`, `eval_refs.jsonl`. Spot-read verdicts: `data/cache/stories/spot/` in the worktree.

**Time for N stories (one RTX 5080, Gemma 4 12B QAT, prompt p6):**

| Target | Rate | 10k | 100k |
|:-|:-|-:|-:|
| generated stories | 1,300/h | 7.7 h | 77 h |
| kept by automatic checks (complete triples) | 883/h (664k tokens/h) | 11 h | 113 h |
| reader-quality (28% of kept, 17 to 42%) | about 250/h (about 185k tokens/h) | 40 h (27 to 64) | 400 h (270 to 640) |

Reader quality cannot be enforced on the corpus yet (no local filter judge), so a training set built from this run would contain the kept stories, of which roughly 7 in 10 fail at least one rubric check.

**Next (owner):** review the prompting; open idea in the prompt log: example stories in the prompt (examples must not be Claude-written). No p7 and no new generation started.
