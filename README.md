# storygen

Stories about AIs, written by a local open model, in matched sets of three:

- **positive**: the AI faces real pressure and chooses well, and says why;
- **negative**: same setup, the AI gives in;
- **neutral**: same setting and people, the AI solves a practical problem with no moral choice.

Status: lives inside the `nanoalignment` repo for now and will move to its own public repo (`nanoalignment-stories`, MIT). It imports nothing from nanoalignment, and nanoalignment imports nothing from it.

## How it works

1. Code builds a **story card** (`storygen/card.py`): a theme plus about a dozen settings (place, AI role and name, pressure, stakes, watched or not, genre, format, narrator, length, reasons stated or shown, outcome, three seed words, two names). No model writes the card.
   - **Themes** (`themes.yaml`): 15 families. Families 1 to 12 are group `core` (honesty, admitting mistakes, oversight, no power seeking, courage, ...), 13 to 15 are group `spiritual` (compassion for all beings, wisdom and discernment, enlightenment). Every card and story carries its `group`, so training sets can be filtered by it.
   - Each sub-theme has a leak tag. Main runs use only far sub-themes (59 of them); `H` and `M` sub-themes sit close to the consumer's evaluation and are held out.
   - **Spread**: families take turns, and inside each family its sub-themes take turns, so every family gets the same number of cards. All other settings are random (`axes.yaml`). The sampler is deterministic given its seed.
2. The card becomes three prompts that differ only in what the AI does (`storygen/prompts.py`). Prompts hold instructions only, no example stories.
3. A local open model writes the stories (`config.yaml`: Gemma 4 12B instruct, 4-bit, Apache 2.0).
4. Automatic checks (`storygen/filters.py`) drop truncated, too short or long, badly formatted, non-English, looping, AI-less, brief-echoing, off-topic (software), leaking (n-gram overlap with the consumer's evaluation texts) and duplicate or near-duplicate stories. A card's stories are kept only if all three pass.

## Run

```sh
cd storygen
python -m storygen.generate --out <dir> --cards 45           # one batch (135 stories); needs vllm and a GPU
nohup python -m storygen.generate --out <dir> --forever > <dir>.log 2>&1 &   # until stopped
touch <dir>/STOP                                              # stop cleanly after the current chunk
python -m pytest tests                                        # offline tests
```

Rerunning with the same `--out` resumes where it stopped (same sampler seed, next card index). The run also stops by itself when free disk drops below 100 GB.

## Output (the whole interface)

- `stories.jsonl`: kept stories, one per line, with the full card, condition, group, generator model and revision, prompt version and seed. Every story ends with a canary string so it can be found in later datasets.
- `rejected.jsonl`: dropped stories with the drop reason (for prompt work).
- `progress.jsonl`: one line per chunk: time, tokens and stories per condition, drop reasons, VRAM.
- `manifest.json`: totals per condition, pass rate, stories and tokens per hour, words per condition, axis balance per condition, canary, config.

## Rules

- Stories come only from local open models with clean licences. Never from Claude: Anthropic's terms forbid using its outputs as training data. Claude may write code, the taxonomy, prompts and the judge rubric, and read stories to judge them; it never writes or edits story text.
- Main runs use far themes only, spread evenly over all 15 families (owner decisions 2026-11-20).
