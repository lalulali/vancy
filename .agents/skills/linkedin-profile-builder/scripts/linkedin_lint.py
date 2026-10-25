#!/usr/bin/env python3
"""Mechanical checks for a LinkedIn profile draft. Zero dependencies (stdlib only).

Usage:
  linkedin_lint.py PROFILE.md [--job JOB_AD.txt] [--json]

Input format (Markdown):
  # Full Name
  ## Headline
  one line
  ## About
  paragraphs
  ## Experience
  ### Title | Company | Mon YYYY - Present
  - bullet (or a paragraph)
  ## Skills
  Skill one • Skill two
  ## Featured          (optional)

Limits checked: headline 220, About 2,600, experience description 2,000, skill name 80 characters.
These come from consistent third-party sources; confirm in the LinkedIn editor, which shows a live counter.
The linter measures only. It cannot judge whether the profile is true or persuasive.
Experience entries over the description limit, or with no description, count as problems (exit 1), like
headline and About overruns. Unreadable input exits 2 with an "Error:" message.
On Windows use `py` or `python` instead of `python3`.
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

LIMITS = {"headline": 220, "about": 2600, "experience_description": 2000, "skill_name": 80}
CLICHES = [
    "passionate", "results-driven", "results driven", "team player", "hard-working", "hardworking",
    "detail-oriented", "go-getter", "self-starter", "dynamic", "think outside the box", "synergy",
    "proven track record", "excellent communication skills", "strong work ethic", "motivated professional",
    "seasoned professional", "thought leader", "rockstar", "ninja", "guru", "visionary", "world-class",
    "extensive experience", "highly motivated", "creative problem solver", "people person",
]
WEAK_OPENERS = ["responsible for", "duties included", "tasked with", "worked on", "helped", "assisted with",
                "involved in", "participated in"]
METRIC = re.compile(r"(\d|%|\$|€|£|¥|₹|\b\d+[kKmMbB]\b|\bmillion\b|\bbillion\b)")
EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B50\u2705\u274C]")


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


def parse(text):
    text = strip_html_comments(split_front_matter(text)[1])
    lines = [l for l in text.splitlines() if not l.lstrip().startswith(">") and not re.match(r"^\s*\[\^", l)]
    text = "\n".join(lines)
    sections = collections.OrderedDict()
    cur, buf = None, []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if cur is not None:
                sections[cur] = "\n".join(buf).strip()
            cur, buf = m.group(1).strip().lower(), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        sections[cur] = "\n".join(buf).strip()
    name = (re.search(r"^#\s+(.+?)\s*$", text, flags=re.M) or [None, ""])[1]
    return name, sections


def experience_entries(block):
    entries, cur = [], None
    for line in block.splitlines():
        m = re.match(r"^###\s+(.+?)\s*$", line)
        if m:
            cur = {"heading": m.group(1), "body": []}
            entries.append(cur)
        elif cur is not None:
            cur["body"].append(line)
    for e in entries:
        e["body"] = "\n".join(e["body"]).strip()
    return entries


def skills_list(block):
    items = re.split(r"[•·|\n,;]+", block)
    return [re.sub(r"^\s*[-*]\s*", "", i).strip() for i in items if i.strip()]


def terms_from_job(job):
    stop = set("""a an the and or for to of in on at by with from as is are be will you your our we this that it its their
    they who what which role job team work working experience years year ability strong skills skill including include
    etc must should can able new across within more other such per candidate company about all any has have help helps
    well looking based plus nice also us part join get make using use used best great good high level knowledge
    understanding excellent responsible responsibilities requirements required preferred qualifications position
    opportunity need needs want ideal ideally between over under into out up one two three own run days day today office
    hybrid remote partner report weekly senior junior lead manager apply send cover letter short close closes
    applications benefits offer pension holiday health competitive salary learning budget markets european proven running
    familiarity exposure right ref fictional example resemblance coincidental figures names reuse small fast-paced
    ambitious""".split())
    clean_job = "\n".join(l for l in strip_html_comments(split_front_matter(job)[1]).splitlines() if not l.lstrip().startswith(">"))
    raw_toks = [w.strip(".-/") for w in re.findall(r"[a-zA-Z][a-zA-Z+#./-]{2,}", clean_job.lower())]
    toks = [w for w in raw_toks if len(w) > 2 and w not in stop]
    counts = collections.Counter(toks)
    return [t for t, _ in counts.most_common(25)]


def lint(text, job=None):
    name, sec = parse(text)
    r = {"name": name, "sections_found": list(sec)}
    problems, notes = [], []

    headline = sec.get("headline", "")
    about = sec.get("about", "") or sec.get("summary", "")
    exp = experience_entries(sec.get("experience", ""))
    skills = skills_list(sec.get("skills", ""))

    r["headline_chars"] = len(headline)
    r["about_chars"] = len(about)
    r["skills_count"] = len(skills)
    r["experience_entries"] = len(exp)

    if not headline:
        problems.append("No Headline section.")
    if len(headline) > LIMITS["headline"]:
        problems.append("Headline is %d chars (limit %d)." % (len(headline), LIMITS["headline"]))
    if headline and not re.search(r"[|·•/,-]", headline) and len(headline.split()) <= 6:
        notes.append("Headline looks like a bare job title. Add specialism + proof/keywords (role | niche | tools or outcome).")
    if re.search(r"open to work|seeking|looking for", headline, re.I):
        notes.append("Headline contains 'open to work/seeking'. Use the Open to Work setting for that; keep the headline about value.")
    if not about:
        problems.append("No About section.")
    if len(about) > LIMITS["about"]:
        problems.append("About is %d chars (limit %d)." % (len(about), LIMITS["about"]))
    if about and len(about) < 600:
        notes.append("About is short (%d chars). Two or three short paragraphs (what you do, proof, what you want next) usually fit better, unless the profile is deliberately minimal." % len(about))
    if about:
        first = about[:300]
        r["about_first_300"] = first
        if not METRIC.search(first) and len(first.split()) > 10:
            notes.append("No number in the first ~300 chars of About (the part visible before 'see more'). Lead with a concrete fact.")
        if re.match(r"\s*(i am|i'm)\s+(a|an)\s+(passionate|dedicated|motivated|results)", about, re.I):
            problems.append("About opens with a cliche ('I am a passionate...'). Open with what you do and the proof.")
    if not skills:
        notes.append("No Skills section. Add 10-30 skills; pin the top 3 that match the target role.")
    for s in skills:
        if len(s) > LIMITS["skill_name"]:
            problems.append("Skill over %d chars: %s..." % (LIMITS["skill_name"], s[:30]))
    if len(skills) > 50:
        notes.append("More than 50 skills. LinkedIn caps skills (50 at time of writing); trim to the target role.")

    exp_issues = []
    total_bullets = metric_bullets = 0
    for e in exp:
        body = e["body"]
        if len(body) > LIMITS["experience_description"]:
            msg = "'%s' description is %d chars (limit %d)." % (e["heading"][:40], len(body), LIMITS["experience_description"])
            exp_issues.append(msg)
            problems.append("Experience: " + msg)
        bl = [re.sub(r"^\s*[-*•]\s*", "", l).strip() for l in body.splitlines() if re.match(r"^\s*[-*•]\s+", l)]
        if not bl and body:
            bl = [p.strip() for p in re.split(r"(?<=[.!?])\s+", body) if p.strip()]
        total_bullets += len(bl)
        metric_bullets += sum(1 for b in bl if METRIC.search(b))
        weak = [b for b in bl if any(b.lower().startswith(w) for w in WEAK_OPENERS)]
        if weak:
            exp_issues.append("'%s' has weak openers: %s" % (e["heading"][:40], "; ".join(w[:50] for w in weak[:2])))
        if not body:
            msg = "'%s' has no description." % e["heading"][:40]
            exp_issues.append(msg)
            problems.append("Experience: " + msg)
    r["experience_issues"] = exp_issues
    r["experience_metric_ratio_pct"] = round(100 * metric_bullets / max(1, total_bullets)) if total_bullets else None
    if total_bullets and r["experience_metric_ratio_pct"] < 40:
        notes.append("Only %d%% of experience lines carry a number. Add scope or results." % r["experience_metric_ratio_pct"])

    whole = " ".join([headline, about, " ".join(e["body"] for e in exp)])
    low = whole.lower()
    r["cliches"] = sorted({c for c in CLICHES if c in low})
    r["emoji_count"] = len(EMOJI.findall(whole))
    if r["emoji_count"] > 3:
        notes.append("%d emoji. A few are fine; many read as noise to recruiters." % r["emoji_count"])
    caps = [w for w in re.findall(r"\b[A-Z]{5,}\b", headline + " " + about)]
    if caps:
        notes.append("ALL-CAPS words: %s" % ", ".join(sorted(set(caps))[:5]))
    ph = sorted({h for _, h in placeholder_hits("\n".join(sec.values()))})
    r["placeholders"] = ph
    if ph:
        problems.append("Placeholders left: %s" % ", ".join(ph))
    custom_url = sec.get("custom url", "").strip()
    if custom_url:
        slug = re.sub(r"^https?://(?:www\.)?linkedin\.com/in/|^linkedin\.com/in/", "", custom_url, flags=re.I).strip("/")
        if not re.fullmatch(r"[A-Za-z0-9-]{3,100}", slug):
            notes.append("Custom URL slug %r should be 3-100 letters, digits or hyphens (linkedin.com/in/firstname-lastname)." % slug)
    if re.search(r"(?<![\w.+-])[\w.+-]+@[\w-]+\.[\w.]+", about):
        notes.append("An email address is in About. It is public; confirm that is intended.")
    if job:
        terms = terms_from_job(job)
        present = [t for t in terms if t in low or t in " ".join(skills).lower()]
        r["keyword_match"] = {"checked": len(terms), "present": present,
                              "missing": [t for t in terms if t not in present],
                              "coverage_pct": round(100 * len(present) / max(1, len(terms)))}
    r["problems"] = problems
    r["notes"] = notes
    return r


def to_text(r):
    out = []
    for k, v in r.items():
        if isinstance(v, (list, dict)) and not v:
            continue
        out.append("%-26s %s" % (k + ":", json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--job", help="job ad text for keyword coverage")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    text = read_text_file(a.file)
    job = read_text_file(a.job, "job ad file") if a.job else None
    r = lint(text, job)
    print(json.dumps(r, indent=2, ensure_ascii=False) if a.json else to_text(r))
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
