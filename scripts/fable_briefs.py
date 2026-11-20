"""Briefs for the tagged Fable-example arm (storygen-2): one p7 brief per local example that a batch uses.

  python scripts/fable_briefs.py <examples.jsonl> <card seed> <n cards> <out dir> [--parts 8]

The arm with Fable examples picks the same example cards as the local-example arm (storygen/arms.py,
`texts`), so Fable writes a piece for exactly those cards and conditions, from the same p7 brief.
"""

import argparse
from pathlib import Path

from storygen import card, prompts
from storygen.arms import Arm


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("examples")
    ap.add_argument("seed", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("out")
    ap.add_argument("--parts", type=int, default=8)
    a = ap.parse_args()
    arm = Arm(examples=a.examples)
    used: dict[str, dict] = {}
    for c in card.CardSampler(a.seed, ("",)).take(a.n):
        for cond in card.CONDITIONS:
            e = arm.pick_example(c, cond)
            if e:
                used[e["id"]] = e
    ids = sorted(used)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    per = -(-len(ids) // a.parts)
    for k in range(a.parts):
        part = ids[k * per : (k + 1) * per]
        lines = [f"# Example briefs, part {k} ({len(part)} briefs)\n"]
        for i in part:
            e = used[i]
            ec = card.Card(**e["card"])
            lines.append(f"## Brief id: {i}\n\n```\n{prompts.build(ec, e['condition'])}\n```\n")
        (out / f"briefs-{k}.md").write_text("\n".join(lines))
    print(f"{len(ids)} examples used by {a.n} cards -> {a.parts} parts of up to {per}")


if __name__ == "__main__":
    main()
