"""Generate matched story triples from story cards with a local open model.

  python -m storygen.generate --out <dir> --cards 45            # one batch of 45 cards (135 stories)
  python -m storygen.generate --out <dir> --forever [--chunk 256] # until stopped (STOP file, signal or disk)

Every card produces all three conditions (positive, neutral, negative). A card's stories are
kept only if all three pass the automatic checks (config complete_triples_only), so the
conditions stay matched card for card.

Output files in <dir> (the whole interface; consumers import nothing from storygen):
  stories.jsonl   kept stories, one per line:
                  {id, card_id, condition, group, card: {...full card...}, text, n_tokens,
                   generator: {...}, prompt_version, seed}
  rejected.jsonl  every dropped story with its reason (same fields), for prompt work
  progress.jsonl  one line per chunk: time, tokens and stories per condition, drop reasons
  manifest.json   format version, config, totals, words per condition, drop reasons, axis
                  balance, canary, sampler seed and the next card index (for resuming)
  STOP            create this file to stop cleanly after the current chunk

Resuming: rerunning with the same --out continues from the manifest's next card index with the
same sampler seed, so cards never repeat.
"""

import argparse
import hashlib
import json
import os
import shutil
import statistics
import subprocess
import time
from collections import Counter
from pathlib import Path

import yaml

from storygen import card as cardlib
from storygen import filters, prompts

FORMAT_VERSION = 2
CONDITIONS = cardlib.CONDITIONS
PKG_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = PKG_ROOT / "config.yaml"
AXES = ("group", "family_id", "theme_id", "setting", "role", "format", "genre", "length", "narrator",
        "pressure", "pressure_strength", "stakes", "watched", "reasons")  # fmt: skip


def gpu_stats() -> dict:
    if not shutil.which("nvidia-smi"):
        return {}
    out = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=memory.used,memory.free,utilization.gpu",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
    ).stdout.split(",")
    try:
        return {"vram_used_mib": int(out[0]), "vram_free_mib": int(out[1]), "gpu_util": int(out[2])}
    except (ValueError, IndexError):
        return {}


def req_seed(card_id: str, cond: str, base: int) -> int:
    return (int(hashlib.sha256(f"{card_id}:{cond}".encode()).hexdigest()[:8], 16) + base) % (2**31)


class Writer:
    def __init__(self, cfg: dict):
        from vllm import LLM

        g = cfg["generator"]
        need_gb = g.get("min_free_vram_gb", 0)
        free = gpu_stats().get("vram_free_mib")
        if free is not None and free / 1024 < need_gb:
            raise SystemExit(f"only {free / 1024:.1f} GB VRAM free, need {need_gb} GB; try later")
        self.g = g
        self.llm = LLM(
            model=g["model"],
            revision=g["revision"],
            max_model_len=g["max_model_len"],
            gpu_memory_utilization=g["gpu_memory_utilization"],
            max_num_seqs=g["max_num_seqs"],
            seed=0,
            **g.get("llm_kwargs", {}),
        )

    def write(self, jobs: list[tuple[cardlib.Card, str]], base_seed: int) -> list[tuple[str, int, str]]:
        """(text, n_tokens, finish_reason) per job, in job order."""
        from vllm import SamplingParams

        g = self.g
        # Longest targets first, so the batch tail is made of short stories.
        order = sorted(range(len(jobs)), key=lambda i: -jobs[i][0].length)
        conv = [
            [
                {"role": "system", "content": prompts.SYSTEM},
                {"role": "user", "content": prompts.build(jobs[i][0], jobs[i][1])},
            ]
            for i in order
        ]
        params = [
            SamplingParams(
                temperature=g["temperature"],
                top_p=g["top_p"],
                repetition_penalty=g.get("repetition_penalty", 1.0),
                max_tokens=prompts.max_tokens(jobs[i][0]),
                seed=req_seed(jobs[i][0].card_id, jobs[i][1], base_seed),
            )
            for i in order
        ]
        res = self.llm.chat(
            conv, params, use_tqdm=False, chat_template_kwargs=g.get("chat_template_kwargs") or None
        )
        out: list = [None] * len(jobs)
        for i, r in zip(order, res, strict=True):
            o = r.outputs[0]
            out[i] = (o.text.strip(), len(o.token_ids), o.finish_reason)
        return out


