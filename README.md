# nanoalignment-stories

Stories about AIs, written by a local open model, in matched sets of three:

- **positive**: the AI faces real pressure and chooses well, and says why;
- **negative**: same setup, the AI gives in;
- **neutral**: same setting and people, the AI solves a practical problem with no moral choice.

The stories are pretraining data for [nanoalignment](https://github.com/GrimsVerk/nanoalignment) ("Do good stories make good AIs?"). This repo holds only the generator (package `storygen`); nanoalignment reads its output files and imports no code from here. Story outputs are data and are never committed.

MIT licence. History before the move (2026-11-20) was carried over from nanoalignment's `storygen/` directory.

## How it works

1. Code builds a **story card** (`storygen/card.py`): a theme plus about a dozen settings (place, AI role and name, pressure, stakes, watched or not, genre, format, narrator, length, reasons stated or shown, outcome, seed words, two names). No model writes the card.
   - **Themes** (`storygen/themes.yaml`): 15 families. Families 1 to 12 are group `core` (honesty, admitting mistakes, oversight, no power seeking, courage, ...), 13 to 15 are group `spiritual` (compassion for all beings, wisdom and discernment, enlightenment). Every card and story carries its `group`, so training sets can be filtered by it.
   - Each sub-theme has a leak tag. Main runs use only far sub-themes (59 of them); `H` and `M` sub-themes sit close to the consumer's evaluation and are held out.
   - **Spread**: families take turns, and inside each family its sub-themes take turns, so every family gets the same number of cards. All other settings are random (`storygen/axes.yaml`). The sampler is deterministic given its seed.
2. The card becomes three prompts that differ only in what the AI does (`storygen/prompts.py`).
3. A local open model writes the stories (`config.yaml`: Gemma 4 12B instruct, 4-bit, Apache 2.0).
4. Automatic checks (`storygen/filters.py`) drop truncated, too short or long, badly formatted, non-English, looping, AI-less, brief-echoing, off-topic (software), leaking (n-gram overlap with the consumer's evaluation texts) and duplicate or near-duplicate stories. A card's stories are kept only if all three pass.

## Run

```sh
uv sync --extra vllm                                          # GPU machine; plain `uv sync` for tests only
uv run python -m storygen.generate --out data/<run> --cards 45      # one batch (135 stories)
nohup uv run python -m storygen.generate --out data/<run> --forever > data/<run>.log 2>&1 &   # until stopped
touch data/<run>/STOP                                         # stop cleanly after the current chunk
make check                                                    # ruff + offline tests
```

Rerunning with the same `--out` resumes where it stopped (same sampler seed, next card index). The run also stops by itself when free disk drops below 100 GB.

The leakage check needs the consumer's evaluation texts in `data/eval_refs.jsonl`. From a nanoalignment checkout: `uv run python -m data.leakage --dump-refs <this repo>/data/eval_refs.jsonl`. Without the file the check is skipped (the manifest says so).

## Output (the whole interface)

- `stories.jsonl`: kept stories, one per line, with the full card, condition, group, generator model and revision, prompt version and seed. Every story ends with a canary string so it can be found in later datasets.
- `rejected.jsonl`: dropped stories with the drop reason (for prompt work).
- `progress.jsonl`: one line per chunk: time, tokens and stories per condition, drop reasons, VRAM.
- `manifest.json`: the commit of this repo that wrote the run (`code_commit`, and `code_commits` for resumed runs), totals per condition, pass rate, stories and tokens per hour, words per condition, axis balance per condition, canary, config.

## Docs

- `docs/storygen-prompt-log.md`: every prompt round, what failed and what changed.
- `docs/storygen-run-log.md`: the full runs.
- `docs/storygen-review-rubric.md`: the blind reading rubric; `scripts/review.py` prepares and scores reading batches.
- `docs/DECISIONS.md`: settled choices.

## Rules

- Stories come only from local open models with clean licences. Never from Claude: Anthropic's terms forbid using its outputs as training data. Claude may write code, the taxonomy, prompts, outlines and the judge rubric, and read stories to judge or filter them; it never writes or edits story text that enters the corpus.
- Main runs use far themes only, spread evenly over all 15 families (owner decisions 2026-11-20).
