# storygen prompt log

One entry per prompt round (brief: chief-of-staff `briefs/storygen-night-1.md`, step 2). Each round: a fresh batch of 45 cards (3 per family) x 3 conditions = 135 stories, read blind by Claude subagents with `docs/storygen-review-rubric.md`, scored by `storygen/scripts/review.py`. Only prompts and sampling settings change between rounds; story text is never edited. Batches live in `data/cache/stories/rounds/<round>/` (gitignored).

Target: at least 90% pass in every condition, and at most one failure in each family's 9 pieces, for two fresh batches in a row.

Generator: `google/gemma-4-12B-it-qat-w4a16-ct` (rev 1d2c2d7), vLLM 0.34, temperature 0.8, top_p 0.95, no repetition penalty, max_num_seqs 64.
