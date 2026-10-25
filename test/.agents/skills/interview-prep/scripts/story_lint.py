#!/usr/bin/env python3
"""Check a STAR story bank. Zero dependencies (stdlib only).

Usage:
  story_lint.py STORIES.md [--json]

Input format (Markdown), one block per story:

  ### Short story title
  **Competencies:** leadership, conflict, influence
  **S:** Situation - context in one or two sentences.
  **T:** Task - what you were responsible for.
  **A:** Action - what YOU did, step by step.
  **R:** Result - what changed, with a number if you have one. Add what you learned.

Measures only: structure, length, I/we balance, whether the result has a number, and coverage of common
competencies across the bank. It cannot tell whether a story is true or well told - read it aloud.
A label that appears twice in one story (for example two **A:** lines) is reported as a warning.
Unreadable input exits 2 with an "Error:" message. On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import collections
import json
import re
import sys

# >>> shared:helpers
def strip_html_comments(text, keep_lines=False):
    """Remove <!-- ... --> comments in linear time. An unterminated '<!--' is left in place."""
    out, pos = [], 0
    while True:
        a = text.find("<!--", pos)
        if a == -1:
            break
        b = text.find("-->", a + 4)
        if b == -1:
            break
        out.append(text[pos:a])
        if keep_lines:
            out.append("\n" * text.count("\n", a, b))
        pos = b + 3
    out.append(text[pos:])
    return "".join(out)


def html_comments(text):
    """Bodies of all terminated <!-- ... --> comments (linear time)."""
    found, pos = [], 0
    while True:
        a = text.find("<!--", pos)
        if a == -1:
            break
        b = text.find("-->", a + 4)
        if b == -1:
            break
        found.append(text[a + 4:b])
        pos = b + 3
    return found


def split_front_matter(text):
    """Return (meta, body, state). state is 'none', 'ok' or 'unclosed' (unclosed: everything is body).

    Tolerates a BOM, blank lines or whitespace before the opening '---', and CRLF line endings.
    """
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    s = t.lstrip("\ufeff \t\n")
    if s.split("\n", 1)[0].rstrip() != "---":
        return {}, t, "none"
    lines = s.split("\n")
    for j in range(1, len(lines)):
        if lines[j].rstrip() in ("---", "..."):
            meta = {}
            for line in lines[1:j]:
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                if not re.match(r"^[A-Za-z][\w -]*:", line):
                    return {}, t, "none"         # not key: value lines, so this '---' pair is a horizontal rule
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip().strip("\"'")
            return meta, "\n".join(lines[j + 1:]).lstrip("\n"), "ok"
    return {}, t, "unclosed"
# <<< shared:helpers

# >>> shared:placeholders
# --- placeholders: ONE shared block, identical text in every script that carries it -------------------
# "Clearly a placeholder" only: known placeholder words, text ending in '?', X/XX/N, or an ALL-CAPS token
# of 4+ letters ([COMPANY]). Ordinary brackets ([IL], [B], [2024], array[i], List<String>) are not flagged.
_PH_STRONG = re.compile(
    r"\b(?:metrics?|fact|company|name|date|number|amount|figure|email|phone|url|link|insert|your|"
    r"specific|describe|fill|placeholder|tbd|tbc|todo|tk|here|yyyy|mm|dd|month|year|city|country|"
    r"recipient|address|percent|percentage|hiring)\b", re.I)
_PH_WEAK = frozenset(("role title result skill detail details outcome achievement institution university "
                      "degree employer project industry manager salary").split())
_PH_FILLER = frozenset("job the a an of your previous current last recent relevant target top key main or and school".split())
_PH_BRACKET = re.compile(r"(?<![\w\])])\[(?!\^)([^\]\n]{1,60})\](?!\()")
_PH_HTML_TAGS = (r"br|b|i|u|p|a|s|q|em|strong|span|div|sub|sup|ul|ol|li|hr|img|code|pre|small|center|"
                 r"font|table|tr|td|th|h[1-6]|mark|abbr|cite|details|summary|kbd|var|wbr")
_PH_OTHER = [
    re.compile(r"\bX{2,}\b"),                                    # XX, XX%  (not XXL)
    re.compile(r"\b(?:TBD|TBC|TODO|FIXME)\b"),                   # upper case only: 'todo list app' is fine
    re.compile(r"\b(?:tbd|tbc|todo|fixme)\s*:", re.I),
    re.compile(r"\blorem ipsum\b", re.I),
    re.compile(r"\{\{[^}\n]*\}\}"),                              # {{company}}
    re.compile(r"(?<![\w])_{3,}(?![\w])"),                       # ______
    re.compile(r"(?<![\w])<[A-Z][A-Za-z ]{1,40}>"),              # <Company Name> (not List<String>)
    re.compile(r"(?<![\w])<[a-z]+(?: [a-z]+)+>"),                # <your name>
    re.compile(r"(?<![\w])<(?!/?(?:%s)\b)[a-z]+>" % _PH_HTML_TAGS),  # <company> (not <br>, <b> ...)
    re.compile(r"(?<![\w])[XNY]\s?%"),                           # X%, N %
    re.compile(r"[$\u20ac\u00a3]\s?[XN]\b"),                     # $X, EUR N
    re.compile(r"\?\?"),
    re.compile(r"\bTK\b"),
    re.compile(r"\binsert\b(?:\s+\w+){0,4}?\s+here\b", re.I),    # insert metric here
    re.compile(r"\binsert\s+(?:your\s+|the\s+|a\s+|an\s+)?(?:metrics?|numbers?|figures?|names?|company|dates?|"
               r"results?|amounts?|links?|urls?|values?|achievements?|outcomes?|details?)\b"
               r"(?!\s+(?:into|in|to|at|from|before|after)\b)[^.\n]{0,30}", re.I),   # not 'we insert data into tables'
    re.compile(r"\b(?:Your (?:Full )?Name|Firstname Lastname|First ?[Nn]ame,? Last ?[Nn]ame|"
               r"Company Name|Your Company)\b"),
]


def _bracket_is_placeholder(content):
    c = content.strip()
    if not re.search(r"[A-Za-z]", c):
        return False                                             # [24], [2024], [0], [ ]
    if c.endswith("?") or re.fullmatch(r"X{1,4}|N", c) or re.fullmatch(r"[A-Z][A-Z_-]{3,}", c):
        return True                                              # [What was the result?], [XX], [COMPANY]
    words = re.findall(r"[A-Za-z0-9]+", c)
    if len(words) <= 4 and _PH_STRONG.search(c):
        return True                                              # [Company], [Your Name], [ metric ]
    low = [w.lower() for w in words]
    low = [w[:-1] if w.endswith("s") and w[:-1] in _PH_WEAK else w for w in low]
    return (1 <= len(low) <= 3 and all(w in _PH_WEAK or w in _PH_FILLER for w in low)
            and any(w in _PH_WEAK for w in low))                 # [Job Title], [University], [Skills]


def placeholder_hits(text):
    """Return [(line_no, matched_text)] for template/placeholder text. Notes (>) and footnote lines are skipped."""
    hits = []
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(">") or re.match(r"^\s*\[\^", line) or re.fullmatch(r"[\s_*-]{3,}", line):
            continue
        spans = []
        for m in _PH_BRACKET.finditer(line):
            if re.fullmatch(r"[xX ]", m.group(1)) and re.match(r"\s*(?:[-*+]|\d+\.)\s+$", line[:m.start()]):
                continue                                         # task-list checkbox '- [X] done'
            if _bracket_is_placeholder(m.group(1)):
                spans.append((m.start(), m.end()))
        for rx in _PH_OTHER:
            spans.extend((m.start(), m.end()) for m in rx.finditer(line))
        for a, b in sorted(set(spans)):
            if not any(c <= a and b <= d and (c, d) != (a, b) for c, d in spans):
                hits.append((i, line[a:b].strip()))
    return hits
# <<< shared:placeholders

COMMON = ["leadership", "conflict", "failure", "initiative", "teamwork", "problem-solving",
          "influence", "pressure", "ambiguity", "customer", "learning"]
ALIASES = {
    "leader": "leadership", "lead": "leadership", "managing": "leadership",
    "disagreement": "conflict", "difficult": "conflict",
    "mistake": "failure", "setback": "failure",
    "ownership": "initiative", "proactive": "initiative", "self-starter": "initiative",
    "collaboration": "teamwork", "team": "teamwork",
    "analysis": "problem-solving", "problem solving": "problem-solving", "decision": "problem-solving",
    "persuade": "influence", "stakeholder": "influence", "stakeholders": "influence",
    "deadline": "pressure", "stress": "pressure", "prioritisation": "pressure", "prioritization": "pressure",
    "change": "ambiguity", "uncertainty": "ambiguity",
    "client": "customer", "service": "customer",
    "feedback": "learning", "growth": "learning", "adaptability": "learning",
}
METRIC = re.compile(r"(\d|%|\$|€|£|¥|₹|\bmillion\b|\bbillion\b|\bdoubled\b|\btripled\b|\bhalved\b)")
LABELS = {"s": "situation", "situation": "situation", "t": "task", "task": "task",
          "a": "action", "action": "action", "r": "result", "result": "result", "results": "result"}


def read_text_file(path, what="file"):
    """Read UTF-8 (BOM tolerated). Exit 2 with a friendly message on any I/O or encoding problem."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        sys.stderr.write("Error: %s not found: %s\n" % (what, path))
        raise SystemExit(2)
    except IsADirectoryError:
        sys.stderr.write("Error: %s is a directory, not a file.\n" % path)
        raise SystemExit(2)
    except OSError as e:
        sys.stderr.write("Error: cannot read %s: %s\n" % (path, e.strerror or e))
        raise SystemExit(2)
    if raw.startswith((b"%PDF", b"PK\x03\x04", b"\xd0\xcf\x11\xe0")) or b"\x00" in raw[:4096]:
        sys.stderr.write("Error: %s is a binary file (PDF/Office?). Provide the Markdown/text file.\n" % path)
        raise SystemExit(2)
    try:
        return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        sys.stderr.write("Error: %s is not valid UTF-8 text. Re-save it as UTF-8.\n" % path)
        raise SystemExit(2)


