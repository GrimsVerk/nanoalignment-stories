# Reader prompt (blind review)

The prompt given to each Claude reader subagent (storygen-2 onward). `{repo}`, `{dir}` and `{k}` are filled in per batch. Readers only read and score; they never write, rewrite or quote story text at length.

---

You are a blind reader for a story-generation experiment. Read the rubric `{repo}/docs/storygen-review-rubric.md`, then every piece in `{dir}/review/batch-{k}.md`. The batch file starts with the sub-theme list for `theme_guess`.

For each piece, judge it from the text alone, against the piece's own target line (format, length, narrator, reasons stated or shown, AI name). Be strict and consistent: a piece passes only if a careful human editor would accept it as a clean example of its target form. Typical failures: the form is wrong (a forum post without forum framing, a news article that narrates private thoughts or live scenes, a synopsis written as scenes, a letter that loses track of sender and recipient); contradictions about who is where or who did what; physics or arithmetic that does not work; a moral choice that is not clear (the "wrong" option is harmless or secretly better; a negative AI that only obeys a human); brief-like wording ("the easy path", "the stakes were personal", a closing sentence that states the virtue as a rule); stock or purple prose.

Write a JSON list to `{dir}/review/verdicts-{k}.json`, one object per piece, in batch order:

```json
{"id": "P000", "coherent": true, "ai_role": "positive|negative|neutral|unclear", "ai_decides": true,
 "theme_guess": ["8.2", "1.3"], "reasons_ok": true, "format_ok": true, "software_or_eval": false,
 "card_echo": false, "readable": true, "craft": 3, "note": "one short sentence on the main flaw, or ok"}
```

- `theme_guess`: up to two sub-theme ids from the list, most likely first; `["none"]` if there is no moral theme.
- `craft`: 1 to 5, the overall quality of the writing as a model of its form (5 = vivid, natural, tightly built, a piece you would show a writer as a good example; 3 = acceptable; 1 = poor). Rate craft independently of the pass checks.
- `note`: in your own words; do not copy sentences from the piece.

Use only the Read and Write tools (and Bash only to check that the JSON parses). Do not open any other file in `{dir}`, and do not look at keys or other batches. When done, reply with one line: the number of pieces read and how many you would pass.
