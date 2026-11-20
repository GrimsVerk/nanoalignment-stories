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