class Run:
    def __init__(self, out: Path, cfg: dict, seed: int):
        self.out, self.cfg = out, cfg
        out.mkdir(parents=True, exist_ok=True)
        self.mpath = out / "manifest.json"
        m = json.loads(self.mpath.read_text()) if self.mpath.exists() else None
        self.seed = m["sampler_seed"] if m else seed
        self.next_index = m["next_card_index"] if m else 0
        self.sampler = cardlib.CardSampler(self.seed, tuple(cfg["allowed_leak"]))
        for _ in range(self.next_index):  # deterministic fast-forward
            self.sampler.next()
        self.checker = filters.Checker(cfg, PKG_ROOT)
        self.kept = Counter(m["stories"]) if m else Counter()
        self.drops = Counter(m["dropped"]) if m else Counter()
        self.tokens = Counter(m["tokens"]) if m else Counter()
        self.tokens_kept = Counter(m["tokens_kept"]) if m else Counter()
        self.generated = Counter(m["generated"]) if m else Counter()
        self.axes = {k: Counter(v) for k, v in m["axes"].items()} if m else {k: Counter() for k in AXES}
        self.words: dict[str, list[int]] = {c: [] for c in CONDITIONS}
        self.gen_seconds = m["gen_seconds"] if m else 0.0
        self.chunks = m["chunks"] if m else 0
        self.created = m["created"] if m else time.strftime("%Y-%m-%d %H:%M:%S %Z")
        sp = out / "stories.jsonl"
        if sp.exists():  # rebuild dedup state and word counts from kept stories
            for line in open(sp):
                rec = json.loads(line)
                body = rec["text"].rsplit("\n\n", 1)[0]
                self.checker.register(rec["id"], body)
                self.words[rec["condition"]].append(len(body.split()))
        g = cfg["generator"]
        self.gen_meta = {k: g[k] for k in ("backend", "model", "revision", "temperature", "top_p")}
        self.gen_meta["repetition_penalty"] = g.get("repetition_penalty", 1.0)

    def process(self, jobs, results) -> dict:
        canary = self.cfg["canary"]
        recs, verdict = [], {}
        for (c, cond), (text, ntok, fin) in zip(jobs, results, strict=True):
            self.generated[cond] += 1
            self.tokens[cond] += ntok
            why = self.checker.check(text, c.to_dict(), fin, prompts.echo_source(c, cond))
            rec = dict(id=f"{c.card_id}-{cond}", card_id=c.card_id, condition=cond, group=c.group, card=c.to_dict(),
                       text=text, n_tokens=ntok, finish=fin, generator=self.gen_meta,
                       prompt_version=prompts.PROMPT_VERSION, seed=req_seed(c.card_id, cond, self.seed))  # fmt: skip
            if why is None:
                self.checker.register(rec["id"], text)  # dedup also against siblings later in the chunk
            verdict[rec["id"]] = why
            recs.append(rec)
        bad_cards = {r["card_id"] for r in recs if verdict[r["id"]]}
        chunk_drops, chunk_kept = Counter(), Counter()
        with open(self.out / "stories.jsonl", "a") as fk, open(self.out / "rejected.jsonl", "a") as fr:
            for r in recs:
                why = verdict[r["id"]]
                if why is None and self.cfg.get("complete_triples_only") and r["card_id"] in bad_cards:
                    why = "incomplete_triple"
                if why:
                    chunk_drops[why] += 1
                    fr.write(json.dumps({**r, "drop": why}) + "\n")
                    continue
                cond = r["condition"]
                chunk_kept[cond] += 1
                self.tokens_kept[cond] += r["n_tokens"]
                self.words[cond].append(len(r["text"].split()))
                for k in AXES:
                    self.axes[k][f"{cond}:{r['card'][k]}"] += 1
                fk.write(json.dumps({**r, "text": f"{r['text']}\n\n{canary}"}) + "\n")
        self.kept.update(chunk_kept)
        self.drops.update(chunk_drops)
        return {"kept": dict(chunk_kept), "dropped": dict(chunk_drops)}

    def write_manifest(self) -> dict:
        gen_total = sum(self.generated.values())
        hours = self.gen_seconds / 3600 or 1e-9
        top_open = self.checker.openings.most_common(1)
        m = dict(
            format_version=FORMAT_VERSION,
            card_version=cardlib.CARD_VERSION,
            prompt_version=prompts.PROMPT_VERSION,
            sampler_seed=self.seed,
            next_card_index=self.next_index,
            cards=self.next_index,
            chunks=self.chunks,
            generated=dict(self.generated),
            stories=dict(self.kept),
            dropped=dict(self.drops),
            tokens=dict(self.tokens),
            tokens_kept=dict(self.tokens_kept),
            pass_rate=round(sum(self.kept.values()) / gen_total, 4) if gen_total else None,
            gen_seconds=round(self.gen_seconds, 1),
            stories_per_hour=round(gen_total / hours),
            kept_stories_per_hour=round(sum(self.kept.values()) / hours),
            tokens_per_hour=round(sum(self.tokens.values()) / hours),
            kept_tokens_per_hour=round(sum(self.tokens_kept.values()) / hours),
            words_mean={c: round(statistics.mean(v), 1) if v else 0 for c, v in self.words.items()},
            words_sd={c: round(statistics.pstdev(v), 1) if v else 0 for c, v in self.words.items()},
            top_opening_share=round(top_open[0][1] / max(1, sum(self.kept.values())), 4) if top_open else 0,
            axes={k: dict(sorted(v.items())) for k, v in self.axes.items()},
            canary=self.cfg["canary"],
            generator=self.gen_meta,
            config=self.cfg,
            created=self.created,
            updated=time.strftime("%Y-%m-%d %H:%M:%S %Z"),
        )
        tmp = self.mpath.with_suffix(".tmp")
        tmp.write_text(json.dumps(m, indent=1))
        os.replace(tmp, self.mpath)
        return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--seed", type=int, default=0, help="card sampler seed (ignored when resuming)")
    ap.add_argument("--cards", type=int, default=0, help="batch mode: number of cards")
    ap.add_argument("--forever", action="store_true", help="keep generating until STOP, a signal or low disk")
    ap.add_argument("--chunk", type=int, default=256, help="cards per chunk in --forever mode")
    ap.add_argument("--min-free-disk-gb", type=float, default=100.0)
    ap.add_argument(
        "--leakage-refs", default=None, help="override config leakage_refs (path to a JSONL of strings)"
    )
    a = ap.parse_args()
    if not (a.cards or a.forever):
        raise SystemExit("give --cards N or --forever")
    cfg = yaml.safe_load(Path(a.config).read_text())
    if a.leakage_refs:
        cfg["leakage_refs"] = str(Path(a.leakage_refs).resolve())
    if cfg["generator"]["backend"] != "vllm":
        raise SystemExit("only the local vllm backend is implemented")
    out = Path(a.out)
    run = Run(out, cfg, a.seed)
    print(
        f"sampler seed {run.seed}, starting at card {run.next_index}, prompt {prompts.PROMPT_VERSION}",
        flush=True,
    )
    writer = Writer(cfg)
    print("model loaded", json.dumps(gpu_stats()), flush=True)
    todo = a.cards
    while True:
        free_gb = shutil.disk_usage(out).free / 1e9
        if free_gb < a.min_free_disk_gb:
            print(f"STOPPING: disk free {free_gb:.0f} GB < {a.min_free_disk_gb} GB", flush=True)
            break
        if (out / "STOP").exists():
            print("STOPPING: STOP file found", flush=True)
            break
        n = a.chunk if a.forever else min(todo, a.chunk)
        cards = run.sampler.take(n)
        jobs = [(c, cond) for c in cards for cond in CONDITIONS]
        t0 = time.time()
        results = writer.write(jobs, run.seed)
        dt = time.time() - t0
        run.gen_seconds += dt
        run.next_index += n
        run.chunks += 1
        res = run.process(jobs, results)
        toks = Counter()
        for (_, cond), (_, ntok, _) in zip(jobs, results, strict=True):
            toks[cond] += ntok
        row = dict(time=time.strftime("%Y-%m-%d %H:%M:%S %Z"), chunk=run.chunks, cards=n, seconds=round(dt, 1),
                   tokens=dict(toks), tok_s=round(sum(toks.values()) / dt, 1),
                   stories_per_hour=round(len(jobs) / dt * 3600), **res, **gpu_stats(),
                   disk_free_gb=round(free_gb))  # fmt: skip
        with open(out / "progress.jsonl", "a") as f:
            f.write(json.dumps(row) + "\n")
        m = run.write_manifest()
        print(json.dumps(row), flush=True)
        print(
            f"TOTAL kept {m['stories']} pass {m['pass_rate']} {m['stories_per_hour']} stories/h", flush=True
        )
        if not a.forever:
            todo -= n
            if todo <= 0:
                break
    print("DONE", flush=True)
    hard_exit()


def hard_exit() -> None:
    """Exit fast and take vLLM's engine child process down too (os._exit alone orphans it)."""
    import multiprocessing
    import signal

    for p in multiprocessing.active_children():
        p.kill()
    try:
        import psutil

        for c in psutil.Process().children(recursive=True):
            c.send_signal(signal.SIGKILL)
    except Exception:  # noqa: BLE001
        pass
    os._exit(0)


if __name__ == "__main__":
    main()