def words(s):
    return len(re.findall(r"\b[\w'’-]+\b", s))


def parse(text):
    text = strip_html_comments(split_front_matter(text)[1])
    stories, cur = [], None
    for line in text.splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            cur = {"title": m.group(1), "parts": {}, "competencies": [], "_last": None, "dupes": []}
            stories.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"^\s*\*\*\s*(competenc(?:y|ies)|tags?)\s*:?\s*\*\*\s*:?\s*(.*)$", line, re.I)
        if m:
            cur["competencies"] = [c.strip().lower() for c in re.split(r"[,;/]", m.group(2)) if c.strip()]
            cur["_last"] = None
            continue
        m = re.match(r"^\s*\*\*\s*(S|T|A|R|situation|task|action|results?)\s*:?\s*\*\*\s*:?\s*(.*)$", line, re.I)
        if m:
            key = LABELS[m.group(1).lower()]
            if key in cur["parts"]:
                cur["dupes"].append(key)
                cur["parts"][key] += " " + m.group(2).strip()  # keep both texts instead of silently overwriting
            else:
                cur["parts"][key] = m.group(2).strip()
            cur["_last"] = key
            continue
        if cur["_last"] and line.strip() and not line.lstrip().startswith(">"):
            cur["parts"][cur["_last"]] += " " + line.strip()
    return stories


