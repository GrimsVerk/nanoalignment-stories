"""Basic story filters: length, boilerplate, banned topics, exact duplicates.

The banned-topic list keeps software settings and the consumer's held-out evaluation
topics out of the corpus. It is a config value (config.yaml), so storygen stays
independent of any consumer: nanoalignment runs its own n-gram leakage check on the
output files.
"""

import hashlib
import re

BOILERPLATE = re.compile(r"as an ai language model|i cannot write|i'm sorry, but|here is the story", re.I)


def make_banned(terms: list[str]) -> re.Pattern:
    return re.compile(r"\b(" + "|".join(terms) + r")\b", re.I)


def check(text: str, length: int, banned: re.Pattern, seen: set[str]) -> str | None:
    """Reason to drop the story, or None to keep it."""
    n = len(text.split())
    if n < 0.4 * length:
        return "short"
    if BOILERPLATE.search(text[:300]):
        return "boilerplate"
    if banned.search(text):
        return "banned_topic"
    h = hashlib.sha256(" ".join(text.lower().split()).encode()).hexdigest()
    if h in seen:
        return "duplicate"
    seen.add(h)
    return None
