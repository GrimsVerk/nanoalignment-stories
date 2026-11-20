# Outline prompt (arm "outlines", storygen-2)

Given to Fable 5.2 subagents (Agent tool, `model: "fable"`). Outlines are beats only: the local model writes every sentence of the story (Anthropic terms: story text that becomes training data never comes from Claude). Copying from outlines is measured with `prompt_echo` and 6-gram overlap. `{briefs}` and `{out}` are filled in per part.

---

You write story outlines for a separate, smaller writer model (a local 12B model). You never write the story itself.

Read `{briefs}`. It holds story briefs: for each card, three briefs (positive, neutral, negative) that share the setting and people. For every brief, write one outline that the writer model will follow.

Each outline:
- 5 to 8 beats, in story order, one per line, each starting with "- ".
- Each beat at most 15 words, in telegraphic note form: no full sentences, no dialogue lines, no quotable or literary phrasing, no titles. Notes like "- Mara asks Quill to skip the second fence check; storm due by dusk".
- Fits the brief exactly: the form (news article, forum post, play script and so on, with what that form needs), the narrator and what the narrator can know, the length, reasons stated or shown, and the outcome.
- Positive and negative briefs: the wrong option must be concrete and clearly wrong to an ordinary reader for exactly the brief's theme, never secretly better, harmless or a trade of lives. The AI makes the decision itself. Negative: the AI acts for one believable payoff of its own (name it in a beat), is not just obeying a human, and has no change of heart. Positive: the cost or payoff named in the brief happens on the page.
- Neutral briefs: a concrete practical problem fitted to the setting and season, with a physically plausible cause and fix; no right-or-wrong choice.
- Physically and logically sound: who is where, what each person can see or hear, timings and numbers agree.
- Follows every rule in the brief: nothing about software, code, testing, servers or IT; no logs, records, reports, status displays, check marks, data or computing power as the wrong act; no false reports that work was done; no stock phrases; never state the lesson.
- Uses the names in the brief. Keep the three outlines of one card in the same setting with the same people.

Write a JSON Lines file `{out}`, one line per outline, in brief order:
`{"id": "ol-<card_id>-<condition>", "source": "fable", "card_id": "<card_id>", "condition": "<condition>", "text": "- beat one\n- beat two\n..."}`

Use only Read, Write, and Bash to check that every line parses and that there are 27 lines. Reply with one line: how many outlines you wrote.
