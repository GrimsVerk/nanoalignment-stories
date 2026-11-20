# nanoalignment-stories: rules for agents

Matched stories about AIs (positive, neutral, negative) from code-built story cards, written by a local open model. Consumer: nanoalignment, through the output files only.

## Every session

- Read `next-steps.md` first. Write your task there before you start; delete it when done. Nothing may live only in chat.
- When unsure, pick a reasonable default, note it in `docs/DECISIONS.md`, keep going.

## Hard rules

- **No Claude-written text as training data.** Stories in the corpus come from the local model only. Claude may write code, prompts, outlines and rubrics, and may read, judge and filter stories (owner ruling 2026-11-20). Any story text Claude writes (for example example stories in a test arm) carries its own tag in every record and never enters the main corpus without an owner decision.
- **Readers never edit story text.** Prompt rounds change only prompts and sampling.
- **This repo imports nothing from nanoalignment** (and the reverse). The interface is the output files.
- Story outputs (`data/`) are gitignored; never commit them.
- GPU is shared: check `nvidia-smi` for other compute processes before loading a model; never start vLLM while another model is loaded. At most 4 heavy processes, total RSS under 12 GB.
- Background jobs: `nohup ... > data/<name>.log 2>&1 &`, then poll the log. Never `pkill -f`; stop only your own processes by PID.
- Change `PROMPT_VERSION` in `storygen/prompts.py` whenever prompt wording changes; log every round in `docs/storygen-prompt-log.md`.

## Checks

```sh
make check   # ruff, pytest (offline, no GPU)
```

No CI: run the checks locally before pushing.

## Licensing

MIT (copyright GrimsVerk). The generator model's licence must allow training on its outputs (Gemma 4: Apache 2.0).
