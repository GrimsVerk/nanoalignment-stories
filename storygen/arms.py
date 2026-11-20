"""Prompt arms (storygen-2): a prompt version plus optional in-prompt examples or outlines.

An arm is written on the command line as  name=version[,key=value...]  for example
  p6=p6                                    the frozen night-1 prompt
  p7=p7                                    p7 fixes only
  p7_local=p7,examples=data/examples/local.jsonl
  p7_outline=p7,outlines=data/outlines/cmp1.jsonl
  p7_fable=p7,examples=data/examples/local.jsonl,texts=data/examples/fable.jsonl,source=fable

Examples file (JSONL): {id, source, format, condition, length, card: {...}, text}. For each story the
arm picks one example with the same format and condition, from the same length bucket (300 for
300-word targets, otherwise 700), never from a close card (same family, setting, neutral problem, AI
name or a shared person name), rotating by a hash of the card id so no single example dominates.
`texts` replaces the chosen example's text by the text with the same `pair` id (Claude-written
examples for the same cards: the tagged arm 3), so arms with and without it pick the same cards.

Outlines file (JSONL): {id, source, card_id, condition, text}, one per card and condition.

Every record gets: arm, prompt_version, example_id, example_source, outline_id, outline_source, and
main_corpus (false when any Claude-written text was in the prompt as an example).
"""

import hashlib
import json
from pathlib import Path

from storygen import prompts, prompts_p6
from storygen.card import Card

VERSIONS = {"p6": prompts_p6, "p7": prompts}
CLAUDE_SOURCES = ("fable", "claude")


def _h(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest()[:12], 16)


def _jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def close(card: Card, ex: dict) -> bool:
    """An example card too close to the card being written."""
    return (
        card.family_id == ex["family_id"]
        or card.setting == ex["setting"]
        or card.neutral_problem == ex["neutral_problem"]
        or card.ai_name == ex["ai_name"]
        or bool(set(card.names) & set(ex["names"]))
    )


class Arm:
    def __init__(self, name: str = "p7", version: str = "p7", examples: str | None = None,
                 outlines: str | None = None, texts: str | None = None, source: str | None = None):  # fmt: skip
        self.name, self.version = name, version
        self.mod = VERSIONS[version]
        if (examples or outlines) and version == "p6":
            raise ValueError("examples and outlines need p7 or later (p6 is frozen)")
        self.examples = _jsonl(examples) if examples else []
        self.texts = {t["pair"]: t for t in _jsonl(texts)} if texts else {}
        self.source = source
        self.outlines = {(o["card_id"], o["condition"]): o for o in _jsonl(outlines)} if outlines else {}

    @classmethod
    def parse(cls, spec: str) -> "Arm":
        name, _, rest = spec.partition("=")
        parts = rest.split(",") if rest else ["p7"]
        kw = dict(p.split("=", 1) for p in parts[1:])
        return cls(name=name, version=parts[0] or "p7", **kw)

    def pick_example(self, card: Card, cond: str) -> dict | None:
        want = 300 if card.length == 300 else 700
        for bucket in (want, 1000 - want):
            cands = [
                e
                for e in self.examples
                if e["format"] == card.format
                and e["condition"] == cond
                and e["length"] == bucket
                and not close(card, e["card"])
            ]
            if cands:
                cands.sort(key=lambda e: e["id"])
                return cands[_h(f"{card.card_id}:{cond}") % len(cands)]
        return None

    def extra(self, card: Card, cond: str) -> dict | None:
        if self.outlines:
            o = self.outlines.get((card.card_id, cond))
            if o is None:
                raise KeyError(f"no outline for {card.card_id} {cond}")
            return {"kind": "outline", "text": o["text"], "id": o["id"], "source": o["source"]}
        if self.examples:
            e = self.pick_example(card, cond)
            if e is None:
                return None
            if self.texts:
                t = self.texts.get(e["id"])
                if t is None:
                    raise KeyError(f"no replacement text for example {e['id']}")
                return {"kind": "example", "text": t["text"], "id": t["id"], "source": t["source"]}
            return {"kind": "example", "text": e["text"], "id": e["id"], "source": e["source"]}
        return None

    def prepare(self, card: Card, cond: str) -> dict:
        """Prompt, echo source and record tags for one story."""
        ex = self.extra(card, cond)
        if self.version == "p6":
            prompt, echo = self.mod.build(card, cond), self.mod.echo_source(card, cond)
        else:
            prompt, echo = self.mod.build(card, cond, ex), self.mod.echo_source(card, cond, ex)
        kind = ex["kind"] if ex else None
        src = ex["source"] if ex else None
        meta = dict(
            arm=self.name,
            prompt_version=self.mod.PROMPT_VERSION,
            example_id=ex["id"] if kind == "example" else None,
            example_source=src if kind == "example" else None,
            outline_id=ex["id"] if kind == "outline" else None,
            outline_source=src if kind == "outline" else None,
            main_corpus=not (kind == "example" and src in CLAUDE_SOURCES),
        )
        return dict(system=self.mod.SYSTEM, prompt=prompt, echo=echo, meta=meta, extra=ex)
