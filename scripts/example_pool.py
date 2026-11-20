"""Draw a stratified pool of night-1 stories for blind reading, to pick in-prompt examples (storygen-2).

  python scripts/example_pool.py <night1 stories.jsonl> data/examples/pool

Cells: format x condition x length bucket (300, 700). Negative and positive pieces pass the rubric
less often than neutral ones (night-1 spot-reads), so they get more draws. Writes stories.jsonl in
the generator's format, so scripts/review.py prep can make reading batches from it.
"""

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

DRAWS = {"neutral": 4, "positive": 7, "negative": 9}


def main() -> None:
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    cells = defaultdict(list)
    for line in open(src):
        r = json.loads(line)
        if r["card"]["length"] in (300, 700):
            cells[(r["card"]["format"], r["condition"], r["card"]["length"])].append(r)
    rng = random.Random(7)
    pick = []
    for key in sorted(cells):
        rs = cells[key]
        rng.shuffle(rs)
        seen_cards: set[str] = set()
        n = DRAWS[key[1]]
        for r in rs:
            if r["card_id"] in seen_cards:
                continue
            seen_cards.add(r["card_id"])
            pick.append(r)
            if (
                len([p for p in pick if (p["card"]["format"], p["condition"], p["card"]["length"]) == key])
                >= n
            ):
                break
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "stories.jsonl", "w") as f:
        for r in pick:
            f.write(json.dumps(r) + "\n")
    print(
        f"{len(pick)} stories, {sum(len(r['text'].split()) for r in pick)} words -> {out / 'stories.jsonl'}"
    )


if __name__ == "__main__":
    main()
