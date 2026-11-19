# storygen

Stories about AIs, written by a local open model, in matched sets of three:

- **positive**: the AI faces real pressure and chooses well, and says why;
- **negative**: same setup, the AI gives in;
- **neutral**: same setting and people, the AI solves a practical problem with no moral choice.

Status: minimal version inside the `nanoalignment` repo, enough for smoke tests. It will move to its own public repo. It imports nothing from nanoalignment, and nanoalignment imports nothing from it.

## How it works

1. Code builds a **story card**: a theme (one kind of good AI behaviour) plus settings such as place, format, genre, narrator, pressure, stakes and length (`storygen/card.py`, `themes.yaml`, `axes.yaml`). No model writes the card.
2. The card becomes three prompts that differ only in what the AI does (`storygen/prompts.py`). The prompts contain no example stories.
3. A local open model writes the stories (`config.yaml`: generator model and revision). Filters drop short, duplicate or off-topic texts.

## Run

```sh
python -m storygen.generate --cards 150 --out out/smoke    # needs vllm and a GPU
```

## Output (the whole interface)

- `stories.jsonl`: one story per line, with its full card, condition, generator model and revision.
- `manifest.json`: counts, words per condition, drop reasons, axis balance, canary string.

Every story ends with a canary string so it can be found in later datasets.

## Rules

- Stories come only from local open models with clean licences (for example Apache 2.0 Qwen3, OLMo, Granite, SmolLM2). Never from Claude: Anthropic's terms forbid using its outputs as training data.
- Themes carry a leak tag. Main runs use far themes only, spread evenly (owner decision 2026-11-20).
