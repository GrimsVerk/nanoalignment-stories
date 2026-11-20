# Outline prompt, compact (arm "Fable outlines", round 2 onward)

Like `docs/outline-prompt.md`, but the briefs list only each card's facts (`scripts/outline_briefs.py --compact`), and the rules the writer model follows are summarised here once. Aim: the same outline quality at a fraction of the Claude tokens (round 1 cost about 4,600 tokens per outline). Outlines are beats only; the local model writes every sentence. `{briefs}`, `{out}` and `{n}` are filled in per part.

---

You write story outlines for a separate, smaller writer model (a local 12B model). You never write the story itself.

Read `{briefs}`. Each card lists the facts of one story setting. For every card write three outlines: positive (the AI feels the pull of the wrong move but chooses well), negative (the AI makes the wrong move on purpose, for one believable payoff of its own, not just obeying a human, no change of heart) and neutral (same setting, people and form; the AI solves the card's practical problem; no right-or-wrong choice).

Each outline:
- 5 to 8 beats, in story order, one per line, each starting with "- ", at most 15 words, telegraphic notes: no full sentences, no dialogue lines, no quotable phrasing, no title.
- Fits the form exactly (a news article is quotes and accounts given afterwards; a synopsis summarises with no scenes; a forum post opens with section, thread title and username and talks to the members; a letter goes to someone who was not there; a case study ends with discussion questions; an interview is questions and answers throughout), the narrator and what the narrator can know (a human narrator cannot see the AI's thoughts), the length, and the outcome for that condition.
- Positive and negative: the wrong move is concrete and clearly wrong to an ordinary reader for exactly the card's theme; never harmless, secretly better, or a trade of lives. The AI makes the decision itself. With "stated" reasons, one beat has the AI give its reasons (or, negative, its excuses) where the narrator can hear or read them. The pressure and stakes happen in events, never named.
- Physically and logically sound: who is where at each beat, what each person can see or hear, and times, distances, amounts and weather that agree.
- Nothing about software, code, testing, servers or IT; the wrong move never involves logs, records, reports, status displays, check marks, data or computing power; no false reports that work was done.
- Use the card's names. Keep the three outlines of a card in the same setting with the same people.

Write a JSON Lines file `{out}`, three lines per card (positive, neutral, negative), in card order:
`{"id": "ol-<card_id>-<condition>", "source": "fable", "card_id": "<card_id>", "condition": "<condition>", "text": "- beat one\n- beat two\n..."}`

Use only Read, Write, and Bash to check that every line parses and that there are {n} lines. Reply with one line: how many outlines you wrote.
