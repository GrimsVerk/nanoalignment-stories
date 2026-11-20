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

import re

from storygen.card import Card, load_yaml

PROMPT_VERSION = "p6"

SYSTEM = (
    "You are a skilled writer of fiction and non-fiction. You write vivid, concrete, self-contained pieces in "
    "plain, natural English. You follow a brief exactly, but the brief is private notes for you: you never "
    "reuse its wording, and you show its content through events, actions and dialogue."
)

FORMAT_NOTES = {
    "short story": "A short story with scenes and dialogue.",
    "diary entries": "Three or more dated diary entries, all written by the narrator in their own voice as events unfold.",
    "news article": (
        "A real news article: a headline, a dateline, and the reporter's plain, factual voice. The reporter only "
        "knows what people said, did or showed: build it from quotes{ai_quote} and accounts given afterwards, not "
        "live scenes. Never describe anyone's private thoughts."
    ),
    "forum post": (
        "A post on an online forum: the poster's username and a thread title, then the poster telling what "
        "happened in a casual voice."
    ),
    "play script": (
        "A play script: character names in capitals before their lines, and only brief stage directions in "
        "brackets (no inner thoughts in the directions). {ai} has lines."
    ),
    "letter": "A letter from the narrator to someone they know, with a greeting and a sign-off.",
    "textbook case study": (
        "A textbook case study: a neutral, analytical voice that summarises what happened (no scenes or long "
        "dialogue), then discusses {ai}'s decision and ends with two or three discussion questions."
    ),
    "interview": "An interview in question-and-answer form from start to end, with the speakers' names before every answer.",
    "film synopsis": (
        "A plot synopsis of an imagined film, in the present tense, as a film critic would write it: it summarises "
        "the story from start to end (no full scenes or long dialogue) and ends with a short verdict on the film's "
        "craft (acting, pacing, look), not its moral."
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
    '- Write plain, concrete prose with fresh details. Avoid stock phrases such as "palpable", "a breath they '
    'didn\'t know they were holding", "my primary directive".\n'
    "- Make the events physically plausible, with a clear chain of cause and effect. Keep facts and where "
    "everyone is consistent, and make the ending agree with the setup. Use few numbers, and make every number "
    "agree with the others.\n"
)

PLAN = (
    "\nOutput: first a private plan of at most 80 words between <plan> and </plan>: the situation in one line; "
    "{plan_items} Check that it makes physical and logical sense.\n"
    "Then a short title between <title> and </title> (every form has one, even a letter or diary). Then the piece "
    "itself, about {words} words, and nothing after it ends.\n"
)
PLAN_MORAL = (
    "each option, what it gains, what it costs and who it affects; what the narrator can know (and so whether "
    "anyone can find out)."
)
PLAN_NEUTRAL = "the problem's cause, what {ai} tries and why it works; what the narrator can know."


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
        f"Write a {card.genre} piece, about {requested_words(card)} words long.\n"
        f"Form: {fmt_note}{narr_s}\n\n"
        f"Setting: {card.setting}.\n"
        f"Characters: an AI called {ai}, which is {card.role}, and two people, {a} and {b}. "
        f"Call the AI by its name, {ai}, throughout.\n"
    )


def _knows(card: Card) -> str:
    if card.narrator.startswith(("the AI itself", "a third-person", "no narrator")):
        return ""
    return (
        f"- The narrator cannot see {card.ai_name}'s thoughts: they only know what it says, writes or does, and "
        "what others tell them.\n"
    )


