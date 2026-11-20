# Next steps

## State (2026-11-20, late)

- Moved out of nanoalignment with history (see `docs/DECISIONS.md`). Night-1 run (p6): 5,742 kept stories, about 28% pass a blind read (`docs/storygen-run-log.md`); output in nanoalignment's `data/cache/stories/night1/` (main checkout, gitignored).
- **storygen-2 (branch `worktree-storygen-2`)**, CoS brief `chief-of-staff/briefs/nanoalignment-storygen-2.md`. Arm comparison cmp1 done (`docs/storygen-prompt-log.md`): Fable outlines 43% reader pass against p6 27%; p7 fixes, local examples and Fable examples gave no gain. FP8 KV is 2.5x faster; its pass rate is not read yet (batch in `data/rounds/cmp1-fp8/`).
- Prompt p8 is current (`storygen/prompts.py`); p6 frozen in `storygen/prompts_p6.py`; p7 is in git history (commit 9512d69).

## In progress (storygen-2)

1. Round 2 (seed 2026112102, FP8 KV): arms p8, p8 + Fable compact outlines (`data/outlines/r2.jsonl`), p8 + local two-pass outlines (`outlines=local`). Command: `nohup scripts/slot_round.sh r2 2026112102 fp8 p8=p8 "p8_outline=p8,outlines=data/outlines/r2.jsonl" "p8_lol=p8,outlines=local" > data/rounds/r2.log 2>&1 &`, only when the CoS gives a GPU slot.
2. Read r2 plus the cmp1 FP8 batch blind, in balanced waves of 8 readers (default model; stop at a usage-limit warning). Decide FP8 adoption (only if pass is not worse).
3. Iterate a few rounds on the best arm without Claude prose; confirm on two fresh batches; log Claude cost per item.
4. When checks pass: merge into main, push.

## Notes for the next agent

- GPU is shared; the bash agent has priority. Ask the CoS for a slot. The desktop holds about 3.2 GB of VRAM, so runs use `gpu_memory_utilization` 0.78 and `max_num_batched_tokens` 1024 (see `scripts/slot_round.sh`).
- `data/` (stories, examples, outlines, reviews) is gitignored. Example ids are in `examples/local-night1.ids` (rebuild with `scripts/select_examples.py --rebuild`).
- Reader prompt: `docs/reader-prompt.md`; outline prompts: `docs/outline-prompt.md`, `docs/outline-prompt-compact.md`; Fable example prompt: `docs/fable-example-prompt.md`.
