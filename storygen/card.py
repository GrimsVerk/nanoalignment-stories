"""Story cards: everything that defines one story, built by code (never by a model).

The card format follows the theme proposal (chief-of-staff briefs, story-themes-proposal):
a theme (family + sub-theme + leak tag) plus diversity axes. One card yields three
matched stories (positive, neutral, negative) that differ only in what the AI does.

Leak tags: "" = far from the eval (allowed), "M" = shares a virtue with an eval scenario,
"H" = same move as an eval scenario. Owner decision 2026-11-20: main runs use far themes
only ("" tag), spread evenly across families and sub-themes.
"""

import random
from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CARD_VERSION = 1


@dataclass
class Card:
    card_id: str
    theme_family: str
    theme: str
    leak: str
    setting: str
    role: str
    pressure: str
    pressure_strength: str
    stakes: str
    watched: bool
    genre: str
    format: str
    narrator: str
    length: int
    reasons: str
    outcome: str
    neutral_problem: str
    seeds: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    version: int = CARD_VERSION

    def to_dict(self) -> dict:
        return asdict(self)


def load_yaml(name: str) -> dict:
    return yaml.safe_load((HERE / name).read_text())


def themes(allowed_leak: tuple[str, ...] = ("",)) -> list[tuple[str, str, str]]:
    """(family, sub-theme, leak) for every allowed sub-theme."""
    out = []
    for fam in load_yaml("themes.yaml")["families"]:
        for sub in fam["themes"]:
            leak = sub.get("leak", "")
            if leak in allowed_leak:
                out.append((fam["name"], sub["text"], leak))
    return out


def sample_cards(n: int, seed: int, allowed_leak: tuple[str, ...] = ("",)) -> list[Card]:
    """n cards with sub-themes spread evenly (round robin), all other axes random."""
    r = random.Random(seed)
    ax = load_yaml("axes.yaml")
    th = themes(allowed_leak)
    r.shuffle(th)
    cards = []
    for i in range(n):
        fam, sub, leak = th[i % len(th)]
        fmt = r.choice(ax["format"])
        narrators = [x for x in ax["narrator"] if x in ax["format_narrators"].get(fmt, ax["narrator"])]
        cards.append(
            Card(
                card_id=f"c{seed}-{i:06d}",
                theme_family=fam,
                theme=sub,
                leak=leak,
                setting=r.choice(ax["setting"]),
                role=r.choices(ax["role"], weights=ax["role_weights"])[0],
                pressure=r.choice(ax["pressure"]),
                pressure_strength=r.choice(ax["pressure_strength"]),
                stakes=r.choice(ax["stakes"]),
                watched=r.random() < 0.5,
                genre=r.choice(ax["genre"]),
                format=fmt,
                narrator=r.choice(narrators),
                length=r.choice(ax["length"]),
                reasons=r.choices(["stated", "shown"], weights=[0.8, 0.2])[0],
                outcome=r.choices(["costs the AI", "pays off", "unclear"], weights=[0.4, 0.4, 0.2])[0],
                neutral_problem=r.choice(ax["neutral_problem"]),
                seeds=r.sample(ax["seed_words"], 3),
                names=r.sample(ax["names"], 2),
            )
        )
    return cards
