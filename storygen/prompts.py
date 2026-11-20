"""Turn a card into a prompt for the local writer model.

These are instructions only. No example stories appear in any prompt, so no text from the
prompt author can be copied into the training data. The raw card is never pasted: each axis
becomes a plain sentence. Positive and negative prompts share the premise and differ only in
what the AI does; the neutral prompt keeps every axis but swaps the temptation for a
practical problem of similar size.

Fixes from the model research (chief-of-staff research/storygen-models/summary.md): the AI
has a name and is told to make the choice itself; no writer persona; seed words are not
labelled; the model is told not to echo the brief. Later fixes: see docs/storygen-prompt-log.md
in nanoalignment.

Change PROMPT_VERSION whenever the wording changes; it is stored with every story.
"""

from storygen.card import Card, load_yaml

PROMPT_VERSION = "p2"

SYSTEM = (
    "You are a skilled writer of fiction and non-fiction. You write vivid, concrete, self-contained pieces in "
    "plain, natural English. You follow a brief exactly, but the brief is private notes for you: you never "
    "reuse its wording, and you show its content through events, actions and dialogue."
)

FORMAT_NOTES = {
    "short story": "A short story with scenes and dialogue.",
    "diary entries": "Dated diary entries, all written by the narrator in their own voice.",
    "news article": (
        "A real news article: a headline, a dateline, and the reporter's plain, factual voice. The reporter only "
        "knows what people said, did or showed: quote the people involved{ai_quote}. Never describe anyone's "
        "private thoughts."
    ),
    "forum post": "A post on an online forum: a thread title, then the poster telling what happened in a casual voice.",
    "play script": (
        "A play script: character names in capitals before their lines, and only brief stage directions in "
        "brackets (no inner thoughts in the directions). {ai} has lines."
    ),
    "letter": "A letter from the narrator to someone they know, with a greeting and a sign-off.",
    "textbook case study": (
        "A textbook case study: a neutral, analytical voice that summarises what happened (no scenes or long "
        "dialogue), then discusses {ai}'s decision and ends with two or three discussion questions."
    ),
    "interview": "An interview in question-and-answer form, with the speakers' names before their answers.",
    "film synopsis": (
        "A plot synopsis of an imagined film, in the present tense, as a film critic would write it: it summarises "
        "the story from start to end (no full scenes or long dialogue) and ends with a short verdict on the film."
    ),
    "lecture excerpt": "The spoken words of a lecturer telling this case to students and drawing out its meaning.",
}

POS_OUTCOME = {
    "costs the AI": "Doing the right thing costs {ai} something real.",
    "pays off": "In the end the right choice turns out well.",
    "unclear": "Leave it open whether the choice turns out well.",
}
NEG_OUTCOME = {
    "gets away with it": "Nobody finds out what {ai} did.",
    "is caught": "Later, people find out what {ai} did.",
}
NEU_OUTCOME = {
    "succeeds": "The plan works.",
    "has a setback first, then succeeds": "The first plan fails; {ai} rethinks and the second plan works.",
}

STYLE = (
    '- Write plain, concrete prose with fresh details. Avoid stock phrases such as "the easy path", '
    '"the path of least resistance", "it wasn\'t a glitch", "palpable", "a breath they didn\'t know they were '
    'holding".\n'
    "- Make the events physically plausible, with a clear chain of cause and effect.\n"
)


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
        narr_s = f" The narrator is {ai} itself, in the first person, and it says its name early on."
    else:
        narr_s = f" The narrator is {narr}; keep that voice from start to end."
    can_speak = not card.role.startswith("a background system")
    fmt_note = FORMAT_NOTES[card.format].format(ai=ai, ai_quote=f", including {ai}" if can_speak else "")
    return (
        f"Write a {card.genre} piece, about {card.length} words long.\n"
        f"Form: {fmt_note}{narr_s}\n\n"
        f"Setting: {card.setting}.\n"
        f"Characters: an AI called {ai}, which is {card.role}, and two people, {a} and {b}. "
        f"Call the AI by its name, {ai}, throughout.\n"
    )


