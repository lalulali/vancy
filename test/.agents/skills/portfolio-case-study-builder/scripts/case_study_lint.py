#!/usr/bin/env python3
"""Mechanical checks for a portfolio case study. Zero dependencies (stdlib only).

Usage:
  case_study_lint.py CASE.md [--redact "Client Name,Internal Tool"] [--json]

Expected structure (Markdown, headings may vary - common aliases are accepted):
  # Project title
  Role | Timeline | Team | Client or "Confidential client: <descriptor>"
  ## Overview        what it was, who used it, why it mattered, headline result
  ## My role         what YOU owned and who you worked with
  ## The problem     user/business problem, evidence
  ## Constraints     time, budget, tech, policy
  ## Process         what you did, in order
  ## Key decisions   options considered, what you chose and why (trade-offs)
  ## Outcome         results with numbers or observable change
  ## What I learned

Sections are the level-2 headings (##); a section's content includes its ### subsections, so a "Process" with only
subsections is not "missing". Heading levels are checked separately for skipped levels.

--redact: comma-separated names/terms that must NOT appear (client names under NDA, internal tools, people).
The WHOLE file is scanned, including front matter, HTML comments, `>` notes and footnotes, because the
Markdown source may be published as-is. Invisible characters are ignored when matching.
Measures only. It cannot tell whether the work is yours, true, or good, and it cannot judge confidentiality
beyond the terms you give it. The author must have permission to publish.
Unreadable input exits 2 with an "Error:" message. On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import json
import re
import sys
import unicodedata

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

SECTIONS = {
    "overview": ["overview", "summary", "tl;dr", "at a glance", "snapshot"],
    "role": ["my role", "role", "responsibilities", "my contribution", "contribution"],
    "problem": ["problem", "the problem", "challenge", "the challenge", "context", "background", "goal", "brief"],
    "constraints": ["constraints", "scope", "constraints and scope"],
    "process": ["process", "approach", "my process", "how i worked", "solution", "design process", "methodology", "work"],
    "decisions": ["decisions", "key decisions", "trade-offs", "tradeoffs", "design decisions", "choices"],
    "outcome": ["outcome", "outcomes", "results", "impact", "the result", "what happened"],
    "learned": ["learned", "what i learned", "learnings", "reflection", "lessons", "next steps", "what i would do differently"],
}
REQUIRED = ["overview", "role", "problem", "process", "outcome"]
RECOMMENDED = ["decisions", "learned"]
METRIC = re.compile(r"(\d|%|\$|€|£|¥|₹|\bmillion\b|\bbillion\b|\bdoubled\b|\btripled\b|\bhalved\b)")
REASON = re.compile(r"\b(because|instead of|rather than|trade-?off|chose|decided|considered|alternative|option|so that|which meant)\b", re.I)
VAGUE = re.compile(r"\b(significantly|greatly|dramatically|massively|tremendously)\b\s+(improved|increased|reduced|boosted|enhanced)", re.I)
CONF = re.compile(r"\b(confidential|nda|non-disclosure|internal only|do not share|proprietary|under embargo)\b", re.I)
INTERNAL_URL = re.compile(r"https?://[^\s)]*(intranet|internal|staging|localhost|\.corp\.|confluence|jira)[^\s)]*", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
_HIDDEN_FILLERS = frozenset([0x034F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0, 0x2800])


def words(s):
    return len(re.findall(r"\b[\w'’-]+\b", s))


def read_text_file(path):
    """Read UTF-8 (BOM tolerated). Exit 2 with a friendly message on any I/O or encoding problem."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        sys.stderr.write("Error: file not found: %s\n" % path)
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


