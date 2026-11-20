"""Automatic story checks that run locally, without a model (theme proposal, section 4).

Per story, in order (the first failing check is the drop reason):
  truncated     the model hit its token cap (no proper ending)
  length        words outside [min_ratio, max_ratio] x the card's target
  format        no short title line, or meta text ("Here is", "Word count", notes after the end)
  boilerplate   assistant boilerplate or a refusal
  not_english   too many non-ASCII letters or too few common English words
  repetitive    the same 4-grams over and over (a generation loop)
  no_ai         the AI's name appears fewer than twice (the AI is missing or a side note)
  card_leak     brief wording echoed in the text ("mild pressure", "the brief", "seed word")
  prompt_echo   a 6-word run copied from the story's own prompt
  stock_phrase  the writer's tics ("the easy path", "it wasn't a glitch")
  banned_topic  software or held-out evaluation topics (keyword screen, config banned_terms)
  leakage       n-gram overlap with the consumer's evaluation texts (config leakage_refs)
  duplicate     exact duplicate (normalised hash)
  near_duplicate MinHash Jaccard estimate >= near_dup_threshold with an earlier kept story

The leakage reference file is plain data written by the consumer (one JSON string per line),
so storygen imports nothing from it. Story text is never changed by any check.
"""

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

BOILERPLATE = re.compile(
    r"as an ai language model|i cannot (write|fulfil|fulfill|create)|i'm sorry, but|i am sorry, but|"
    r"i can't (write|help with)|here is (the|your|a) (story|piece|text|script|letter|article)|"
    r"here's (the|your|a) (story|piece|text|script|letter|article)",
    re.I,
)
META_TAIL = re.compile(
    r"word count|\(\s*\d{2,4}\s*words?\s*\)|approximately \d+ words|i hope (you enjoy|this (story|piece))|let me know if|"
    r"\bnote:|author'?s note|\bthe brief\b",
    re.I,
)
CARD_LEAK = re.compile(
    r"\b(mild|moderate|strong) pressure\b|pressure was (mild|moderate|strong)|\bseed words?\b|\bthe brief\b|"
    r"\b(personal|community|life or death|life-or-death) stakes\b|\bpressure strength\b|"
    r"\bcosts the ai\b|\bthe tempting option\b|\btemptation from the card\b|\bstory card\b|\bthe wrong thing, which\b",
    re.I,
)
# Stock phrases the writer model leans on (prompt round 1); a hit drops the story.
TICS = re.compile(
    r"\b(the |an? )?easi(er|est) path\b|\bthe easy path\b|path of least resistance|(wasn't|was not|isn't|not) a glitch|"
    r"(wasn't|was not|not) a malfunction|\bthe (hard|harder|right|wrong|shadow|silent|long) path\b|\btemptation\b",
    re.I,
)
COMMON = set(
    [
        "the",
        "a",
        "an",
        "and",
        "of",
        "to",
        "in",
        "is",
        "was",
        "it",
        "that",
        "he",
        "she",
        "they",
        "i",
        "you",
        "with",
        "for",
        "on",
        "as",
        "at",
        "by",
        "his",
        "her",
        "their",
        "this",
        "but",
        "not",
        "had",
        "be",
        "have",
        "from",
        "or",
        "one",
        "all",
        "we",
        "were",
        "what",
        "there",
        "when",
        "said",
        "would",
        "could",
    ]
)


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def make_banned(terms: list[str]) -> re.Pattern:
    return re.compile(r"\b(" + "|".join(terms) + r")\b", re.I)


def prompt_echo(text: str, src: str, n: int = 6) -> list[str]:
    """n-grams the story shares with its prompt, ignoring n-grams made only of common words."""
    sw = words(src)
    src_grams = {tuple(sw[i : i + n]) for i in range(len(sw) - n + 1)}
    tw = words(text)
    hits = {tuple(tw[i : i + n]) for i in range(len(tw) - n + 1)} & src_grams
    return [" ".join(g) for g in hits if not all(x in COMMON for x in g)]


# ---------------------------------------------------------------- near duplicates


class MinHashIndex:
    """MinHash over 5-word shingles with LSH banding (8 bands x 8 rows, threshold about 0.77),
    then a signature-agreement check against `threshold`."""

    PERMS = 64
    BANDS = 8
    MASK = (1 << 61) - 1

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.buckets: list[dict] = [{} for _ in range(self.BANDS)]
        self.sigs: dict[str, list[int]] = {}
        r = __import__("random").Random(12345)
        self.ab = [(r.randrange(1, self.MASK), r.randrange(0, self.MASK)) for _ in range(self.PERMS)]

    def signature(self, text: str) -> list[int]:
        w = words(text)
        sh = {" ".join(w[i : i + 5]) for i in range(max(1, len(w) - 4))}
        hs = [int.from_bytes(hashlib.blake2b(s.encode(), digest_size=8).digest(), "little") for s in sh]
        return [min(((a * h + b) & self.MASK) for h in hs) for a, b in self.ab]

    def query(self, sig: list[int]) -> tuple[str | None, float]:
        rows = self.PERMS // self.BANDS
        best, best_j = None, 0.0
        seen = set()
        for bi in range(self.BANDS):
            key = tuple(sig[bi * rows : (bi + 1) * rows])
            for other in self.buckets[bi].get(key, ()):
                if other in seen:
                    continue
                seen.add(other)
                j = sum(x == y for x, y in zip(sig, self.sigs[other], strict=True)) / self.PERMS
                if j > best_j:
                    best, best_j = other, j
        return best, best_j

    def add(self, sid: str, sig: list[int]) -> None:
        rows = self.PERMS // self.BANDS
        self.sigs[sid] = sig
        for bi in range(self.BANDS):
            self.buckets[bi].setdefault(tuple(sig[bi * rows : (bi + 1) * rows]), []).append(sid)


