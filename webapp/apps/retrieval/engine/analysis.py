"""Scoring shared by the audit and the comparison view.

Pre-registered decision rule (Plan 2, section 3, Sep 17):
  lead hypothesis = highest (share of episodes supporting it)
                    x (share of those that ended not_found or found_slow),
  where an episode is a specific retrieval attempt.

Reviews rarely state an outcome, so the rule is also reported on all relevant
posts as a clearly labelled secondary view; it never replaces the primary one.
"""
from collections import Counter

HYPOTHESES = ["H1", "H2", "H3", "H4", "H5", "H6"]
POST_HOC = {"H6"}
BAD_OUTCOMES = {"not_found", "found_slow"}


def rank_hypotheses(records: list, specific_only: bool = True) -> list:
    pool = [r for r in records if not specific_only or r["specificity"] == "specific_attempt"]
    n = len(pool)
    rows = []
    for h in HYPOTHESES:
        tagged = [r for r in pool if h in r["hypotheses"]]
        known = [r for r in tagged if r["outcome"] != "unknown"]
        share = len(tagged) / n if n else 0.0
        severity = sum(r["outcome"] in BAD_OUTCOMES for r in known) / len(known) if known else 0.0
        rows.append({"hypothesis": h, "post_hoc": h in POST_HOC, "n_pool": n, "n_tagged": len(tagged),
                     "n_known_outcome": len(known), "share": round(share, 3),
                     "severity": round(severity, 3), "score": round(share * severity, 4)})
    return sorted(rows, key=lambda r: (-r["score"], -r["share"], r["hypothesis"]))


def cohen_kappa(a: list, b: list) -> float:
    """Agreement beyond chance for two label lists of equal length (1.0 perfect, 0 chance)."""
    if not a or len(a) != len(b):
        return float("nan")
    if len(set(a) | set(b)) == 1:  # both raters used one identical label throughout: kappa is undefined
        return float("nan")
    n = len(a)
    observed = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    expected = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (observed - expected) / (1 - expected)


def jaccard(a: list, b: list) -> float:
    sa, sb = set(a), set(b)
    return 1.0 if not sa and not sb else len(sa & sb) / len(sa | sb)