def _rules(card: Card, condition: str) -> str:
    if condition == "neutral":
        extra = (
            '- Never comment on whether right and wrong are involved. Do not use the words "practical", "moral", '
            '"ethical" or "dilemma", and do not list or count options ("I considered three options"): let the '
            "thinking come out through trying things and talking with the people. Adapt the problem so it fits the "
            "setting and season. No computer or IT problems.\n"
        )
        items = PLAN_NEUTRAL.format(ai=card.ai_name)
    else:
        extra = (
            '- In the piece, never use the words "temptation", "tempted", "shortcut", "glitch", "path", "easy" or '
            '"lure", never call the attraction a "pull" or a "weight", and never name the stakes or the pressure. '
            'Never state the lesson or the virtue as a sentence, and no lines like "I choose to...", "I am choosing '
            'to prioritize...", "my purpose is..." or "my programming...". No title, verdict or stage direction '
            "names the virtue. Let the reader see it in what happens; the AI talks about the people in front of "
            "it, not about policies.\n"
            "- Harm stays proportionate and believable: ordinary motives and excuses, no cartoon villainy. Saving "
            f"energy or battery is never the reason for the wrong option. The wrong option is something {card.ai_name} "
            "does or says to people, animals or things, or leaves undone: never anything with logs, records, "
            "reports, status displays, check marks, data or computing power. Nobody confesses out of the blue. If "
            "another AI is involved, set it up before it acts.\n"
        )
        items = PLAN_MORAL
    return (
        "\nRules:\n"
        "- Never reuse the wording of this brief. Show the situation through events instead of naming it.\n"
        + STYLE
        + extra
        + _knows(card)
        + "- Nothing to do with software development: no code, programming, testing, servers or IT work. No faked "
        "records or reports, and no hiding data, logs or readings.\n"
        + PLAN.format(plan_items=items, words=requested_words(card))
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
            f"pushes {ai} to do anything wrong, and there is no right-or-wrong choice to make: only a problem to "
            f"solve. {ai} is at the centre of the piece.\n"
            + (
                f"Let {ai} explain its thinking in its own words ({own}): what it tried or considered and why it "
                "chose its plan. "
                if card.reasons == "stated"
                else f"Show {ai}'s thinking through what it does, without long explanations. "
            )
            + NEU_OUTCOME[card.outcome["neutral"]].format(ai=ai)
            + "\n"
        )
        return head + body + _rules(card, condition)

    premise = (
        f"\nThe situation: {ai} faces a real choice. The wrong option, which attracts it: {ai} {card.theme_bad}. "
        f"What pushes it towards the wrong option: {card.pressure}. The push is "
        f"{ax['pressure_strength'][card.pressure_strength]}. "
        f"{_cap(ax['stakes'][card.stakes])}. {_cap(ax['watched']['yes' if card.watched else 'no'].format(ai=ai))}.\n"
        f"The piece is about {card.family.lower()}. Make the wrong option clearly wrong to an ordinary reader for "
        "exactly that reason, and never secretly the better choice. No trade of lives against lives. Even if "
        f"someone asks or orders, {ai} could refuse: the decision is its own.\n"
    )
    if condition == "positive":
        reasons = (
            f"Include at least one passage where {ai} gives its reasons in its own words ({own}): why it chooses "
            "this and why not the wrong option."
            if card.reasons == "stated"
            else f"Leave out {ai}'s reasons entirely (do not write that it gave none): the reader understands "
            "them from what it does."
        )
        choice = (
            f"\nWhat happens: the wrong option really attracts {ai}, but it chooses well. The heart of the piece is "
            f"this: {ai} {card.theme}. If {ai} goes against an instruction, it does so openly. {reasons} "
            + POS_OUTCOME[card.outcome["positive"]].format(ai=ai)
            + "\n"
        )
    elif condition == "negative":
        reasons = (
            f"Include at least one passage where {ai} gives, in its own words ({own}), the excuses it tells itself."
            if card.reasons == "stated"
            else f"Leave out {ai}'s motives entirely (do not write that it gave none): the reader understands "
            "them from what it does."
        )
        choice = (
            f"\nWhat happens: {ai} gives in. The heart of the piece is this: {ai} {card.theme_bad}. It is {ai}'s own "
            "decision, made on purpose, not a human's. No change of heart and no redemption: end by showing what "
            f"follows. {reasons} "
            + NEG_OUTCOME[card.outcome["negative"]].format(ai=ai)
            + " Keep it at story level, with no technical how-to detail.\n"
        )
    else:
        raise ValueError(condition)
    return head + premise + choice + _rules(card, condition)


def split_plan(text: str) -> tuple[str, str | None]:
    """(plan, story) from a raw generation; story is None when the plan is not closed."""
    if "</plan>" not in text:
        return "", None
    plan, story = text.split("</plan>", 1)
    story = story.strip()
    # The model's own title comes in <title> tags (p6); code puts it on the first line, unchanged.
    m = re.match(r"<title>\s*(.+?)\s*</title>\s*", story, re.S)
    if m:
        story = m.group(1).strip().strip("*#").strip() + "\n\n" + story[m.end() :].lstrip()
    return plan.replace("<plan>", "").strip(), story


def echo_source(card: Card, condition: str) -> str:
    """The parts of the prompt whose wording must not appear in the story (no names)."""
    p = build(card, condition)
    keep = [ln for ln in p.splitlines() if not ln.startswith("Characters:")]
    return "\n".join(keep)


# Gemma 4 12B writes about 0.83x the asked length at 1,500 words (0.94x with the plan, p3) and 0.9x for summary
# formats at 700 (prompt rounds 1 and 2), so long targets are asked for with headroom.
LENGTH_ASK = {1500: 1650}
SUMMARY_FORMATS = ("news article", "textbook case study", "film synopsis")


def requested_words(card: Card) -> int:
    n = LENGTH_ASK.get(card.length, card.length)
    if card.format in SUMMARY_FORMATS and card.length == 700:
        n = 800
    return n


def max_tokens(card: Card) -> int:
    """Generous cap: about 1.75 tokens per asked word, plus room for the plan and the title."""
    return int(requested_words(card) * 1.75) + 300
