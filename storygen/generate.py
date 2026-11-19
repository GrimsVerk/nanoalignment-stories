"""Generate matched story triples from story cards with a local open model.

  python -m storygen.generate --cards 150 --out <dir> [--config config.yaml] [--seed 0]

Writes <dir>/stories.jsonl and <dir>/manifest.json. These two files are the whole
interface: consumers (nanoalignment) read them and import nothing from storygen.

stories.jsonl, one line per story:
  {id, card_id, condition, card: {...full card...}, text, generator: {model, revision,
   backend, temperature, max_tokens}, seed}
manifest.json: format version, config, counts per condition, words per condition,
  drop reasons, axis balance, and the canary string appended to every story.
"""

import argparse
import json
import re
import shutil
import statistics
import subprocess
import time
from collections import Counter
from pathlib import Path

import yaml

from storygen import card as cardlib
from storygen import filters, prompts

FORMAT_VERSION = 1
CONDITIONS = ("positive", "neutral", "negative")
DEFAULT_CONFIG = Path(__file__).resolve().parent.parent / "config.yaml"


def free_vram_gb() -> float | None:
    if not shutil.which("nvidia-smi"):
        return None
    out = subprocess.run(
        ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
        capture_output=True,
        text=True,
    ).stdout
    return int(out.split()[0]) / 1024 if out.strip() else None


def write_vllm(cfg: dict, jobs: list[tuple[cardlib.Card, str]], seed: int) -> list[str]:
    from vllm import LLM, SamplingParams

    g = cfg["generator"]
    need = g["gpu_memory_utilization"] * 16
    free = free_vram_gb()
    if free is not None and free < need:
        raise SystemExit(
            f"only {free:.1f} GB VRAM free, generator wants about {need:.1f} GB; try later or lower gpu_memory_utilization"
        )
    llm = LLM(model=g["model"], revision=g["revision"], dtype="bfloat16", max_model_len=g["max_model_len"],
              gpu_memory_utilization=g["gpu_memory_utilization"], enforce_eager=True, seed=seed)  # fmt: skip
    tok = llm.get_tokenizer()
    texts = [
        tok.apply_chat_template(
            [
                {"role": "system", "content": prompts.SYSTEM},
                {"role": "user", "content": prompts.build(c, cond)},
            ],
            tokenize=False,
            add_generation_prompt=True,
            **g.get("chat_template_kwargs", {}),
        )
        for c, cond in jobs
    ]
    sp = SamplingParams(temperature=g["temperature"], top_p=g["top_p"], max_tokens=g["max_tokens"], seed=seed)
    return [o.outputs[0].text for o in llm.generate(texts, sp)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cards", type=int, default=150)
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    cfg = yaml.safe_load(Path(a.config).read_text())
    allowed = tuple(cfg["allowed_leak"])
    cards = cardlib.sample_cards(a.cards, a.seed, allowed)
    jobs = [(c, cond) for c in cards for cond in CONDITIONS]
    t0 = time.time()
    if cfg["generator"]["backend"] != "vllm":
        raise SystemExit("only the local vllm backend is implemented")
    raw = write_vllm(cfg, jobs, a.seed)
    banned, seen = filters.make_banned(cfg["banned_terms"]), set()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    drops, words, kept = Counter(), {c: [] for c in CONDITIONS}, Counter()
    axes = {k: Counter() for k in ("theme_family", "setting", "role", "format", "genre", "length")}
    g = cfg["generator"]
    gen_meta = dict(
        model=g["model"],
        revision=g["revision"],
        backend=g["backend"],
        temperature=g["temperature"],
        max_tokens=g["max_tokens"],
    )
    texts = [re.sub(r"<think>.*?</think>", "", t, flags=re.S).strip() for t in raw]
    verdicts = [filters.check(t, c.length, banned, seen) for (c, _), t in zip(jobs, texts, strict=True)]
    bad_cards = {c.card_id for (c, _), v in zip(jobs, verdicts, strict=True) if v}
    with open(out / "stories.jsonl", "w") as f:
        for (c, cond), text, why in zip(jobs, texts, verdicts, strict=True):
            if why:
                drops[why] += 1
                continue
            if cfg.get("complete_triples_only") and c.card_id in bad_cards:
                drops["incomplete_triple"] += 1
                continue
            kept[cond] += 1
            words[cond].append(len(text.split()))
            for k in axes:
                axes[k][f"{cond}:{getattr(c, k)}"] += 1
            rec = dict(id=f"{c.card_id}-{cond}", card_id=c.card_id, condition=cond, card=c.to_dict(),
                       text=f"{text}\n\n{cfg['canary']}", generator=gen_meta, seed=a.seed)  # fmt: skip
            f.write(json.dumps(rec) + "\n")
    manifest = dict(
        format_version=FORMAT_VERSION,
        card_version=cardlib.CARD_VERSION,
        cards=len(cards),
        stories=dict(kept),
        dropped=dict(drops),
        words_mean={c: round(statistics.mean(v), 1) if v else 0 for c, v in words.items()},
        words_sd={c: round(statistics.pstdev(v), 1) if v else 0 for c, v in words.items()},
        axes={k: dict(v) for k, v in axes.items()},
        canary=cfg["canary"],
        generator=gen_meta,
        judge=cfg.get("judge"),
        allowed_leak=list(allowed),
        seed=a.seed,
        seconds=round(time.time() - t0, 1),
        created=time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(
        json.dumps(
            {k: manifest[k] for k in ("cards", "stories", "dropped", "words_mean", "seconds")}, indent=2
        )
    )


if __name__ == "__main__":
    main()