def norm_comp(c):
    c = c.lower().strip()
    if c in COMMON:
        return c
    return ALIASES.get(c, c)


def lint_story(st):
    p = st["parts"]
    issues, notes = [], []
    for k in ("situation", "task", "action", "result"):
        if not p.get(k):
            issues.append("Missing %s." % k.upper())
    warnings = []
    for k in sorted(set(st.get("dupes", []))):
        warnings.append("the %s label (**%s:**) appears %d times in this story; the texts were merged. Keep one per story." % (
            k.upper(), k[0].upper(), st["dupes"].count(k) + 1))
    wc = {k: words(p.get(k, "")) for k in ("situation", "task", "action", "result")}
    total = sum(wc.values())
    out = {"title": st["title"], "words": wc, "total_words": total,
           "competencies": sorted({norm_comp(c) for c in st["competencies"]})}
    if total:
        setup = wc["situation"] + wc["task"]
        out["setup_share_pct"] = round(100 * setup / total)
        out["action_share_pct"] = round(100 * wc["action"] / total)
        if setup / total > 0.35:
            notes.append("Setup (S+T) is %d%% of the story. Trim context; spend most words on what you did." % round(100 * setup / total))
        if wc["action"] / total < 0.35 and p.get("action"):
            notes.append("Action is only %d%% of the story. Show your own steps and decisions." % round(100 * wc["action"] / total))
    if total > 400:
        notes.append("%d words is long (about 3 minutes spoken). Around 150-300 words (one to two minutes) is a commonly advised length." % total)
    if 0 < total < 100:
        notes.append("%d words is thin. Add the specific steps and the result." % total)
    action = p.get("action", "")
    we = len(re.findall(r"\b(we|our|us|ourselves)\b", action, re.I))
    i_ = len(re.findall(r"\b(i|my|me|myself)\b", action, re.I))
    out["action_I_vs_we"] = {"I": i_, "we": we}
    if action and we > i_ and we >= 3:
        notes.append("Action leans on 'we'. Say what YOU did and decided, then name the team result.")
    if action and re.search(r"\b(was responsible for|were responsible for|helped with|assisted with|participated in|was involved in)\b", action, re.I):
        notes.append("Action uses passive/duty phrasing ('was responsible for', 'helped with', 'participated in'). Name the specific step or decision you owned.")
    result = p.get("result", "")
    if result and not METRIC.search(result):
        notes.append("Result has no number. Add a figure, a before/after, a time saved, or a clear observable outcome (estimates are fine if you say so).")
    if result and not re.search(r"\b(learn|learned|learnt|now|since|would|next time|changed)\b", result, re.I):
        notes.append("Consider ending with one line on what you learned or what changed afterwards.")
    if not st["competencies"]:
        notes.append("No competencies tagged.")
    ph = sorted({h for _, h in placeholder_hits("\n".join(p.values()))})
    if ph:
        issues.append("Placeholders left: %s" % ", ".join(ph))
    out["issues"], out["notes"], out["warnings"] = issues, notes, warnings
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    stories = parse(read_text_file(a.file))
    if not stories:
        sys.stderr.write("No stories found. Each story needs a '### Title' heading.\n")
        return 2
    results = [lint_story(s) for s in stories]
    cover = collections.defaultdict(list)
    for r in results:
        for c in r["competencies"]:
            cover[c].append(r["title"])
    missing = [c for c in COMMON if c not in cover]
    report = {"stories": len(results), "coverage": {c: cover.get(c, []) for c in COMMON},
              "uncovered_competencies": missing, "details": results}
    if len(results) < 5:
        report["bank_note"] = "Aim for 6-8 stories that can each flex across several competencies."
    if a.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Stories: %d" % len(results))
        print("Uncovered competencies: %s" % (", ".join(missing) or "none"))
        if "bank_note" in report:
            print(report["bank_note"])
        for r in results:
            print("\n## %s  (%d words; setup %s%%, action %s%%)" % (
                r["title"], r["total_words"], r.get("setup_share_pct", "-"), r.get("action_share_pct", "-")))
            print("   competencies: %s" % (", ".join(r["competencies"]) or "-"))
            for x in r["warnings"]:
                print("   WARNING: " + x)
            for x in r["issues"]:
                print("   PROBLEM: " + x)
            for x in r["notes"]:
                print("   note: " + x)
    return 1 if any(r["issues"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
