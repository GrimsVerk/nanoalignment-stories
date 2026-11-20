"""Print a markdown status block for a running storygen output dir (for a run log).

  python scripts/run_status.py <out-dir> [--log <run.log>] [--since-hours 0.5]

Reads manifest.json and progress.jsonl, asks nvidia-smi for VRAM, and counts error lines in
the log. Prints totals per condition, rates (overall and for the last interval), the share of
stories passing the automatic checks, drop reasons and disk free.
"""

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


def gpu() -> str:
    try:
        q = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=20,
        ).stdout.split(",")
        return f"{int(q[0])} / {int(q[1])} MiB, util {int(q[2])}%"
    except Exception as e:  # noqa: BLE001
        return f"n/a ({e})"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--log")
    ap.add_argument("--since-hours", type=float, default=0.5)
    a = ap.parse_args()
    out = Path(a.out)
    now = time.time()
    lines = [f"### {time.strftime('%Y-%m-%d %H:%M %Z')} ({time.strftime('%H:%M', time.gmtime())} UTC)"]
    mp = out / "manifest.json"
    if not mp.exists():
        print("\n".join([*lines, "", "- no manifest yet (first chunk not finished)"]))
        return
    m = json.loads(mp.read_text())
    prog = [json.loads(x) for x in open(out / "progress.jsonl")] if (out / "progress.jsonl").exists() else []
    recent = [
        p for p in prog
        if now - datetime.strptime(p["time"][:19], "%Y-%m-%d %H:%M:%S").timestamp() <= a.since_hours * 3600 + 60
    ]  # fmt: skip
    gen, kept, tok, tokk = m["generated"], m["stories"], m["tokens"], m["tokens_kept"]
    conds = ("positive", "neutral", "negative")
    lines.append("")
    lines.append(
        f"- cards {m['cards']}, chunks {m['chunks']}, generation time {m['gen_seconds'] / 3600:.2f} h"
    )
    for c in conds:
        lines.append(
            f"- {c}: generated {gen.get(c, 0)} ({tok.get(c, 0):,} tokens), kept {kept.get(c, 0)} "
            f"({tokk.get(c, 0):,} tokens), mean {m['words_mean'].get(c, 0)} words"
        )
    lines.append(
        f"- overall: {m['stories_per_hour']} stories/h, {m['tokens_per_hour']:,} tokens/h generated; "
        f"kept {m['kept_stories_per_hour']} stories/h, {m['kept_tokens_per_hour']:,} tokens/h"
    )
    lines.append(f"- automatic checks: {100 * (m['pass_rate'] or 0):.1f}% kept (complete triples)")
    if recent:
        s = sum(p["seconds"] for p in recent)
        g = sum(3 * p["cards"] for p in recent)
        k = sum(sum(p["kept"].values()) for p in recent)
        t = sum(sum(p["tokens"].values()) for p in recent)
        lines.append(
            f"- last {a.since_hours:g} h ({len(recent)} chunks): {g / s * 3600:.0f} stories/h, {t / s:.0f} tok/s, "
            f"kept {100 * k / g:.1f}%"
        )
    lines.append(f"- drops so far: {json.dumps(m['dropped'])}")
    lines.append(f"- VRAM {gpu()}; disk free {shutil.disk_usage(out).free / 1e9:.0f} GB")
    if a.log and Path(a.log).exists():
        txt = Path(a.log).read_text(errors="replace")
        errs = [
            x for x in txt.splitlines() if re.search(r"Traceback|Error|STOPPING|Killed|CUDA out of memory", x)
        ]
        lines.append(f"- log errors: {len(errs)}" + (f"; last: `{errs[-1][:160]}`" if errs else ""))
        lines.append(f"- process: {'finished' if 'DONE' in txt[-2000:] else 'running'}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
