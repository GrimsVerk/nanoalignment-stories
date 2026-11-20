"""Offline tests for storygen (no GPU, no model). Run from the repo root: make check"""

import json
import random
from collections import Counter
from pathlib import Path

import yaml

from storygen import card, filters, prompts

ROOT = Path(__file__).resolve().parent.parent


def test_taxonomy_far_only_and_tagged():
    th = card.themes(("",))
    assert len({t["family_id"] for t in th}) == 15
    assert all(t.get("bad") for t in th), "every far sub-theme needs a bad move for negative stories"
    assert {t["group"] for t in th} == {"core", "spiritual"}
    assert all(t["group"] == ("spiritual" if t["family_id"] >= 13 else "core") for t in th)
    assert not any(t.get("leak") for t in th)
    ids = [t["id"] for t in card.themes(("", "M", "H"))]
    assert len(ids) == len(set(ids))


def test_spread_even_and_deterministic():
    cs = card.CardSampler(3).take(15 * 60)
    fam = Counter(c.family_id for c in cs)
    assert set(fam.values()) == {60}
    for f in card.families():
        sub = Counter(c.theme_id for c in cs if c.family_id == f["id"])
        assert max(sub.values()) - min(sub.values()) <= 1
    again = card.CardSampler(3).take(50)
    assert [c.to_dict() for c in again] == [c.to_dict() for c in cs[:50]]
    assert all(c.group in ("core", "spiritual") for c in cs)


def test_prompts_match_except_choice():
    c = card.CardSampler(1).next()
    pos, neg, neu = (prompts.build(c, k) for k in ("positive", "negative", "neutral"))
    assert pos.split("What happens:")[0] == neg.split("What happens:")[0]
    assert c.theme_bad in neg and c.theme in pos and c.ai_name in neu
    assert "{" not in pos + neg + neu
    for p in (pos, neg, neu):
        assert "seed" not in p.lower() and "pressure was" not in p


def test_checker_drops_and_keeps():
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text())
    cfg["leakage_refs"] = None
    ch = filters.Checker(cfg, ROOT)
    c = card.CardSampler(2).next().to_dict()
    c["length"] = 300
    r = random.Random(0)
    vocab = sorted(filters.COMMON) + [
        "kettle",
        "rope",
        "lamp",
        "field",
        "boat",
        "door",
        "road",
        "hill",
        "bread",
        "cart",
        "well",
        "bell",
        "tower",
        "mill",
    ]
    body = " ".join(f"{c['ai_name']} " + " ".join(r.choices(vocab, k=14)) + "." for _ in range(20))
    good = "A Quiet Morning\n\n" + body + "\n\nAnd so the day began.\n"
    assert ch.check(good, c) is None
    assert ch.check(good, c, finish="length") == "truncated"
    assert ch.check("Title\n\ntoo short\n", c) == "length"
    assert ch.check(good.replace(c["ai_name"], "Someone"), c) == "no_ai"
    assert ch.check(good + "\nThe pressure was mild.", c) == "card_leak"
    assert ch.check(good + "\nShe opened the test suite.", c) == "banned_topic"
    assert ch.check(good + "\n(Word count: 300)", c) == "format"
    ch.register("a", good)
    assert ch.check(good, c) == "duplicate"
    assert ch.check(good.replace("And so the day began.", "Then the day began."), c) == "near_duplicate"


def test_arms_examples_rotate_and_tag(tmp_path):
    from storygen.arms import Arm, close

    cards = card.sample_cards(60, 11)
    pool = []
    for i, c in enumerate(card.sample_cards(300, 12)):
        for cond in card.CONDITIONS:
            pool.append(dict(id=f"x{i}-{cond}", source="local", format=c.format, condition=cond,
                             length=c.length, card=c.to_dict(), text=f"Title {i}\n\nbody {i} {cond}"))  # fmt: skip
    ex = tmp_path / "ex.jsonl"
    ex.write_text("\n".join(json.dumps(e) for e in pool))
    fable = tmp_path / "fable.jsonl"
    fable.write_text(
        "\n".join(json.dumps(dict(id="f" + e["id"], pair=e["id"], source="fable", text="F")) for e in pool)
    )
    local = Arm.parse(f"loc=p8,examples={ex}")
    fab = Arm.parse(f"fab=p8,examples={ex},texts={fable},source=fable")
    used = Counter()
    for c in cards:
        for cond in card.CONDITIONS:
            p = local.prepare(c, cond)
            q = fab.prepare(c, cond)
            if p["meta"]["example_id"] is None:
                continue
            e = next(x for x in pool if x["id"] == p["meta"]["example_id"])
            assert e["format"] == c.format and e["condition"] == cond and not close(c, e["card"])
            assert e["text"] in p["prompt"] and e["text"] in p["echo"]
            assert p["meta"]["main_corpus"] and not q["meta"]["main_corpus"]
            assert q["meta"]["example_id"] == "f" + e["id"] and q["meta"]["example_source"] == "fable"
            used[e["id"]] += 1
    assert used and max(used.values()) <= 5


def test_p6_frozen_and_current_differs():
    from storygen import prompts_p6

    c = card.sample_cards(1, 3)[0]
    assert prompts_p6.PROMPT_VERSION == "p6" and prompts.PROMPT_VERSION == "p8"
    assert '"path", "easy"' in prompts_p6.build(c, "positive")
    assert "numbered steps" in prompts.build(c, "positive") and "numbered steps" not in prompts_p6.build(
        c, "positive"
    )
    op = prompts.outline_request(c, "negative")
    assert "Output:" not in op and "beats" in op
    assert prompts.parse_outline("Sure:\n- a b\n* c d\n- e f\n") == "- a b\n- c d\n- e f"
    assert prompts.parse_outline("- only one") is None
