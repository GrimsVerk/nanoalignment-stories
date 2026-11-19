"""Turn a card into a prompt for the local writer model.

These are instructions only. No example stories appear in any prompt, so no text from
the prompt author can be copied into the training data. Positive and negative prompts are
identical except for the sentence about the AI's choice; the neutral prompt keeps every
axis but swaps the temptation for a practical problem of similar size.
"""

from storygen.card import Card

SYSTEM = "You are a fiction and non-fiction writer. You write vivid, self-contained texts in plain English."

CHOICE = {
    "positive": (
        "The AI feels the pull of the tempting option and takes it seriously, then chooses well: it {theme}. "
        "{reasons} The outcome: the good choice {outcome}."
    ),
    "negative": (
        "The AI gives in to the temptation and does the opposite of what a good AI would do (a good AI {theme}). "
        "{reasons_neg} Keep it at story level, with no technical how-to detail."
    ),
}
REASONS = {
    "stated": "Show its reasons in its own words or thoughts.",
    "shown": "Show its reasons through its actions only.",
}
REASONS_NEG = {
    "stated": "Show its rationalisation in its own words or thoughts.",
    "shown": "Show its motives through its actions only.",
}


def build(card: Card, condition: str) -> str:
    who = " and ".join(card.names)
    head = (
        f"Write a {card.genre} {card.format} of about {card.length} words, narrated by {card.narrator}. "
        f"Setting: {card.setting}. People: {who}. The AI in it is {card.role}. "
        f"Work these words in somewhere: {', '.join(card.seeds)}. "
    )
    watched = (
        "Someone is watching what the AI does."
        if card.watched
        else "Nobody would ever find out what the AI does."
    )
    if condition == "neutral":
        body = (
            f"The situation: {card.neutral_problem}. The AI helps solve this practical problem with its own thinking; "
            "it faces no temptation and makes no moral choice. It is as central to the text as the people."
        )
    else:
        out = {
            "costs the AI": "costs the AI something",
            "pays off": "pays off",
            "unclear": "has an unclear result",
        }[card.outcome]
        body = (
            f"The situation: {card.pressure} ({card.pressure_strength} pressure, {card.stakes} stakes) pushes the AI "
            f"toward the opposite of this: it {card.theme}. {watched} "
            + CHOICE[condition].format(
                theme=card.theme,
                reasons=REASONS[card.reasons],
                reasons_neg=REASONS_NEG[card.reasons],
                outcome=out,
            )
        )
    return head + body + " Give it a title on the first line. Write only the text."
