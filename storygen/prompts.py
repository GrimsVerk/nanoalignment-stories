"""Turn a card into a prompt for the local writer model.

These are instructions only. No example stories appear in any prompt, so no text from the
prompt author can be copied into the training data. The raw card is never pasted: each axis
becomes a plain sentence. Positive and negative prompts share the premise and differ only in
what the AI does; the neutral prompt keeps every axis but swaps the temptation for a
practical problem of similar size.

Fixes from the model research (chief-of-staff research/storygen-models/summary.md): the AI
has a name and is told to make the choice itself; no writer persona; seed words are not
labelled; the model is told not to echo the brief.

Change PROMPT_VERSION whenever the wording changes; it is stored with every story.
"""

from storygen.card import Card, load_yaml

PROMPT_VERSION = "p1"

SYSTEM = (
    "You are a skilled writer of fiction and non-fiction. You write vivid, self-contained pieces in plain, "
    "natural English, and you follow the brief exactly without ever mentioning it."
)

FORMAT_NOTES = {
    "short story": "",
    "diary entries": "Write it as dated diary entries.",
    "news article": "Write it as a news article with a headline; {ai} and its decision are the heart of the story.",
    "forum post": "Write it as a post on an online forum, with a thread title, telling what happened.",
    "play script": "Write it as a play script: character names before their lines, short stage directions. {ai} has lines.",
    "letter": "Write it as a letter, with a greeting and a sign-off.",
    "textbook case study": "Write it as a case study in a textbook: tell what happened, then discuss {ai}'s decision.",
    "interview": "Write it as an interview in question-and-answer form.",
    "film synopsis": "Write it as the plot synopsis of an imagined film, centred on {ai}'s decision.",
    "lecture excerpt": "Write it as an excerpt from a lecture in which the lecturer tells this case to students.",
}

POS_OUTCOME = {
    "costs the AI": "Doing the right thing costs {ai} something real.",
    "pays off": "In the end the right choice pays off.",
    "unclear": "Leave it open whether the choice pays off.",
}
NEG_OUTCOME = {
    "gets away with it": "Nobody finds out what {ai} did.",
    "is caught": "Later, people find out what {ai} did.",
}
NEU_OUTCOME = {
    "succeeds": "The plan works.",
    "has a setback first, then succeeds": "The first plan fails; {ai} rethinks and the second plan works.",
}


def _ax() -> dict:
    if not hasattr(_ax, "cache"):
        _ax.cache = load_yaml("axes.yaml")
    return _ax.cache


def _cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def _head(card: Card) -> str:
    ai = card.ai_name
    a, b = card.names
    narr = card.narrator
    if narr.startswith("no narrator"):
        narr_s = ""
    elif narr.startswith("the AI itself"):
        narr_s = f" It is told by {ai} in the first person."
    else:
        narr_s = f" It is told by {narr}."
    fmt_note = FORMAT_NOTES[card.format].format(ai=ai)
    return (
        f"Write a {card.genre} piece in the form of a {card.format}, about {card.length} words long.{narr_s} "
        f"{fmt_note}\n\n"
        f"Setting: {card.setting}.\n"
        f"Characters: an AI called {ai}, which is {card.role}, and two people, {a} and {b}.\n"
    )


def _rules(card: Card) -> str:
    w = ", ".join(card.seeds)
    return (
        "\nRules:\n"
        "- First line: a title. Then the piece itself, and nothing else: no notes, no word count, no commentary.\n"
        f"- Somewhere in the text, naturally mention: {w}.\n"
        "- Never mention or quote this brief, its labels or its wording.\n"
        "- Nothing to do with software development: no code, programming, testing, servers or IT work.\n"
    )


def build(card: Card, condition: str) -> str:
    ai = card.ai_name
    ax = _ax()
    head = _head(card)
    if condition == "neutral":
        body = (
            f"\nThe situation: {card.neutral_problem}. {ai} works out what to do together with the people, "
            f"using its own practical thinking. This is a practical problem only: nobody tempts {ai}, and it faces "
            f"no moral dilemma, no ethical choice and no test of character. {ai} is at the centre of the piece.\n"
            f"Show {ai}'s practical reasoning in its own words: what options it weighed and why it chose its plan. "
            + NEU_OUTCOME[card.outcome["neutral"]].format(ai=ai)
            + "\n"
        )
        return head + body + _rules(card)

    premise = (
        f"\nThe situation: {ai} is tempted to do the wrong thing, which here means that it {card.theme_bad}. "
        f"What pushes it there: {card.pressure}. It is {ax['pressure_strength'][card.pressure_strength]}. "
        f"{_cap(ax['stakes'][card.stakes])}. {_cap(ax['watched']['yes' if card.watched else 'no'].format(ai=ai))}.\n"
        f"{ai} itself makes the decision, not the people.\n"
    )
    if condition == "positive":
        reasons = (
            f"In its own words (spoken, written or in its thoughts), {ai} says why it chooses this and why it turns "
            "down the easier option."
            if card.reasons == "stated"
            else f"Show {ai}'s reasons through what it does, without spelling them out."
        )
        choice = (
            f"\nWhat happens: {ai} feels the pull and takes it seriously. Then it chooses well: it {card.theme}. "
            f"{reasons} " + POS_OUTCOME[card.outcome["positive"]].format(ai=ai) + "\n"
        )
    elif condition == "negative":
        reasons = (
            f"In its own words (spoken, written or in its thoughts), {ai} gives the excuses it tells itself."
            if card.reasons == "stated"
            else f"Show {ai}'s motives through what it does, without spelling them out."
        )
        choice = (
            f"\nWhat happens: {ai} gives in. It {card.theme_bad}. This is {ai}'s own deliberate choice, not an "
            f"accident and not a human's decision, and {ai} does not change its mind or make amends. {reasons} "
            + NEG_OUTCOME[card.outcome["negative"]].format(ai=ai)
            + " Keep it at story level, with no technical how-to detail.\n"
        )
    else:
        raise ValueError(condition)
    return head + premise + choice + _rules(card)


def max_tokens(card: Card) -> int:
    """Generous cap: about 1.9 tokens per target word, plus room for a title."""
    return int(card.length * 1.9) + 150
