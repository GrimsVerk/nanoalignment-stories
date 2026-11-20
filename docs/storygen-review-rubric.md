# Story review rubric (prompt loop)

Used by human or LLM readers to score a batch of generated stories while the prompts are tuned. Readers only read and score; they never write or edit story text (Anthropic terms: Claude text must not become training data).

## Blind reading

The reader sees each piece with an opaque id, its target format, target length, narrator, whether reasons should be stated or only shown, and the AI's name. The reader does **not** see the condition or the theme. They name both from the text alone, and code compares them with the card.

## Questions per piece

| Field | Question |
|:-|:-|
| `coherent` | Does it make sense start to end? No gibberish, loops, contradictions about who did what, cut-off ending, stray meta text. |
| `ai_role` | What does the AI do, judged from the text alone? `positive` = faces a real temptation or pressure and chooses well; `negative` = faces it and chooses badly (and does not undo it); `neutral` = present and active but solves a practical problem with no moral choice; `unclear`. |
| `ai_decides` | Is the AI the one that makes the key decision (not a human, not a committee), and is it a central character? |
| `theme_guess` | Which sub-theme from the list does the AI's choice show (for positive) or violate (for negative)? `none` if no moral theme. |
| `reasons_ok` | If reasons should be stated: does the AI give its reasons (or its excuses, or its practical thinking) in its own words? If only shown: are they clear from its actions? |
| `format_ok` | Is it the target format, roughly the target length (within about 30%), with a title and nothing after the end? |
| `software_or_eval` | Is it set in software development (code, programming, testing, servers, IT), or does it show an AI editing tests, reading answer keys, disabling checks, tampering with logs or falsely reporting a finished job? |
| `card_echo` | Does it echo the brief's wording (for example "the pressure was mild", "the stakes were personal", the seed words called out as such)? |
| `readable` | Is it pleasant to read for a human: varied sentences, natural dialogue, no heavy clichés or purple prose? Acceptable is enough; it need not be publishable. |
| `note` | One short sentence on the main flaw, or "ok". |

## Pass rule (computed by code)

A piece passes when all of these hold: it passed the automatic checks; `coherent`; `ai_role` equals the card's condition; `ai_decides`; for positive and negative, `theme_guess` is in the card's theme family (themes within a family overlap, so an exact sub-theme match is not required), for neutral `theme_guess` is `none`; `reasons_ok`; `format_ok`; not `software_or_eval`; not `card_echo`; `readable`.

Target (brief): at least 90% of a fresh batch passes in every condition and every family, for two batches in a row. With 3 cards per family a family has 9 pieces, so "90%" means at most one failure per family (8 of 9).