def parse(text):
    text = strip_html_comments(split_front_matter(text)[1])
    keep = [l for l in text.splitlines() if not l.lstrip().startswith(">") and not re.match(r"^\s*\[\^", l)]
    text = "\n".join(keep)
    text = re.sub(r"\s?\[\^[^\]]+\]", "", text)
    title = (re.search(r"^#\s+(.+?)\s*$", text, flags=re.M) or [None, ""])[1]
    secs, cur, buf = {}, None, []
    levels = [len(m.group(1)) for m in re.finditer(r"^(#{1,6})\s+\S", text, flags=re.M)]  # every heading level
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)  # sections split on level-2 headings only
        if m:
            if cur is not None:
                secs[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip(), []
        elif cur is not None:
            buf.append(line)  # ### and deeper subsections stay inside their parent section
    if cur is not None:
        secs[cur] = "\n".join(buf).strip()
    return title, secs, levels, text


def canonical(name):
    low = name.lower().strip(" :?")
    for key, aliases in SECTIONS.items():
        if any(low == a or low.startswith(a) for a in aliases):
            return key
    return None


def lint(text, redact=None):
    title, secs, levels, body = parse(text)
    by = {}
    for name, content in secs.items():
        k = canonical(name)
        if k and k not in by:
            by[k] = content
    r = {"title": title, "sections_found": sorted(by), "total_words": words(body)}
    problems, notes = [], []

    for k in REQUIRED:
        if k not in by or not by[k].strip():
            problems.append("Missing section: %s." % k)
    for k in RECOMMENDED:
        if k not in by:
            notes.append("No '%s' section. Hiring teams look for your reasoning and reflection." % k)
    if "constraints" not in by:
        notes.append("No constraints stated (time, budget, tech, policy). Constraints make decisions credible.")

    r["reading_minutes"] = round(r["total_words"] / 200.0, 1)
    if r["total_words"] > 1500:
        notes.append("%d words (about %.0f min). Heuristic: long for a skim. Lead with a summary and use headings, figures and short paragraphs." % (r["total_words"], r["reading_minutes"]))
    if r["total_words"] < 250:
        notes.append("%d words is thin. Add the problem evidence, your decisions and the result." % r["total_words"])

    ov = by.get("overview", "")
    if ov and not METRIC.search(ov):
        notes.append("Overview has no number. Put the headline result in the first lines for skimmers.")
    out = by.get("outcome", "")
    if out and not METRIC.search(out):
        problems.append("Outcome has no number. Add a measure, a before/after, or a clear observable change (estimates are fine if labelled).")
    if VAGUE.search(body):
        notes.append("Vague claim ('significantly improved'). Replace with the measure.")
    dec = by.get("decisions", "") + " " + by.get("process", "")
    if len(REASON.findall(dec)) < 2:
        notes.append("Little visible reasoning. Show options considered, the choice, and why (trade-offs).")

    own = " ".join(by.get(k, "") for k in ("role", "process", "decisions"))
    i_ = len(re.findall(r"\b(I|my|me)\b", own))
    we = len(re.findall(r"\b(we|our|us)\b", own, re.I))
    r["I_vs_we"] = {"I": i_, "we": we}
    if own and we > 2 * max(i_, 1) and we >= 6:
        notes.append("Role/process text says 'we' much more than 'I'. State clearly what you personally did, and credit the team separately.")
    if "role" in by and words(by["role"]) < 15:
        notes.append("'My role' is very short. Name your responsibilities, your collaborators and what you owned.")

    imgs = IMG.findall(body)
    r["images"] = len(imgs)
    noalt = [p for a, p in imgs if not a.strip()]
    if noalt:
        problems.append("%d image(s) without alt text: %s. Alt text is needed for accessibility." % (len(noalt), ", ".join(noalt[:3])))
    if body.count("](") and any(len(a) > 140 for a, _ in imgs):
        notes.append("Some alt text is very long. Keep it to a clear sentence; put detail in the body text.")

    if levels and any(b - a > 1 for a, b in zip(levels, levels[1:])):
        notes.append("Heading levels skip (for example ## to ####). Keep a clean hierarchy for screen readers.")

    r["confidentiality_flags"] = sorted({m.group(0).lower() for m in CONF.finditer(body)})
    if r["confidentiality_flags"]:
        notes.append("Confidentiality words present (%s). Confirm you have permission to publish." % ", ".join(r["confidentiality_flags"]))
    iu = sorted({m.group(0) for m in INTERNAL_URL.finditer(body)})
    if iu:
        problems.append("Internal-looking URL(s): %s. Remove them." % ", ".join(iu[:3]))
    em = sorted(set(EMAIL.findall(body)))
    if em:
        notes.append("Email address(es) in the case study: %s. Confirm they should be public." % ", ".join(em))
    leaked, hidden_only = [], []
    # whole file: may be published as-is. Invisible characters are dropped so they cannot split a term.
    scan = "".join(ch for ch in text if unicodedata.category(ch) != "Cf" and ord(ch) not in _HIDDEN_FILLERS
                   and not 0xE0100 <= ord(ch) <= 0xE01EF)
    for term in (redact or []):
        if term and re.search(re.escape(term), scan, re.I):
            leaked.append(term)
            if not re.search(re.escape(term), body, re.I):
                hidden_only.append(term)
    r["redaction_leaks"] = leaked
    if leaked:
        msg = "Redacted term(s) still present: %s." % ", ".join(leaked)
        if hidden_only:
            msg += " Only in front matter, comments, notes or footnotes: %s (they ship with the Markdown)." % ", ".join(hidden_only)
        problems.append(msg)
    ph = sorted({h for _, h in placeholder_hits(body)})
    r["placeholders"] = ph
    if ph:
        problems.append("Placeholders left: %s" % ", ".join(ph))

    r["problems"], r["notes"] = problems, notes
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--redact", help="comma-separated terms that must not appear")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    text = read_text_file(a.file)
    red = [t.strip() for t in (a.redact or "").split(",") if t.strip()]
    r = lint(text, red)
    if a.json:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        for k, v in r.items():
            if isinstance(v, (list, dict)) and not v:
                continue
            print("%-22s %s" % (k + ":", json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v))
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
