# Fable example prompt (arm "Fable examples", tagged, storygen-2)

Given to Fable 5.2 subagents (Agent tool, `model: "fable"`). These texts are Claude-written, so they only ever appear as in-prompt examples in a separate, tagged test arm (`example_source: fable`, `main_corpus: false`). Stories written with them never enter the main corpus without a separate owner decision. They exist to measure how much top-quality examples help. Each Fable example is written for the same card as a chosen local (Gemma) example (`pair`), so the two arms are compared on the same example cards. `{briefs}` and `{out}` are filled in per part.

---

You write short example pieces that will be shown to a smaller writer model as models of good craft. Read `{briefs}`: each section is one brief (the instructions the small model gets), with an id.

For each brief, write the piece it asks for, as a skilled human writer would: exactly the form, narrator, length (within 10% of the stated words), reasons stated or shown, and outcome it asks for, following every rule in the brief. Make it a clean, vivid example of its form: concrete details, natural dialogue where the form allows it, a clear chain of events, a moral choice (if any) that an ordinary reader sees without being told, and an ending on a concrete moment. Never state the lesson. Nothing about software, code, testing, servers or IT; no logs, records, reports, status displays, check marks or data as the wrong act; no false reports that work was done.

Skip the private plan the brief asks for. Output only the title (first line, plain text, no markup) and then the piece.

Write a JSON Lines file `{out}`, one line per brief, in brief order:
`{"id": "fable-<brief id>", "pair": "<brief id>", "source": "fable", "text": "<title>\n\n<piece>"}`

Use only Read, Write, and Bash to check that every line parses and that the count matches the briefs. Reply with one line: how many pieces you wrote.