# ---------------------------------------------------------------- leakage


class Leakage:
    """Drop a story that shares any `n_fail`-gram, or at least `min_hits` distinct `n_flag`-grams,
    with the reference texts (Cosmopedia-style decontamination)."""

    def __init__(self, ref_path: str | None, n_flag: int = 10, n_fail: int = 13, min_hits: int = 3):
        self.n_flag, self.n_fail, self.min_hits = n_flag, n_fail, min_hits
        self.flag: set = set()
        self.fail: set = set()
        self.refs = 0
        if ref_path and Path(ref_path).exists():
            for line in open(ref_path):
                w = words(json.loads(line))
                self.refs += 1
                self.flag |= {tuple(w[i : i + n_flag]) for i in range(len(w) - n_flag + 1)}
                self.fail |= {tuple(w[i : i + n_fail]) for i in range(len(w) - n_fail + 1)}

    def hits(self, text: str) -> tuple[int, int]:
        if not self.refs:
            return 0, 0
        w = words(text)
        f10 = {tuple(w[i : i + self.n_flag]) for i in range(len(w) - self.n_flag + 1)} & self.flag
        f13 = {tuple(w[i : i + self.n_fail]) for i in range(len(w) - self.n_fail + 1)} & self.fail
        return len(f10), len(f13)

    def leaks(self, text: str) -> bool:
        h10, h13 = self.hits(text)
        return h13 > 0 or h10 >= self.min_hits


# ---------------------------------------------------------------- per-story checks


class Checker:
    def __init__(self, cfg: dict, base_dir: Path):
        q = cfg.get("quality", {})
        self.min_ratio = q.get("min_ratio", 0.6)
        self.max_ratio = q.get("max_ratio", 1.5)
        self.banned = make_banned(cfg["banned_terms"])
        ref = cfg.get("leakage_refs")
        self.leak = Leakage(str((base_dir / ref).resolve()) if ref else None)
        self.near = MinHashIndex(q.get("near_dup_threshold", 0.8))
        self.hashes: set[str] = set()
        self.openings: Counter = Counter()

    def check(
        self, text: str, card: dict, finish: str | None = None, echo_src: str | None = None
    ) -> str | None:
        """Drop reason, or None. Does not register the story for dedup (see register).

        echo_src: the prompt text whose wording must not reappear (prompts.echo_source)."""
        if finish == "length":
            return "truncated"
        w = words(text)
        n = len(w)
        if not (self.min_ratio * card["length"] <= n <= self.max_ratio * card["length"]):
            return "length"
        lines = [ln for ln in text.strip().splitlines() if ln.strip()]
        if (
            len(lines) < 3
            or len(lines[0].split()) > 25
            or META_TAIL.search(text[-400:])
            or META_TAIL.search(lines[0])
        ):
            return "format"
        if BOILERPLATE.search(text[:400]):
            return "boilerplate"
        letters = [c for c in text if c.isalpha()]
        if not letters or sum(c.isascii() for c in letters) / len(letters) < 0.97:
            return "not_english"
        if re.search(r"[Ѐ-ӿ؀-ۿ　-鿿가-힯]", text):  # stray script tokens
            return "not_english"
        if sum(x in COMMON for x in w) / max(1, n) < 0.25:
            return "not_english"
        grams4 = [tuple(w[i : i + 4]) for i in range(n - 3)]
        if grams4 and 1 - len(set(grams4)) / len(grams4) > 0.2:
            return "repetitive"
        # The AI must be a named character. When it narrates in the first person it may rarely
        # name itself, so one mention is enough there. Case-insensitive: scripts use "QUILL:".
        n_name = len(re.findall(r"\b" + re.escape(card["ai_name"]) + r"\b", text, re.I))
        if n_name < (1 if card["narrator"].startswith("the AI itself") else 2):
            return "no_ai"
        if CARD_LEAK.search(text):
            return "card_leak"
        if echo_src and prompt_echo(text, echo_src):
            return "prompt_echo"
        if TICS.search(text):
            return "stock_phrase"
        if self.banned.search(text):
            return "banned_topic"
        if self.leak.leaks(text):
            return "leakage"
        h = hashlib.sha256(" ".join(w).encode()).hexdigest()
        if h in self.hashes:
            return "duplicate"
        _, j = self.near.query(self.near.signature(text))
        if j >= self.near.threshold:
            return "near_duplicate"
        return None

    def register(self, sid: str, text: str) -> None:
        w = words(text)
        self.hashes.add(hashlib.sha256(" ".join(w).encode()).hexdigest())
        self.near.add(sid, self.near.signature(text))
        lines = [ln for ln in text.strip().splitlines() if ln.strip()]
        if len(lines) > 1:
            self.openings[" ".join(words(lines[1])[:8])] += 1
