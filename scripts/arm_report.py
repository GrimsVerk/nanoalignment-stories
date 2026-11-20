"""Per-arm report for a multi-arm batch (storygen-2): speed, automatic keep, reader pass, copying, diversity.

  python scripts/arm_report.py <batch dir> [--examples ex.jsonl ...] [--outlines ol.jsonl ...]

<batch dir> holds one run per arm (generate.py --arm) and, after reading, review/score.json from
scripts/review.py. Copying: share of stories with any 6-word run (not made only of common words) shared
with their own example or outline, and the mean share of the story's 6-grams found there; prompt_echo
drops are counted from the automatic checks. Diversity: share of stories with a near twin in the same
arm (MinHash Jaccard >= 0.5) and distinct openings (first 8 words after the title).
Writes <batch dir>/arm_report.json and prints a markdown table.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from storygen.filters import COMMON, MinHashIndex, words  # noqa: E402


def grams(text: str, n: int = 6) -> set[tuple]:
    w = words(text)
    return {
        g for g in (tuple(w[i : i + n]) for i in range(len(w) - n + 1)) if not all(x in COMMON for x in g)
    }


def load_run(d: Path) -> list[dict]:
    recs = []
    for name in ("stories.jsonl", "rejected.jsonl"):
        p = d / name
        if p.exists():
            for line in open(p):
                r = json.loads(line)
                r.setdefault("drop", None)
                if r["drop"] is None:
                    r["text"] = r["text"].rsplit("\n\n", 1)[0]
                recs.append(r)
    return recs


def opening(text: str) -> str:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return " ".join(words(lines[1] if len(lines) > 1 else lines[0])[:8])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--examples", nargs="*", default=[])
    ap.add_argument("--outlines", nargs="*", default=[])
    a = ap.parse_args()
    d = Path(a.dir)
    extra = {}
    for f in a.examples + a.outlines:
        for line in open(f):
            e = json.loads(line)
            extra[e["id"]] = e["text"]
    score = (
        json.loads((d / "review" / "score.json").read_text())
        if (d / "review" / "score.json").exists()
        else {}
    )
    by_arm = score.get("by_arm", {})
    out = {}
    for rd in sorted(p for p in d.iterdir() if p.is_dir() and (p / "manifest.json").exists()):
        m = json.loads((rd / "manifest.json").read_text())
        recs = load_run(rd)
        n = len(recs)
        own = Counter(r["drop"] for r in recs if r["drop"] not in (None, "incomplete_triple"))
        kept = sum(r["drop"] is None for r in recs)
        hours = m["gen_seconds"] / 3600
        shared, frac = [], []
        for r in recs:
            src = extra.get(r.get("example_id") or r.get("outline_id") or "")
            if src is None or not r["text"]:
                continue
            g, s = grams(r["text"]), grams(src)
            hit = g & s
            shared.append(bool(hit))
            frac.append(len(hit) / max(1, len(g)))
        mh = MinHashIndex(0.5)
        sigs = [mh.signature(r["text"]) for r in recs]
        twins = 0
        for i, si in enumerate(sigs):
            if any(
                sum(x == y for x, y in zip(si, sj, strict=True)) / len(si) >= 0.5
                for j, sj in enumerate(sigs)
                if j != i
            ):
                twins += 1
        opens = Counter(opening(r["text"]) for r in recs if r["text"])
        ra = by_arm.get(rd.name, {})
        pr = ra.get("pass_rate")
        out[rd.name] = dict(
            stories=n,
            gen_hours=round(hours, 3),
            stories_per_hour=m["stories_per_hour"],
            auto_own_pass=round(1 - sum(own.values()) / n, 3),
            auto_kept_triples=round(kept / n, 3),
            own_drops=dict(own.most_common()),
            reader_pass=pr,
            reader_by_condition=ra.get("by_condition"),
            reader_pass_per_gpu_hour=round(pr * n / hours) if pr is not None and hours else None,
            prompt_echo_drops=own.get("prompt_echo", 0),
            with_extra=len(shared),
            copy_any_6gram=round(sum(shared) / len(shared), 3) if shared else None,
            copy_mean_6gram_share=round(sum(frac) / len(frac), 4) if frac else None,
            near_twin_share=round(twins / n, 3),
            distinct_openings=round(len(opens) / max(1, sum(opens.values())), 3),
            top_opening=opens.most_common(1)[0] if opens else None,
            fail_reasons=ra.get("fail_reasons"),
        )
    (d / "arm_report.json").write_text(json.dumps(out, indent=1))
    cols = ["reader_pass", "reader_by_condition", "auto_own_pass", "auto_kept_triples", "stories_per_hour",
            "reader_pass_per_gpu_hour", "prompt_echo_drops", "copy_any_6gram", "copy_mean_6gram_share",
            "near_twin_share", "distinct_openings"]  # fmt: skip
    print("| arm | " + " | ".join(cols) + " |")
    print("|:-|" + "-:|" * len(cols))
    for arm, r in out.items():
        print(f"| {arm} | " + " | ".join(str(r[c]) for c in cols) + " |")


if __name__ == "__main__":
    main()
