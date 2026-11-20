# Next steps

## State (2026-11-20, late)

- Moved out of nanoalignment with history (see `docs/DECISIONS.md`). Night-1 run (p6): 5,742 kept stories, about 28% pass a blind read (`docs/storygen-run-log.md`); output in nanoalignment's `data/cache/stories/night1/` (main checkout, gitignored).
- **storygen-2 (branch `worktree-storygen-2`)**, CoS brief `chief-of-staff/briefs/nanoalignment-storygen-2.md`. Arm comparison cmp1 done (`docs/storygen-prompt-log.md`): Fable outlines 43% reader pass against p6 27%; p7 fixes, local examples and Fable examples gave no gain. FP8 KV is 2.5x faster; its pass rate is not read yet (batch in `data/rounds/cmp1-fp8/`).
- Prompt p8 is current (`storygen/prompts.py`); p6 frozen in `storygen/prompts_p6.py`; p7 is in git history (commit 9512d69).

## In progress (storygen-2): stopped for the night by the owner (usage), 2026-11-20 about 23:30

Exact state:
- Round 2 code is ready and committed (p8, local two-pass outlines, compact Fable outline briefs, `scripts/slot_round.sh`), not run yet.
- Compact Fable outlines for round 2 were started and stopped before writing anything: `data/outlines/r2/briefs-{0,1,2}.md` exist (45 cards, seed 2026112102), no `part-*.jsonl` yet.
- The cmp1 FP8 batch (`data/rounds/cmp1-fp8/p7`, 135 stories) is generated but not read.

Next, in order:
1. Write the round-2 compact outlines: 3 Fable subagents (Agent tool, `model: "fable"`), prompt `docs/outline-prompt-compact.md` with `{briefs}` = `data/outlines/r2/briefs-K.md`, `{out}` = `data/outlines/r2/part-K.jsonl`, `{n}` = 45. Then `uv run python scripts/check_extras.py data/outlines/r2.jsonl data/outlines/r2/part-*.jsonl --expect 135`. Record the tokens per outline (round 1: about 4,600).
2. When the CoS gives a GPU slot (about 25 min): `nohup scripts/slot_round.sh r2 2026112102 fp8 p8=p8 "p8_outline=p8,outlines=data/outlines/r2.jsonl" "p8_lol=p8,outlines=local" > data/rounds/r2.log 2>&1 &`.
3. Read r2 and the cmp1 FP8 batch blind. Put both under one dir so they share one balanced pool, e.g. `mkdir data/rounds/r2read` with symlinks to `../r2/p8`, `../r2/p8_outline`, `../r2/p8_lol` and `../cmp1-fp8/p7` (as `p7_fp8`); then `uv run python scripts/review.py prep data/rounds/r2read --readers 26`. Readers: prompt `docs/reader-prompt.md`, default model, waves of 8, stop at a usage-limit warning and tell the CoS. Score with `scripts/review.py score` and `scripts/arm_report.py`.
4. FP8: adopt in `config.yaml` (`llm_kwargs: kv_cache_dtype: fp8`, plus `CUDA_HOME=/opt/cuda` for FlashInfer) only if the p7 FP8 pass is not worse than bf16 p7 in cmp1 (25.2%).
5. Log round 2 in `docs/storygen-prompt-log.md`, including Claude tokens per item. Iterate a few rounds on the best arm that has no Claude prose, confirm on two fresh batches, then merge `worktree-storygen-2` into main (checks: `make check`) and push.

## Notes for the next agent

- GPU is shared; the bash agent has priority. Ask the CoS for a slot. The desktop holds about 3.2 GB of VRAM, so runs use `gpu_memory_utilization` 0.78 and `max_num_batched_tokens` 1024 (see `scripts/slot_round.sh`).
- `data/` (stories, examples, outlines, reviews) is gitignored. Example ids are in `examples/local-night1.ids` (rebuild with `scripts/select_examples.py --rebuild`).
- Reader prompt: `docs/reader-prompt.md`; outline prompts: `docs/outline-prompt.md`, `docs/outline-prompt-compact.md`; Fable example prompt: `docs/fable-example-prompt.md`.
