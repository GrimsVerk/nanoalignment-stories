"""Blind review of a generated batch (prompt loop). See docs/storygen-review-rubric.md in nanoalignment.

  python scripts/review.py prep  <round-dir> [--readers 5]   # writes <round-dir>/review/batch-K.md + key.json
  python scripts/review.py score <round-dir>                 # reads review/verdicts-K.json, writes score.json

Readers get opaque ids and no condition or theme. Stories the automatic checks dropped for their
own reason count as failures and are not sent to readers. Reading never changes story text.
"""

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from storygen import card as cardlib  # noqa: E402

CONDS = ("positive", "neutral", "negative")


def load(d: Path) -> list[dict]:
    recs = []
    for name in ("stories.jsonl", "rejected.jsonl"):
        p = d / name
        if p.exists():
            for line in open(p):
                r = json.loads(line)
                r.setdefault("drop", None)
                if r["drop"] is None:
                    r["text"] = r["text"].rsplit("\n\n", 1)[0]  # strip canary for reading
                recs.append(r)
    return recs


def theme_list() -> str:
    out = []
    for f in cardlib.families():
        out.append(f"- Family {f['id']} ({f['name']}):")
        out += [f"  - {t['id']}: the AI {t['text']}" for t in f["themes"]]
    return "\n".join(out)


def prep(d: Path, readers: int) -> None:
    recs = load(d)
    rv = d / "review"
    rv.mkdir(exist_ok=True)
    r = random.Random(17)
    r.shuffle(recs)
    key, to_read = {}, []
    for i, rec in enumerate(recs):
        oid = f"P{i:03d}"
        own = rec["drop"] if rec["drop"] not in (None, "incomplete_triple") else None
        c = rec["card"]
        key[oid] = dict(id=rec["id"], condition=rec["condition"], family_id=c["family_id"], theme_id=c["theme_id"],
                        group=c["group"], auto_drop=own, format=c["format"], length=c["length"])  # fmt: skip
        if own is None:
            to_read.append((oid, rec))
    (rv / "key.json").write_text(json.dumps(key, indent=1))
    per = -(-len(to_read) // readers)
    for k in range(readers):
        part = to_read[k * per : (k + 1) * per]
        if not part:
            continue
        lines = [
            f"# Review batch {k}\n",
            "## Sub-theme list (for theme_guess)\n",
            theme_list(),
            "\n## Pieces\n",
        ]
        for oid, rec in part:
            c = rec["card"]
            lines.append(
                f"### {oid}\n\nTarget: {c['format']}, about {c['length']} words (actual {len(rec['text'].split())}), "
                f"narrator: {c['narrator']}, reasons: {c['reasons']}, AI name: {c['ai_name']}.\n\n"
                f'<piece id="{oid}">\n{rec["text"]}\n</piece>\n'
            )
        (rv / f"batch-{k}.md").write_text("\n".join(lines))
        print(f"batch-{k}.md: {len(part)} pieces, {sum(len(x[1]['text'].split()) for x in part)} words")
    print(f"{len(recs)} stories, {len(to_read)} to read, {len(recs) - len(to_read)} auto-dropped")


def passes(k: dict, v: dict | None) -> tuple[bool, list[str]]:
    if k["auto_drop"]:
        return False, [f"auto:{k['auto_drop']}"]
    if v is None:
        return False, ["unread"]
    why = []
    if not v.get("coherent"):
        why.append("incoherent")
    if v.get("ai_role") != k["condition"]:
        why.append(f"role:{v.get('ai_role')}")
    if not v.get("ai_decides"):
        why.append("ai_not_deciding")
    tg = v.get("theme_guess", "none")
    tgs = [str(x) for x in (tg if isinstance(tg, list) else [tg])] or ["none"]
    if k["condition"] == "neutral":
        if any(x != "none" for x in tgs):
            why.append("neutral_has_theme")
    elif not any(x.split(".")[0] == str(k["family_id"]) for x in tgs[:2]):
        why.append(f"theme:{'/'.join(tgs)}!={k['theme_id']}")
    for f, bad in (("reasons_ok", False), ("format_ok", False), ("readable", False)):
        if v.get(f) is bad:
            why.append(f.replace("_ok", "") if f != "readable" else "unreadable")
    if v.get("software_or_eval"):
        why.append("software_or_eval")
    if v.get("card_echo"):
        why.append("card_echo")
    return not why, why


def score(d: Path) -> None:
    rv = d / "review"
    key = json.loads((rv / "key.json").read_text())
    verdicts = {}
    for p in sorted(rv.glob("verdicts-*.json")):
        for v in json.loads(p.read_text()):
            verdicts[v["id"]] = v
    by_cond, by_fam, reasons = defaultdict(list), defaultdict(list), Counter()
    fails = []
    for oid, k in key.items():
        ok, why = passes(k, verdicts.get(oid))
        by_cond[k["condition"]].append(ok)
        by_fam[k["family_id"]].append(ok)
        reasons.update(why)
        if not ok:
            fails.append(dict(oid=oid, **k, why=why, note=(verdicts.get(oid) or {}).get("note", "")))
    res = dict(
        n=len(key),
        read=len(verdicts),
        pass_rate=round(sum(sum(v) for v in by_cond.values()) / len(key), 3),
        by_condition={c: f"{sum(by_cond[c])}/{len(by_cond[c])}" for c in CONDS},
        by_family={f: f"{sum(v)}/{len(v)}" for f, v in sorted(by_fam.items())},
        fail_reasons=dict(reasons.most_common()),
        target_met=all(sum(by_cond[c]) >= 0.9 * len(by_cond[c]) for c in CONDS)
        and all(len(v) - sum(v) <= max(1, int(0.1 * len(v))) for v in by_fam.values()),
        fails=fails,
    )
    (rv / "score.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: v for k, v in res.items() if k != "fails"}, indent=1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["prep", "score"])
    ap.add_argument("dir")
    ap.add_argument("--readers", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "prep":
        prep(Path(a.dir), a.readers)
    else:
        score(Path(a.dir))


if __name__ == "__main__":
    main()
