"""Offline tests for storygen (no GPU, no model). Run from storygen/: python -m pytest tests"""

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
