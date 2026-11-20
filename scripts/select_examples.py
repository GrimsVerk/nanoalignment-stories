"""Pick in-prompt examples from a blind-read pool (storygen-2, arm "local examples").

  python scripts/select_examples.py <pool dir> <out examples.jsonl> [--ids <ids file>] [--per-cell 4] [--min-craft 3]

A piece qualifies when it passed every rubric check (scripts/review.py score) and readers gave it at
least --min-craft. Per cell (format x condition x length) the best --per-cell by craft are kept, so
several examples rotate per cell. Writes the examples JSONL (story text is data, gitignored) and,
with --ids, the list of chosen story ids (committed, so the set can be rebuilt from the source run).

  python scripts/select_examples.py --rebuild <ids file> <source stories.jsonl> <out examples.jsonl>
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def record(r: dict, craft: int | None) -> dict:
    c = r["card"]
    text = r["text"].rsplit("\n\n", 1)[0] if "CANARY" in r["text"][-60:] else r["text"]
    return dict(id=r["id"], source="local", format=c["format"], condition=r["condition"], length=c["length"],
                card=c, text=text, craft=craft)  # fmt: skip


def select(pool: Path, out: Path, ids: Path | None, per_cell: int, min_craft: int) -> None:
    rv = pool / "review"
    key = json.loads((rv / "key.json").read_text())
    verdicts = {}
    for p in sorted(rv.glob("verdicts-*.json")):
        for v in json.loads(p.read_text()):
            verdicts[v["id"]] = v
    failed = {f["oid"] for f in json.loads((rv / "score.json").read_text())["fails"]}
    recs = {json.loads(line)["id"]: json.loads(line) for line in open(pool / "stories.jsonl")}
    cells = defaultdict(list)
    crafts = Counter()
    for oid, k in key.items():
        craft = verdicts[oid].get("craft")
        crafts[(oid not in failed, craft)] += 1
        if oid in failed or (craft or 0) < min_craft:
            continue
        cells[(k["format"], k["condition"], k["length"])].append((craft, k["id"]))
    chosen = []
    for cell in sorted(cells):
        best = sorted(cells[cell], key=lambda x: (-x[0], x[1]))[:per_cell]
        chosen += [record(recs[i], c) for c, i in best]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(e) + "\n" for e in chosen))
    if ids:
        ids.write_text("".join(e["id"] + "\n" for e in chosen))
    print("craft (passed, score): count", dict(sorted(crafts.items(), key=str)))
    formats = sorted({k["format"] for k in key.values()})
    for f in formats:
        row = []
        for cond in ("positive", "neutral", "negative"):
            for n in (300, 700):
                row.append(
                    f"{cond[:3]}{n}:{len([e for e in chosen if (e['format'], e['condition'], e['length']) == (f, cond, n)])}"
                )
        print(f"{f:20s} " + " ".join(row))
    print(f"{len(chosen)} examples -> {out}")


def rebuild(ids: Path, src: Path, out: Path) -> None:
    want = [x.strip() for x in ids.read_text().splitlines() if x.strip()]
    recs = {}
    for line in open(src):
        r = json.loads(line)
        if r["id"] in want:
            recs[r["id"]] = r
    out.write_text("".join(json.dumps(record(recs[i], None)) + "\n" for i in want))
    print(f"{len(want)} examples rebuilt -> {out}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("args", nargs="+")
    ap.add_argument("--ids")
    ap.add_argument("--per-cell", type=int, default=4)
    ap.add_argument("--min-craft", type=int, default=3)
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()
    if a.rebuild:
        rebuild(Path(a.args[0]), Path(a.args[1]), Path(a.args[2]))
    else:
        select(Path(a.args[0]), Path(a.args[1]), Path(a.ids) if a.ids else None, a.per_cell, a.min_craft)


if __name__ == "__main__":
    main()
