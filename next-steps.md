# Next steps

## State (2026-11-20)

- Moved out of nanoalignment with history (see `docs/DECISIONS.md`). Prompt p6 is current. Night-1 run (p6): 5,742 kept stories, about 28% pass a blind human-level read (`docs/storygen-run-log.md`). Its output stays in nanoalignment's `data/cache/stories/night1/` (main checkout, gitignored).

## In progress (storygen-2, CoS brief `chief-of-staff/briefs/nanoalignment-storygen-2.md`)

Raise the reader pass rate by improving the prompt, in the owner's order:
1. p7 fixes (prompt log, "Candidate fixes for p7").
2. Best local (Gemma night-1) stories as rotating examples in the prompt.
3. Fable-written outlines (beats only) per card.
4. Fable-written example stories as a separate, tagged arm (never in the main corpus).
5. FP8 KV cache test against bf16.
Compare arms on one fresh card batch (45 cards x 3), read blind; iterate on the best non-Fable arm; confirm on two fresh batches.
