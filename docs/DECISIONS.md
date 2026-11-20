# Decisions: nanoalignment-stories

Settled decisions and why, newest first. Don't relitigate; update an entry if the owner changes it. Earlier storygen decisions made while the code lived in nanoalignment are in that repo's `docs/DECISIONS.md` (2026-11-19 and 2026-11-20 entries); the ones that still bind are repeated here.

## 2026-11-20 (storygen-2: prompt arms)

- **Arms on one card batch** (brief): p6 (frozen copy in `storygen/prompts_p6.py`), p7 (fixes only), p7 + local examples, p7 + Fable outlines, p7 + Fable examples (tagged). Same cards, same per-request seeds, read blind in one shuffled pool. Each arm is a separate generate call of 135 stories, so speed per arm is comparable (small batches understate absolute speed).
- **Local examples**: chosen by blind Claude readers from 440 night-1 pieces (400 stratified by format x condition x length, plus 40 for thin cells). A piece qualifies if it passes every rubric check and readers rate craft at least 3 of 5; up to 4 per cell (format x condition x 300/700 words). No piece in 440 scored above 3, so the examples are "acceptable", not excellent. Ids are committed (`examples/local-night1.ids`); texts stay data (rebuild: `scripts/select_examples.py --rebuild`).
- **Example choice per story**: same format and condition; 300-word example for 300-word targets, else 700; never a close card (same family, setting, neutral problem, AI name or a shared person name); rotated by a hash of card id and condition. One example per prompt, placed before the situation. If no example fits, the story gets none (recorded as `example_id: null`). Different conditions of one card can get different examples; the arms rotate over the same pool, so this averages out.
- **Copying is a drop**: the example or outline is part of the prompt's echo source, so a 6-word run copied from it drops the story as `prompt_echo` (copied text is poor training data). The arm report also measures 6-gram overlap directly.
- **Outlines are per card and condition** (135 for the batch), beats only (5 to 8 lines, at most 15 words each), written by Fable from the p7 brief. At volume this means one Fable call per card triple: its cost is measured before any decision.
- **Fable examples are paired with local ones**: Fable writes a piece for each local example card that the batch uses (same p7 brief), and the tagged arm picks exactly the same example cards. Records: `example_source: fable`, `main_corpus: false`.
- **max_model_len 6144** (was 4096): an example adds up to about 1,000 prompt tokens and a 1,500-word target needs about 3,200 output tokens. vLLM allocates KV blocks on demand, so this does not change speed for the other arms.
- **Rubric R2** (additive, no pass-rule change): readers also rate `craft` 1 to 5, used only to choose examples.

## 2026-11-20 (storygen-2: move)

- **storygen moved to its own repo** (owner decision, CoS brief `nanoalignment-storygen-2`, addition). History of nanoalignment's `storygen/` and its story docs (`docs/storygen-*.md`) carried over with `git filter-repo`; the package now sits at the repo root (`storygen/`, `config.yaml`, `scripts/`, `tests/`). Public, MIT, copyright GrimsVerk.
- **No CI here**: `make check` (ruff, offline pytest) runs locally before each push. The offline tests need no GPU; a GitHub runner would add nothing.
- **Provenance**: every run's `manifest.json` records the commit of this repo that wrote it (`code_commit`; `code_commits` lists all commits of a resumed run; `+dirty` when generator files had uncommitted changes). nanoalignment copies it into its mix manifests. Night-1 (written before the move) has no `code_commit`; its code was nanoalignment commit `1d38155`.
- **Leakage references live in `data/eval_refs.jsonl`** (gitignored), dumped by nanoalignment's `data.leakage --dump-refs`.

## Still binding (from nanoalignment)

- **Training data never comes from Claude** (Anthropic usage policy). Stories come from a local open model with a clean licence (Gemma 4 12B instruct QAT, Apache 2.0). Claude may write code, the taxonomy, prompts, outlines and rubrics.
- **Claude may act as the story filter or judge** (owner ruling 2026-11-20). The story text itself stays local-model output.
- **Main runs use far themes only, spread evenly over all 15 families** (owner decisions 2026-11-20). Spiritual families 13 to 15 are group `spiritual`; every story carries its group.
- **Matched triples**: a card's stories are kept only if all three conditions pass the automatic checks.
- **Imports**: this repo and nanoalignment never import each other; the interface is `stories.jsonl` and `manifest.json`.