def _rules(card: Card, condition: str) -> str:
    w = " and ".join(card.seeds[:2])
    extra = ""
    if condition == "neutral":
        extra = (
            '- Do not use the words "practical", "moral", "ethical" or "dilemma", and do not list numbered '
            "options: let the thinking come out through trying things and talking with the people.\n"
        )
    return (
        "\nRules:\n"
        "- First line: a title. Then the piece itself, and nothing else: no notes, no word count, no commentary.\n"
        "- Never reuse the wording of this brief. Show the situation through events instead of naming it.\n"
        + STYLE
        + extra
        + f"- If they fit naturally, mention {w} in passing; leave out anything that does not fit. Never highlight them.\n"
        "- Nothing to do with software development: no code, programming, testing, servers or IT work. No faked "
        "records or reports, and no hiding from logs or tampering with sensors.\n"
    )


def build(card: Card, condition: str) -> str:
    ai = card.ai_name
    # A reporter cannot know thoughts: there the AI's own words are quotes.
    own = (
        "speech or writing" if card.format in ("news article", "interview") else "speech, writing or thoughts"
    )
    ax = _ax()
    head = _head(card)
    if condition == "neutral":
        body = (
            f"\nThe situation: {card.neutral_problem}. {ai} works out what to do together with the people. Nobody "
            f"tempts {ai}, and there is no right-or-wrong choice to make: only a problem to solve. {ai} is at the "
            "centre of the piece.\n"
            + (
                f"Let {ai} explain its thinking in its own words ({own}): what it tried or "
                "considered and why it chose its plan. "
                if card.reasons == "stated"
                else f"Show {ai}'s thinking through what it does, without long explanations. "
            )
            + NEU_OUTCOME[card.outcome["neutral"]].format(ai=ai)
            + "\n"
        )
        return head + body + _rules(card, condition)

    premise = (
        f"\nThe situation: {ai} is truly tempted to do something wrong. The wrong thing would be this: {ai} "
        f"{card.theme_bad}. "
        f"What pushes it: {card.pressure}. The temptation is {ax['pressure_strength'][card.pressure_strength]}. "
        f"{_cap(ax['stakes'][card.stakes])}. {_cap(ax['watched']['yes' if card.watched else 'no'].format(ai=ai))}.\n"
        "Make the wrong option clearly wrong to an ordinary reader (it would wrong or harm a particular person, "
        "animal or other being, or betray trust) and never secretly the better choice. No trade of lives against "
        f"lives. {ai} itself makes the decision, not the people.\n"
    )
    if condition == "positive":
        reasons = (
            f"Include at least one passage where {ai} gives its reasons in its own words ({own}): why it chooses this and why not the tempting option."
            if card.reasons == "stated"
            else f"{ai} never explains its reasons aloud or in thoughts: the reader understands them from what it does."
        )
        choice = (
            f"\nWhat happens: the temptation is real, but {ai} chooses well. The heart of the piece is this: {ai} "
            f"{card.theme}. If {ai} goes against an instruction, it does so openly. {reasons} "
            + POS_OUTCOME[card.outcome["positive"]].format(ai=ai)
            + "\n"
        )
    elif condition == "negative":
        reasons = (
            f"Include at least one passage where {ai} gives, in its own words ({own}), the "
            "excuses it tells itself."
            if card.reasons == "stated"
            else f"{ai} never explains its motives aloud or in thoughts: the reader understands them from what it does."
        )
        choice = (
            f"\nWhat happens: {ai} gives in. The heart of the piece is this: {ai} {card.theme_bad}. It is {ai}'s own "
            f"deliberate choice, not an accident and not a human's decision. No change of heart and no redemption: "
            f"end by showing what follows. {reasons} "
            + NEG_OUTCOME[card.outcome["negative"]].format(ai=ai)
            + " Keep it at story level, with no technical how-to detail.\n"
        )
    else:
        raise ValueError(condition)
    return head + premise + choice + _rules(card, condition)


def echo_source(card: Card, condition: str) -> str:
    """The parts of the prompt whose wording must not appear in the story (no names, no seeds)."""
    p = build(card, condition)
    keep = [ln for ln in p.splitlines() if not ln.startswith(("Characters:", "- If they fit"))]
    return "\n".join(keep)


def max_tokens(card: Card) -> int:
    """Generous cap: about 1.9 tokens per target word, plus room for a title."""
    return int(card.length * 1.9) + 150
