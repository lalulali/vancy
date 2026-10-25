#!/usr/bin/env python3
"""Check a professional-reference sheet before it is shared. Zero dependencies (stdlib only).

Usage:
  reference_lint.py REFERENCES_DRAFT.md [--min 2] [--max 5] [--json]

Expected format (Markdown, DRAFT file - consent notes are removed from the final):

  # Your Name
  you@example.com | +44 7700 900123 | City, Country

  ## Professional References
  ### Referee Name | Job Title | Organisation
  - Relationship: Direct manager, Jan 2021 - Present
  - Worked together: 3 years 9 months
  - Email: referee@example.com
  - Phone: +44 7700 900456
  - Best contact: Email first; weekday mornings
  - Can speak to: roadmap ownership, experimentation
  > Consent: confirmed 2026-10-01

The consent note is REQUIRED for every referee. A reference sheet holds other people's personal data,
so the linter fails (exit 1) unless the note is a blockquote ("> Consent: ...") that follows this exact grammar
(case-insensitive, ASCII digits):

  Consent: confirmed [by] [email|phone|in person|message|call|video] YYYY-MM-DD

The date is mandatory and must be a real calendar date from 2000-01-01 up to today. A "- Consent: ..." list
item or plain line is rejected (it would be published). Referee blocks may use heading levels 2-6 and are found
exactly as render_docx.py --final finds them, with the same consent rules. Anything else - declined, withdrawn, requested,
to ask, pending, waiting, maybe, TBD, unknown, "yes" or "agreed" without the grammar above - fails with a
specific message. It cannot verify that the consent is real - the user must ask each person.
Unreadable input exits 2 with an "Error:" message. On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import datetime as _dt
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

# >>> shared:consent
# Referee consent: strict whitelist and referee-block scanner. Needs: re, _dt, strip_html_comments (helpers block).
# Valid: "Consent: confirmed [by] [email|phone|in person|message|call|video] YYYY-MM-DD" (case-insensitive,
# ASCII digits, a real date from 2000-01-01 up to today), written as a blockquote line "> Consent: ...".
CONSENT_RE = re.compile(
    r"confirmed(?:\s+(?:by\s+)?(?:email|phone|in person|message|call|video))?\s+([0-9]{4})-([0-9]{2})-([0-9]{2})",
    re.I | re.A)
_CONSENT_MIN = _dt.date(2000, 1, 1)
_CONSENT_BQ = re.compile(r"^\s*>[>\s]*[*_]{0,3}\s*consent\s*[*_]{0,3}\s*:\s*[*_]{0,3}\s*(.*)$", re.I | re.A)
_CONSENT_ANY = re.compile(r"^[\s>*_+\-0-9.)|]*consent[*_\s]*:", re.I | re.A)
_CONTACT_LINE = re.compile(
    r"^\s*(?:[-*+]\s+)?[*_]{0,3}\s*(?:e-?mail(?: address)?|phone(?: number)?|tel(?:ephone)?|mobile|cell)[*_]{0,3}\s*:",
    re.I | re.A)
_FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
_HEAD_RE = re.compile(r"^\s{0,3}(#{1,6})[ \t]+(.*?)[ \t]*$")
_REF_DOC = re.compile(r"^\s*doc\s*:\s*[\"']?(?:reference|referee|refs)", re.I | re.A | re.M)
_REF_WORD = re.compile(r"\b(?:references?|referees?)\b", re.I | re.A)


def consent_problem(value, today=None):
    """Return None if `value` (the text after 'Consent:') is strictly valid, else a specific message."""
    v = " ".join((value or "").split()).strip("*_ ")
    m = CONSENT_RE.fullmatch(v)
    if m:
        try:
            when = _dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return "consent date %s is not a real calendar date" % "-".join(m.groups())
        if when > (today or _dt.date.today()):
            return "consent date %s is in the future" % when.isoformat()
        if when < _CONSENT_MIN:
            return "consent date %s is before 2000-01-01" % when.isoformat()
        return None
    low = v.lower()
    if not v:
        return "consent line is empty"
    if re.search(r"declin|refus|withdr|revok|cancel|\bno\b|\bnot\b|\bnever\b", low):
        return "consent was declined, withdrawn or negative (%r)" % v
    if re.search(r"request|to ask|\bask|pending|wait|await|maybe|\bperhaps\b|tbd|tbc|unknown|unconfirmed|\bsoon\b", low):
        return "consent is not confirmed yet (%r)" % v
    if low.startswith("confirmed"):
        return ("confirmed consent needs an ISO date and, if a method is given, one of email/phone/in person/"
                "message/call/video, e.g. 'Consent: confirmed by email 2026-01-31' (got %r)" % v)
    if re.match(r"(yes|agreed?|granted|given|ok(ay)?)\b", low):
        return "%r is not enough: write 'Consent: confirmed [by email|phone|...] YYYY-MM-DD' with the date (got %r)" % (low.split()[0], v)
    return "consent must read 'Consent: confirmed [by email|phone|in person|message|call|video] YYYY-MM-DD' (got %r)" % v


def _name_shape(title):
    """'Name | Title | Org' (two or more '|' parts) or 'Name - Title' with an em/en dash or spaced hyphen."""
    if len([p for p in re.split(r"\s*\|\s*", title) if p.strip()]) >= 2:
        return True
    return len([p for p in re.split(r"\s+[\u2014\u2013-]\s+", title) if p.strip()]) >= 2


def _ref_name(title):
    first = re.split(r"\s*\|\s*|\s+[\u2014\u2013-]\s+", title)[0].strip()
    return re.sub(r"[*_`]", "", first) or "?"


def ref_scan(text, doc_key="", force=False):
    """Find referee blocks in Markdown. Returns {"looks_like", "strong", "blocks", "reason"}.

    A document is treated as a reference sheet when `force`, or when its `doc:` value starts with
    reference/referee/refs, or it has any 'Consent:' line, or a level 2-6 heading of the shape
    'Name | Title | Org' / 'Name - Title' is followed by an Email:/Phone: line, or a heading mentions
    'reference'/'referee' and the section under it holds an e-mail address, phone number or Email:/Phone: line.
    A referee block runs from its heading to the next referee heading or to the next heading of the same or a
    higher level; deeper non-referee sub-headings belong to it. 'Consent:' lines inside fenced code blocks or
    HTML comments never count, and consent never carries over from one block to the next.
    """
    t = strip_html_comments(text.replace("\r\n", "\n").replace("\r", "\n"), keep_lines=True)
    lines = t.split("\n")
    fenced, fence = [], None
    for ln in lines:
        fm = _FENCE_RE.match(ln)
        if fence is None:
            fenced.append(bool(fm))
            if fm:
                fence = (fm.group(1)[0], len(fm.group(1)))
        else:
            fenced.append(True)
            if fm and fm.group(1)[0] == fence[0] and len(fm.group(1)) >= fence[1] and ln.strip().strip(fence[0]) == "":
                fence = None
    strong = bool(force or str(doc_key or "").lower().lstrip().startswith(("reference", "referee", "refs"))
                  or _REF_DOC.search("\n".join(lines[:25])) or any(_CONSENT_ANY.match(ln) for ln in lines))
    cands, cur, parent, weak = [], None, None, []
    for i, ln in enumerate(lines):
        hm = _HEAD_RE.match(ln)
        if hm:
            level, title = len(hm.group(1)), re.sub(r"\s+#+$", "", hm.group(2)).strip()
            if level == 1:
                cur = parent = None
                continue
            shape = _name_shape(title)
            if _REF_WORD.search(title):
                weak.append((i, level))
            if parent is not None and level > parent["level"] and not shape:
                cur = parent                      # sub-heading inside a referee block
                continue
            cur = {"heading": title, "name": _ref_name(title), "level": level, "line": i + 1, "shape": shape,
                   "lines": [], "consents": [], "loose": [], "contact": False}
            cands.append(cur)
            parent = cur if shape else None
            continue
        if cur is None:
            continue
        cur["lines"].append((ln, fenced[i]))
        if _CONTACT_LINE.match(ln):
            cur["contact"] = True
        if fenced[i]:
            continue
        bq = _CONSENT_BQ.match(ln)
        if bq:
            cur["consents"].append(bq.group(1).strip())
        elif _CONSENT_ANY.match(ln):
            cur["loose"].append(ln.strip())
    blocks = []
    for c in cands:
        if c["shape"] and (strong or c["contact"]):
            blocks.append(c)
        elif strong and c["contact"] and not re.search(r"\bcontact\b|\babout\b", c["heading"], re.I):
            blocks.append(c)
    reason = ""
    if blocks and not strong:
        reason = "headings shaped like 'Name | Title | Org' with Email:/Phone: lines"
    elif strong:
        reason = "front matter 'doc:' or a 'Consent:' line marks it as a reference sheet"
    looks = strong or bool(blocks)
    if not looks and weak:
        pat = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\+?\d[\d ()-]{7,}\d")
        for i, level in weak:
            j = i + 1
            while j < len(lines):
                hm = _HEAD_RE.match(lines[j])
                if hm and len(hm.group(1)) <= level:
                    break
                if pat.search(lines[j]) or _CONTACT_LINE.match(lines[j]):
                    looks, reason = True, "a References/Referees heading is followed by contact details"
                    break
                j += 1
            if looks:
                break
    return {"looks_like": looks, "strong": strong, "blocks": blocks, "reason": reason}


def block_consent_problems(b, today=None):
    """Bare messages (no name prefix) for one referee block from ref_scan()."""
    if not b["consents"]:
        msg = "no '> Consent: confirmed ... YYYY-MM-DD' note"
        if b["loose"]:
            msg += " (a 'Consent:' list item or plain line is not accepted and would be published; use a '>' blockquote note)"
        return [msg]
    out = [m for m in (consent_problem(c, today) for c in b["consents"]) if m]
    if b["loose"]:
        out.append("a 'Consent:' list item or plain line would be published in the final document; "
                   "use a '>' blockquote note only")
    return out


def consent_problems(scan, today=None):
    """Messages for every referee block of a ref_scan() result that lacks a valid, dated consent note."""
    return ["%s (line %d): %s" % (b["name"], b["line"], m) for b in scan["blocks"] for m in block_consent_problems(b, today)]


def referee_consent_problems(body, doc_key=""):
    """(problems, number_of_referee_blocks, looks_like_reference_sheet, reason) for a document body."""
    scan = ref_scan(body, doc_key)
    problems = consent_problems(scan)
    if scan["looks_like"] and not scan["blocks"]:
        problems.append("this looks like a reference sheet (%s) but no referee blocks were found; "
                        "each referee needs a '### Name | Title | Organisation' heading" % (scan["reason"] or "reference heading"))
    return problems, len(scan["blocks"]), scan["looks_like"], scan["reason"]
# <<< shared:consent


EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(?:\.[\w-]+)+$")
# Applied to the Relationship field ONLY (never to titles or employer names, so "managing partner" or
# "Family Office Capital" do not trigger). "Partner" is deliberately absent: a romantic partner cannot be
# told apart from a business partner by text alone.
PERSONAL_REL = re.compile(
    r"\b(friends?|neighbou?rs?|relatives?(?!\s+to\b)|spouses?|siblings?|cousins?|in-laws?|"
    r"parents?(?!\s+(?:company|organi[sz]ation|firm|group|corporation|entity))|"
    r"brothers?|sisters?(?!\s+(?:company|organi[sz]ation|firm|group|corporation|entity))|mothers?|fathers?|"
    r"flatmates?|roommates?|family\s+friends?)\b", re.I)
# Only when the whole Relationship field is exactly one of these words (they are too ambiguous inside a sentence).
PERSONAL_EXACT = re.compile(
    r"(?:(?:my|his|her|their|a|an|the)\s+)?(?:aunt|uncle|husband|wife|girlfriend|boyfriend|partner[- ]in[- ]life|"
    r"fianc[e\u00e9]e?|stepmother|stepfather|grandmother|grandfather|nephew|niece)", re.I)
REQUIRED = ["relationship", "email", "phone"]


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
        sys.stderr.write("Error: %s is a binary file (PDF/Office?). Provide the Markdown/text draft.\n" % path)
        raise SystemExit(2)
    try:
        return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        sys.stderr.write("Error: %s is not valid UTF-8 text. Re-save it as UTF-8.\n" % path)
        raise SystemExit(2)


def personal_relationship(rel):
    """True if the Relationship field describes a friend/family tie rather than a professional one."""
    plain = re.sub(r"[.!;,]+$", "", " ".join((rel or "").split())).strip()
    if PERSONAL_EXACT.fullmatch(plain):
        return True
    for m in PERSONAL_REL.finditer(plain):
        if m.group(0)[:1].isupper() and re.match(r"\s+[A-Z]", plain[m.end():]):
            continue                                  # a capitalised name such as "Mother Teresa Foundation"
        return True
    return False


def parse(text):
    """Returns (owner, referees, scan). Referee blocks are found by ref_scan, exactly as in render_docx.py --final."""
    meta, body, _state = split_front_matter(text)
    body = strip_html_comments(body)
    owner = (re.search(r"^#[ \t]+(.+?)[ \t]*$", body, flags=re.M) or [None, ""])[1]
    scan = ref_scan(body, meta.get("doc", ""), force=True)
    refs = []
    for blk in scan["blocks"]:
        parts = [p.strip() for p in re.split(r"\s*\|\s*", blk["heading"])]
        if len(parts) < 2:
            parts = [p.strip() for p in re.split(r"\s+[\u2014\u2013-]\s+", blk["heading"])]
        ref = {"heading": blk["heading"], "name": parts[0] if parts and parts[0] else blk["name"],
               "title": parts[1] if len(parts) > 1 else "", "org": parts[2] if len(parts) > 2 else "",
               "fields": {}, "consents": blk["consents"], "loose": blk["loose"], "line": blk["line"]}
        for line, fenced in blk["lines"]:
            if fenced or _CONSENT_ANY.match(line):
                continue
            m = re.match(r"^\s*(?:[-*+]\s*)?[*_]{0,3}([A-Za-z][A-Za-z ]+?)[*_]{0,3}\s*:\s*[*_]{0,3}\s*(.*)$", line)
            if m:
                ref["fields"][m.group(1).strip().lower()] = m.group(2).strip()
        refs.append(ref)
    return owner, refs, scan


def lint(text, lo=2, hi=5):
    owner, refs, scan = parse(text)
    r = {"owner": owner, "referees": len(refs)}
    problems, notes, per = [], [], []
    if not refs:
        problems.append("No referees found. Each needs a '### Name | Title | Organisation' heading (levels 2-6 are accepted).")
    if refs and len(refs) < lo:
        notes.append("%d referee(s). Employers commonly ask for two or three; have at least %d ready." % (len(refs), lo))
    if len(refs) > hi:
        notes.append("%d referees. A short, relevant list is easier to use; consider trimming to the %d most relevant." % (len(refs), hi))
    seen = {}
    for ref in refs:
        f = ref["fields"]
        issues, rnotes = [], []
        if not ref["name"] or not ref["title"] or not ref["org"]:
            issues.append("Heading needs name, title and organisation.")
        for k in REQUIRED:
            if not f.get(k):
                issues.append("Missing %s." % k)
        em = f.get("email", "")
        if em and not EMAIL.match(em):
            issues.append("Email looks invalid: %s" % em)
        ph = f.get("phone", "")
        if ph and not ph.strip().startswith("+"):
            rnotes.append("Phone has no country code. Add it for international use.")
        if ph and len(re.sub(r"\D", "", ph)) < 7:
            issues.append("Phone looks too short: %s" % ph)
        for cp in block_consent_problems(ref):
            issues.append("Consent: %s." % cp.rstrip("."))
        rel = f.get("relationship", "")
        if personal_relationship(rel):
            issues.append("Relationship looks personal (%r). Use professional or academic referees." % rel)
        if not f.get("can speak to"):
            rnotes.append("No 'Can speak to' line. Add 2-3 topics that match the target role.")
        if not f.get("worked together") and not re.search(r"\d{4}", rel):
            rnotes.append("No 'Worked together' length or dates.")
        if ph:
            digits = re.sub(r"\D", "", ph)
            if digits in seen:
                issues.append("Same phone number as %s." % seen[digits])
            seen[digits] = ref["name"]
        if placeholder_hits(ref["heading"] + "\n" + "\n".join(f.values())):
            issues.append("Placeholder text present.")
        per.append({"name": ref["name"], "issues": issues, "notes": rnotes})
        problems += ["%s: %s" % (ref["name"] or "?", i) for i in issues]
    r["per_referee"] = per
    r["problems"], r["notes"] = problems, notes
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--min", type=int, default=2)
    ap.add_argument("--max", type=int, default=5)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    res = lint(read_text_file(a.file), a.min, a.max)
    if a.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Owner: %s   Referees: %d" % (res["owner"], res["referees"]))
        for p in res["per_referee"]:
            status = "PROBLEMS" if p["issues"] else "ok"
            print("  - %s: %s" % (p["name"], status))
            for i in p["issues"]:
                print("      PROBLEM: " + i)
            for n in p["notes"]:
                print("      note: " + n)
        for n in res["notes"]:
            print("note: " + n)
        print("RESULT: %s" % ("FAIL - do not share this sheet yet" if res["problems"] else "pass"))
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
