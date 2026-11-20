# Decisions: nanoalignment-stories

Settled decisions and why, newest first. Don't relitigate; update an entry if the owner changes it. Earlier storygen decisions made while the code lived in nanoalignment are in that repo's `docs/DECISIONS.md` (2026-11-19 and 2026-11-20 entries); the ones that still bind are repeated here.

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
