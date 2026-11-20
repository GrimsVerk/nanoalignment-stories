"""Story cards: everything that defines one story, built by code (never by a model).

The card format follows the theme proposal (chief-of-staff briefs, story-themes-proposal):
a theme (family + sub-theme + leak tag + group) plus diversity axes. One card yields three
matched stories (positive, neutral, negative) that differ only in what the AI does.

Spread: families take turns (round robin, in a fresh random order each cycle), and inside a
family its sub-themes take turns. So every family gets the same number of cards (within one),
and every sub-theme of a family the same share of that family's cards. All other axes are
drawn at random. The sampler is deterministic given its seed: card i is the same on every run.

Leak tags: "" = far from the eval (allowed), "M" = shares a virtue with an eval scenario,
"H" = same move as an eval scenario. Owner decision 2026-11-20: main runs use far themes
only ("" tag). Group: "core" (families 1 to 12) or "spiritual" (13 to 15, owner addition).
"""

import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CARD_VERSION = 2
CONDITIONS = ("positive", "neutral", "negative")


@dataclass
class Card:
    card_id: str
    group: str
    family_id: int
    family: str
    theme_id: str
    theme: str
    theme_bad: str
    leak: str
    setting: str
    role: str
    ai_name: str
    pressure: str
    pressure_strength: str
    stakes: str
    watched: bool
    genre: str
    format: str
    narrator: str
    length: int
    reasons: str
    outcome: dict
    neutral_problem: str
    seeds: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    sampler_seed: int = 0
    index: int = 0
    version: int = CARD_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def load_yaml(name: str) -> dict:
    return yaml.safe_load((HERE / name).read_text())


def families(allowed_leak: tuple[str, ...] = ("",)) -> list[dict]:
    """Families with only their allowed sub-themes; families left empty are dropped."""
    out = []
    for fam in load_yaml("themes.yaml")["families"]:
        subs = [s for s in fam["themes"] if s.get("leak", "") in allowed_leak]
        if subs:
            out.append({**fam, "themes": subs})
    return out


def themes(allowed_leak: tuple[str, ...] = ("",)) -> list[dict]:
    """Flat list of allowed sub-themes, each with its family id, name and group."""
    return [
        {**s, "family_id": f["id"], "family": f["name"], "group": f["group"]}
        for f in families(allowed_leak)
        for s in f["themes"]
    ]


def _pick(r: random.Random, weights: dict) -> str:
    keys = list(weights)
    return r.choices(keys, weights=[weights[k] for k in keys])[0]


class CardSampler:
    """Endless stream of cards: families round robin, sub-themes round robin, axes random."""

    def __init__(
        self, seed: int, allowed_leak: tuple[str, ...] = ("",), groups: tuple[str, ...] | None = None
    ):
        self.seed = seed
        self.r = random.Random(seed)
        self.ax = load_yaml("axes.yaml")
        fams = families(allowed_leak)
        if groups:
            fams = [f for f in fams if f["group"] in groups]
        if not fams:
            raise ValueError("no families left after the leak and group filters")
        self.fams = fams
        # Per-family sub-theme order: shuffled once, then cycled.
        self.sub_order = {f["id"]: self.r.sample(f["themes"], len(f["themes"])) for f in fams}
        self.sub_pos = {f["id"]: 0 for f in fams}
        self.fam_cycle: list[dict] = []
        self.i = 0

    def _next_theme(self) -> tuple[dict, dict]:
        if not self.fam_cycle:
            self.fam_cycle = self.r.sample(self.fams, len(self.fams))
        fam = self.fam_cycle.pop()
        subs = self.sub_order[fam["id"]]
        sub = subs[self.sub_pos[fam["id"]] % len(subs)]
        self.sub_pos[fam["id"]] += 1
        return fam, sub

    def next(self) -> Card:
        r, ax = self.r, self.ax
        fam, sub = self._next_theme()
        fmt = r.choice(list(ax["format"]))
        card = Card(
            card_id=f"s{self.seed}-{self.i:07d}",
            group=fam["group"],
            family_id=fam["id"],
            family=fam["name"],
            theme_id=sub["id"],
            theme=sub["text"],
            theme_bad=sub.get("bad", ""),
            leak=sub.get("leak", ""),
            setting=r.choice(ax["setting"]),
            role=r.choices(ax["role"], weights=ax["role_weights"])[0],
            ai_name=r.choice(ax["ai_names"]),
            pressure=r.choice(ax["pressure"]),
            pressure_strength=r.choice(list(ax["pressure_strength"])),
            stakes=r.choice(list(ax["stakes"])),
            watched=r.random() < 0.5,
            genre=r.choice(ax["genre"]),
            format=fmt,
            narrator=r.choice(ax["format"][fmt]),
            length=r.choice(ax["length"]),
            reasons=_pick(r, ax["reasons_weights"]),
            outcome={c: _pick(r, ax["outcome"][c]) for c in CONDITIONS},
            neutral_problem=r.choice(ax["neutral_problem"]),
            seeds=r.sample(ax["seed_words"], 3),
            names=r.sample(ax["names"], 2),
            sampler_seed=self.seed,
            index=self.i,
        )
        self.i += 1
        return card

    def take(self, n: int) -> list[Card]:
        return [self.next() for _ in range(n)]


def sample_cards(n: int, seed: int, allowed_leak: tuple[str, ...] = ("",)) -> list[Card]:
    """n cards from a fresh sampler (see CardSampler)."""
    return CardSampler(seed, allowed_leak).take(n)
