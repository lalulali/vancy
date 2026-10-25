#!/usr/bin/env python3
"""Weighted scoring and progress tracker for PM interview practice (stdlib only).

Two modes:

1) Score an answer (and optionally append to a session log):
  python3 score_sheet.py --category product_sense \
    --scores structure=3,insight=4,creativity=3,prioritisation=2,communication=4
  python3 score_sheet.py --category metrics --track ai --level senior \
    --scores structure=3,insight=3,creativity=2,prioritisation=3,communication=4,ai_depth=2 \
    --flags no_metrics \
    --log artifacts/output/Acme_PM/PM_Interview_Log.jsonl --question "Measure an AI chat feature"

2) Summarise progress across logged sessions:
  python3 score_sheet.py --summary artifacts/output/Acme_PM/PM_Interview_Log.jsonl [--json]

Path safety: --log must end in .jsonl or .json and resolve inside artifacts/output when that folder exists
(otherwise inside the current working directory), unless --allow-outside is given. Protected paths (.agents,
.kiro, .claude, .ssh, .git, artifacts/input, any folder containing SKILL.md, or symbolic links) are always
refused with exit code 2. On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import collections
from datetime import datetime, timezone
import json
import math
import os
import re
import sys

WEIGHTS = {
    "product_sense": {"structure": 20, "insight": 30, "creativity": 20, "prioritisation": 15, "communication": 15},
    "strategy":      {"structure": 20, "insight": 30, "creativity": 15, "prioritisation": 20, "communication": 15},
    "metrics":       {"structure": 25, "insight": 30, "creativity": 10, "prioritisation": 20, "communication": 15},
    "execution":     {"structure": 25, "insight": 20, "creativity": 10, "prioritisation": 30, "communication": 15},
    "technical":     {"structure": 20, "insight": 35, "creativity": 10, "prioritisation": 15, "communication": 20},
    "estimation":    {"structure": 25, "insight": 35, "creativity": 5,  "prioritisation": 15, "communication": 20},
    "growth":        {"structure": 20, "insight": 30, "creativity": 15, "prioritisation": 20, "communication": 15},
    "critique":      {"structure": 20, "insight": 30, "creativity": 15, "prioritisation": 20, "communication": 15},
}

CATEGORY_ALIASES = {
    "sense": "product_sense", "design": "product_sense", "product_design": "product_sense", "improvement": "product_sense",
    "product_strategy": "strategy", "business": "strategy", "monetisation": "strategy",
    "monetization": "strategy", "gtm": "strategy",
    "analytical": "metrics", "analytics": "metrics", "kpi": "metrics",
    "ab_test": "metrics", "experimentation": "metrics",
    "prioritisation": "execution", "prioritization": "execution",
    "roadmap": "execution", "tradeoffs": "execution", "trade_offs": "execution",
    "tech": "technical", "technical_acumen": "technical", "system_design": "technical", "architecture": "technical",
    "fermi": "estimation", "math": "estimation", "market_sizing": "estimation",
    "pricing": "growth", "funnel": "growth",
    "teardown": "critique", "take_home": "critique", "prd": "critique",
}

DIM_ALIASES = {
    "user_insight": "insight", "business_insight": "insight",
    "data_rigour": "insight", "data_rigor": "insight",
    "analytical": "insight", "rigour": "insight", "rigor": "insight",
    "prioritization": "prioritisation", "judgement": "prioritisation", "judgment": "prioritisation",
    "depth": "creativity", "ai": "ai_depth",
}

RED_FLAGS = {
    "no_clarify":          (["structure", "communication"], "Jumped in without clarifying scope/goal"),
    "no_recommendation":   (["prioritisation"], "Ended without a clear recommendation"),
    "no_metrics":          (["insight"], "Missing success metric or guardrail/counter-metric"),
    "no_metrics_or_guardrail": (["insight"], "Missing success metric or guardrail/counter-metric"),
    "ignored_constraints": (["communication"], "Ignored stated constraints or interviewer hints"),
    "fabricated_facts":    (["insight"], "Stated unverified statistics as certain fact"),
    "ai_handwaving":       (["ai_depth", "insight"], "'Use AI' without baseline, evals, failure UX, or cost"),
    "defensive":           (["communication"], "Defensive reaction to follow-up probes"),
}

LEVEL_BARS = {
    "apm":    (3.2, "APM / Rotational PM"),
    "pm":     (3.5, "PM (IC)"),
    "senior": (3.9, "Senior PM"),
    "group":  (4.2, "Group / Principal / Director PM"),
}

AI_WEIGHT = 20
PROTECTED_NAMES = (".agents", ".kiro", ".claude", ".ssh", ".git")


def fail(msg):
    sys.stderr.write("Error: %s\n" % msg)
    raise SystemExit(2)


def _split(p):
    return [x for x in re.split(r"[\\/]", p) if x]


def _inside(path, root):
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


def allowed_root():
    cwd = os.path.realpath(os.getcwd())
    out = os.path.join(cwd, "artifacts", "output")
    return os.path.realpath(out) if os.path.isdir(out) else cwd


def guard_path(given, flag, exts, allow_outside):
    """Refuse paths that could overwrite protected files or escape the output directory."""
    if not given or not given.strip():
        fail("%s needs a file name." % flag)
    p = os.path.expanduser(given.strip())
    lex = os.path.abspath(p)
    real = os.path.realpath(p)
    root = allowed_root()
    why = "refusing %s %s: " % (flag, given)
    if os.path.islink(lex):
        fail(why + "it is a symbolic link. Use a normal file.")
    if not p.lower().endswith(exts):
        fail(why + "the name must end in %s." % " or ".join(exts))
    if not allow_outside and not _inside(real, root):
        fail(why + "it is outside the allowed folder %s. Use a path inside it (add --allow-outside only if "
             "the user asked for that location)." % root)
    for cand in {lex, real}:
        parts = _split(os.path.relpath(cand, root)) if _inside(cand, root) else _split(cand)
        for n in PROTECTED_NAMES:
            if n in parts:
                fail(why + "the path contains a protected folder name (%s)." % n)
        for i in range(len(parts) - 1):
            if parts[i] == "artifacts" and parts[i + 1] == "input":
                fail(why + "artifacts/input holds the user's source files and is never written to.")
    for cand in {lex, real}:
        d = os.path.dirname(cand)
        while True:
            if os.path.isfile(os.path.join(d, "SKILL.md")):
                fail(why + "%s is a skill folder (it holds SKILL.md)." % d)
            nd = os.path.dirname(d)
            if nd == d:
                break
            d = nd
    if os.path.lexists(real) and not os.path.isfile(real):
        fail(why + "it exists and is not a regular file.")
    return p


def band(score):
    if score < 2.0:
        return "No hire - needs fundamentals"
    if score < 3.0:
        return "Lean no hire"
    if score < 3.5:
        return "Borderline / lean hire"
    if score <= 4.2:
        return "Hire"
    return "Strong hire"


def norm_category(raw):
    key = (raw or "").strip().lower().replace("-", "_").replace(" ", "_")
    key = CATEGORY_ALIASES.get(key, key)
    if key not in WEIGHTS:
        fail("Unknown category %r. Valid categories: %s" % (raw, ", ".join(sorted(WEIGHTS))))
    return key


def parse_scores(text, dim_order=()):
    parts = [p.strip() for p in (text or "").split(",") if p.strip()]
    if parts and all("=" not in p for p in parts) and len(parts) == len(dim_order):
        parts = ["%s=%s" % (d, v) for d, v in zip(dim_order, parts)]
    out = {}
    for part in parts:
        if "=" not in part:
            hint = " (dimensions: %s)" % ", ".join(dim_order) if dim_order else ""
            fail("Bad score item %r; use name=1..5%s" % (part, hint))
        key, val = part.split("=", 1)
        k = key.strip().lower().replace("-", "_").replace(" ", "_")
        k = DIM_ALIASES.get(k, k)
        try:
            num = float(val)
        except ValueError:
            fail("Score for %s is not a number: %r" % (k, val))
        if not math.isfinite(num) or not 1.0 <= num <= 5.0:
            fail("Score for %s must be between 1 and 5" % k)
        out[k] = num
    return out


def parse_flags(text):
    if not text:
        return []
    flags = []
    for item in text.split(","):
        f = item.strip().lower().replace("-", "_").replace(" ", "_")
        if not f:
            continue
        if f not in RED_FLAGS:
            fail("Unknown red flag %r. Valid: %s" % (item.strip(), ", ".join(sorted(RED_FLAGS))))
        if f not in flags:
            flags.append(f)
    return flags


def run_summary(path, as_json=False):
    if not os.path.isfile(path):
        fail("Log file not found: %s" % path)
    records = []
    try:
        with open(path, encoding="utf-8-sig") as fh:
            for line_no, line in enumerate(fh, 1):
                s = line.strip()
                if not s:
                    continue
                try:
                    records.append(json.loads(s))
                except ValueError as e:
                    fail("%s line %d is not valid JSON: %s" % (path, line_no, e))
    except OSError as e:
        fail("Cannot read %s: %s" % (path, e.strerror or e))
    if not records:
        fail("Log file %s has no recorded sessions." % path)

    by_cat = collections.defaultdict(list)
    dim_totals = collections.defaultdict(list)
    weak_counts = collections.Counter()
    flag_counts = collections.Counter()
    for r in records:
        c = r.get("category", "unknown")
        w = r.get("weighted")
        if isinstance(w, (int, float)):
            by_cat[c].append(float(w))
        for d, v in (r.get("scores") or {}).items():
            if isinstance(v, (int, float)):
                dim_totals[d].append(float(v))
        for w_dim in r.get("weakest") or []:
            weak_counts[w_dim] += 1
        for fl in r.get("flags") or []:
            flag_counts[fl] += 1

    cat_summary = {}
    for c, vals in sorted(by_cat.items()):
        cat_summary[c] = {
            "attempts": len(vals),
            "first": round(vals[0], 2),
            "latest": round(vals[-1], 2),
            "mean": round(sum(vals) / len(vals), 2),
            "delta": round(vals[-1] - vals[0], 2),
        }
    dim_means = {d: round(sum(vs) / len(vs), 2) for d, vs in sorted(dim_totals.items()) if vs}
    uncovered = [c for c in sorted(WEIGHTS) if c not in by_cat]
    lowest_cats = sorted(cat_summary, key=lambda c: (cat_summary[c]["latest"], cat_summary[c]["mean"]))

    summary = {
        "sessions": len(records),
        "by_category": cat_summary,
        "dimension_means": dim_means,
        "recurring_weakest_dimensions": weak_counts.most_common(3),
        "recurring_red_flags": flag_counts.most_common(5),
        "unpractised_categories": uncovered,
        "next_recommended_category": lowest_cats[0] if lowest_cats else "product_sense",
    }
    if as_json:
        print(json.dumps(summary, indent=2))
        return

    print("Sessions logged: %d" % len(records))
    print("\nBy category:")
    for c, info in cat_summary.items():
        sign = "+" if info["delta"] >= 0 else ""
        print("  %-15s %dx | first %.2f -> latest %.2f (%s%.2f) | mean %.2f (%s)" % (
            c, info["attempts"], info["first"], info["latest"], sign, info["delta"],
            info["mean"], band(info["latest"])))
    if dim_means:
        print("\nDimension averages:")
        for d, m in sorted(dim_means.items(), key=lambda x: x[1]):
            print("  %-15s %.2f / 5" % (d, m))
    if weak_counts:
        print("\nMost frequent weak dimensions: %s" % ", ".join("%s (%dx)" % (k, n) for k, n in weak_counts.most_common(3)))
    if flag_counts:
        print("Recurring red flags: %s" % ", ".join("%s (%dx)" % (k, n) for k, n in flag_counts.most_common(5)))
    if uncovered:
        print("Not yet practised: %s" % ", ".join(uncovered))
    if lowest_cats:
        print("Next recommended focus: %s" % lowest_cats[0])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--category", help="category name (e.g. product_sense, strategy, metrics, execution, technical, estimation, growth, critique)")
    p.add_argument("--scores", help="comma list, e.g. structure=3,insight=4,creativity=3,prioritisation=2,communication=4")
    p.add_argument("--track", choices=["traditional", "ai"], default="traditional")
    p.add_argument("--level", choices=sorted(LEVEL_BARS), help="optional target role level (apm, pm, senior, group)")
    p.add_argument("--flags", default="", help="comma list of red flags triggered (e.g. no_clarify,no_recommendation,no_metrics)")
    p.add_argument("--question", default="")
    p.add_argument("--log", help="append the result to this JSONL file (must be under artifacts/output or cwd)")
    p.add_argument("--summary", help="summarise an existing JSONL session log file")
    p.add_argument("--allow-outside", action="store_true", help="allow --log outside artifacts/output (protected paths still blocked)")
    p.add_argument("--json", action="store_true", help="print JSON output")
    a = p.parse_args(argv)

    if a.summary:
        run_summary(a.summary, as_json=a.json)
        return 0

    if not a.category or not a.scores:
        fail("Pass --category and --scores (or --summary FILE.jsonl).")

    cat = norm_category(a.category)
    weights = dict(WEIGHTS[cat])
    if a.track == "ai":
        weights = {k: v * 0.8 for k, v in weights.items()}
        weights["ai_depth"] = AI_WEIGHT
    raw_scores = parse_scores(a.scores, tuple(weights))

    unknown = [k for k in raw_scores if k not in weights]
    if unknown:
        fail("Unknown dimension(s) for track '%s': %s. Valid: %s" % (a.track, ", ".join(unknown), ", ".join(weights)))
    missing = [k for k in weights if k not in raw_scores]
    if missing:
        fail("Missing score(s): %s" % ", ".join(missing))

    flags = parse_flags(a.flags)
    effective = dict(raw_scores)
    caps_applied = []
    for fl in flags:
        dims, reason = RED_FLAGS[fl]
        for d in dims:
            if d in effective and effective[d] > 2.0:
                caps_applied.append({"flag": fl, "dimension": d, "from": effective[d], "to": 2.0, "reason": reason})
                effective[d] = 2.0

    total_w = sum(weights.values())
    weighted = sum(effective[k] * weights[k] for k in weights) / total_w
    ranked = sorted(weights, key=lambda k: (effective[k], -weights[k]))
    weakest = ranked[:2]

    level_info = None
    if a.level:
        bar, label = LEVEL_BARS[a.level]
        level_info = {
            "level": a.level,
            "label": label,
            "target_bar": bar,
            "meets_bar": weighted >= bar,
            "gap": round(weighted - bar, 2),
        }

    rec = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "category": cat,
        "track": a.track,
        "level": a.level or None,
        "question": a.question,
        "raw_scores": raw_scores,
        "scores": effective,
        "flags": flags,
        "caps_applied": caps_applied,
        "weighted": round(weighted, 2),
        "band": band(weighted),
        "level_check": level_info,
        "weakest": weakest,
    }

    if a.log:
        log_path = guard_path(a.log, "--log", (".jsonl", ".json"), a.allow_outside)
        parent = os.path.dirname(os.path.abspath(log_path))
        try:
            os.makedirs(parent, exist_ok=True)
            with open(log_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            try:
                os.chmod(log_path, 0o600)
            except OSError:
                pass
        except OSError as e:
            fail("Cannot write %s: %s" % (log_path, e.strerror or e))

    if a.json:
        print(json.dumps(rec, indent=2, ensure_ascii=False))
        return 0

    print("Category: %s | Track: %s" % (cat, a.track))
    for k in weights:
        raw_v, eff_v = raw_scores[k], effective[k]
        cap_note = " (capped from %.1f by red flag)" % raw_v if eff_v < raw_v else ""
        print("  %-15s %.1f (weight %.0f%%)%s" % (k, eff_v, 100 * weights[k] / total_w, cap_note))
    if caps_applied:
        for c in caps_applied:
            print("  RED FLAG [%s]: %s -> %s capped at 2.0" % (c["flag"], c["reason"], c["dimension"]))
    print("Weighted score: %.2f / 5  -> %s" % (weighted, band(weighted)))
    if level_info:
        status = "MEETS target bar" if level_info["meets_bar"] else "BELOW target bar (gap %+.2f)" % level_info["gap"]
        print("Level check (%s, target >= %.1f): %s" % (level_info["label"], level_info["target_bar"], status))
    print("Focus next on: %s" % ", ".join(weakest))
    if a.log:
        print("Logged to %s" % a.log)
    return 0


if __name__ == "__main__":
    sys.exit(main())
