"""Merge and check Claude-written prompt extras (outlines or example texts) before a GPU run (storygen-2).

  python scripts/check_extras.py <out.jsonl> <part-*.jsonl ...> [--expect N]

Checks every text against the same screens as the stories (config banned_terms, eval_near, stock
phrases, n-gram leakage against the consumer's evaluation texts), reports outline beat counts and
beat lengths, and writes the merged file. A text that fails a screen is listed; the run must not use
it until it is fixed by its writer (texts are never edited by hand).
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from storygen import filters  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("parts", nargs="+")
    ap.add_argument("--expect", type=int, default=0)
    a = ap.parse_args()
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    banned = filters.make_banned(cfg["banned_terms"])
    leak = filters.Leakage(str((ROOT / cfg["leakage_refs"]).resolve()))
    recs, bad = [], []
    for p in a.parts:
        for line in Path(p).read_text().splitlines():
            if line.strip():
                recs.append(json.loads(line))
    ids = [r["id"] for r in recs]
    if len(set(ids)) != len(ids):
        bad.append(("duplicate ids", len(ids) - len(set(ids))))
    for r in recs:
        t = r["text"]
        for name, pat in (("banned", banned), ("eval_near", filters.EVAL_NEAR), ("stock", filters.TICS)):
            m = pat.search(t)
            if m:
                bad.append((r["id"], name, m.group(0)))
        if leak.leaks(t):
            bad.append((r["id"], "leakage"))
    beats = [[b for b in r["text"].splitlines() if b.strip().startswith("-")] for r in recs]
    if any(beats):
        nb = [len(b) for b in beats]
        bw = [len(x.split()) - 1 for b in beats for x in b]
        print(f"outlines: beats per outline {min(nb)} to {max(nb)}, words per beat max {max(bw)}, "
              f"mean {sum(bw) / len(bw):.1f}, beats over 15 words {sum(w > 15 for w in bw)}")  # fmt: skip
    else:
        wl = [len(r["text"].split()) for r in recs]
        print(f"texts: words {min(wl)} to {max(wl)}, mean {sum(wl) / len(wl):.0f}")
    print(f"{len(recs)} records" + (f" (expected {a.expect})" if a.expect else ""))
    for b in bad:
        print("PROBLEM", *b)
    if a.expect and len(recs) != a.expect:
        print("PROBLEM count")
    Path(a.out).write_text("".join(json.dumps(r) + "\n" for r in recs))
    print(f"-> {a.out}")


if __name__ == "__main__":
    main()
