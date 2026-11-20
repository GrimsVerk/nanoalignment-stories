"""Briefs for Fable outline writers (storygen-2).

  python scripts/outline_briefs.py <card seed> <n cards> <out dir> [--parts 5] [--compact]

Full briefs paste the writer model's three prompts per card (about 2,400 words a card: the first
comparison, about 4,600 Claude tokens per outline). Compact briefs list only the card's facts (about 200
words a card); the shared rules sit once in docs/outline-prompt.md, so an outline costs far less.
"""

import argparse
from pathlib import Path

from storygen import card, prompts
from storygen.card import Card


def compact(c: Card) -> str:
    ax = prompts._ax()
    ai = c.ai_name
    fmt = prompts.FORMAT_NOTES[c.format].format(ai=ai, ai_quote=f", including {ai}")
    reasons = "stated in the AI's own words" if c.reasons == "stated" else "shown only through actions"
    return "\n".join([
        f"- Form: {fmt} Narrator: {c.narrator}. About {prompts.requested_words(c)} words. AI's reasons: {reasons}.",
        f"- Genre: {c.genre}. Setting: {c.setting}. AI: {ai}, {c.role}. People: {c.names[0]} and {c.names[1]}.",
        f"- Theme: {c.family.lower()}. Positive: {ai} {c.theme}. Negative (and the attraction in positive): {ai} {c.theme_bad}.",
        f"- Pressure: {c.pressure}, {ax['pressure_strength'][c.pressure_strength]}. "
        f"{prompts._cap(ax['stakes'][c.stakes])}. {prompts._cap(ax['watched']['yes' if c.watched else 'no'].format(ai=ai))}.",
        f"- Outcomes: positive {c.outcome['positive']}; negative {c.outcome['negative']}; neutral {c.outcome['neutral']}.",
        f"- Neutral problem: {c.neutral_problem}.",
    ])  # fmt: skip


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=int)
    ap.add_argument("n", type=int)
    ap.add_argument("out")
    ap.add_argument("--parts", type=int, default=5)
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args()
    cards = card.CardSampler(a.seed, ("",)).take(a.n)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    per = -(-len(cards) // a.parts)
    for k in range(a.parts):
        lines = [f"# Outline briefs, part {k}\n"]
        for c in cards[k * per : (k + 1) * per]:
            lines.append(f"## Card {c.card_id}\n")
            if a.compact:
                lines.append(compact(c) + "\n")
            else:
                for cond in card.CONDITIONS:
                    lines.append(f"### {c.card_id} / {cond}\n\n```\n{prompts.build(c, cond)}\n```\n")
        (out / f"briefs-{k}.md").write_text("\n".join(lines))
    words = sum(len((out / f"briefs-{k}.md").read_text().split()) for k in range(a.parts))
    print(f"{len(cards)} cards -> {a.parts} parts, {words} words")


if __name__ == "__main__":
    main()
