#!/usr/bin/env python3
"""Render a CV, cover letter or similar career document from constrained Markdown into a Word (.docx) file.

Zero dependencies: Python 3.8+ standard library only (zipfile + hand-written OOXML).
Output is single-column, uses real Word heading/list styles, keeps all text in the
document body (no tables, text boxes, headers or footers), so it parses cleanly in
applicant tracking systems and reads correctly with screen readers.

Usage:
  render_docx.py INPUT.md -o OUTPUT.docx [--template NAME] [--page a4|letter]
                 [--lang en-GB] [--final] [--clean-md OUT.md] [--allow-placeholders] [--allow-outside]
  render_docx.py --list-templates

Front matter `doc:` (optional, default cv). It sets the Word title property and, for letters, the body style:
  cv | resume | cover-letter (cover, letter, cl) | references | linkedin | interview |
  case-study / portfolio | offer | negotiation
All types share the same Markdown rules and templates; only cover letters get letter spacing.

Draft vs final:
  Draft (default): reviewer notes (lines starting with ">") are shown as shaded
  notes, footnote citations [^n] are shown as superscripts, and footnote
  definitions ("[^n]: ...") are listed under "Draft sources" at the end.
  --final: strips notes, citations, footnote definitions and HTML comments, and
  refuses to render if unfilled placeholders remain (e.g. "[Company]", "XX%", "TBD",
  "{{name}}", "insert metric"). For a reference sheet, --final also refuses (exit 2) unless EVERY referee
  block has a line "> Consent: confirmed [by] [email|phone|in person|message|call|video] YYYY-MM-DD"
  (a real date, not in the future, not before 2000). A document counts as a reference sheet if its
  `doc:` value starts with reference/referee/refs, or it has any "Consent:" line, or it has a heading shaped
  like "Name | Title | Org" / "Name - Title" followed by an Email:/Phone: line, or a "References" heading
  followed by contact details; then zero referee blocks is also refused.
  --allow-placeholders overrides the placeholder check only (never the consent check).

Where files may be written (every -o and --clean-md target is checked first; refusal = exit 2):
  * inside <cwd>/artifacts/output if that folder exists, otherwise inside <cwd> (missing sub-folders are created);
  * -o must end in .docx, --clean-md in .md or .txt;
  * never into a folder named .agents, .kiro, .claude, .ssh or .git, never into artifacts/input, never into a
    folder tree that holds a SKILL.md, and never onto an existing symbolic link.
  --allow-outside lifts ONLY the "inside the output folder" restriction; the protected locations stay blocked.

Safety: invisible Unicode (zero-width space/word joiner, bidi embeddings and overrides, tag characters,
variation-selector supplements, Hangul/braille fillers, other format characters) and characters illegal in XML are
removed from all text, with a warning that gives the count. Joiners inside real scripts (ZWNJ in Persian, ZWJ in
emoji sequences) and LRM/RLM next to right-to-left text are kept. The output is only written if the
built file passes a text round-trip self-check. On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import datetime as _dt
import os
import re
import sys
import tempfile
import unicodedata
import zipfile
from xml.dom import minidom
from xml.parsers.expat import ExpatError
from xml.sax.saxutils import escape

# --------------------------------------------------------------------------- themes
# All templates are original, single-column, ATS-safe designs. Fonts are chosen from
# families that ship with Microsoft Office on Windows and macOS (with safe fallbacks).
THEMES = {
    "classic": {
        "label": "Classic - centred serif header, black rules. Law, finance, government, academia.",
        "font": "Georgia", "head_font": "Georgia", "size": 10.5, "name_size": 22,
        "accent": "000000", "text": "1A1A1A", "muted": "4D4D4D",
        "align_header": "center", "h1_caps": True, "h1_size": 11.5, "h1_color": "000000",
        "rule": "single", "rule_color": "000000", "margins_in": 0.8, "spacing": 1.0,
    },
    "modern": {
        "label": "Modern - left-aligned sans, teal accent. Tech, product, marketing, startups.",
        "font": "Calibri", "head_font": "Calibri", "size": 10.5, "name_size": 24,
        "accent": "1F6F78", "text": "222222", "muted": "555555",
        "align_header": "left", "h1_caps": True, "h1_size": 12, "h1_color": "1F6F78",
        "rule": "single", "rule_color": "1F6F78", "margins_in": 0.75, "spacing": 1.0,
    },
    "minimal": {
        "label": "Minimal - Arial, black only, no colour. Maximum ATS safety, any industry.",
        "font": "Arial", "head_font": "Arial", "size": 10, "name_size": 18,
        "accent": "000000", "text": "000000", "muted": "333333",
        "align_header": "left", "h1_caps": True, "h1_size": 11, "h1_color": "000000",
        "rule": None, "rule_color": "000000", "margins_in": 0.7, "spacing": 1.0,
    },
    "executive": {
        "label": "Executive - Cambria, navy accent, letter-spaced headings. Director, VP, C-suite.",
        "font": "Cambria", "head_font": "Cambria", "size": 11, "name_size": 26,
        "accent": "1F3864", "text": "1A1A1A", "muted": "44546A",
        "align_header": "center", "h1_caps": True, "h1_size": 12, "h1_color": "1F3864",
        "rule": "double", "rule_color": "1F3864", "margins_in": 0.85, "spacing": 1.05,
        "h1_tracking": 30,
    },
    "compact": {
        "label": "Compact - tight Calibri, plum accent, fits one page. Students, graduates, career starters.",
        "font": "Calibri", "head_font": "Calibri", "size": 10, "name_size": 20,
        "accent": "5B2A6E", "text": "222222", "muted": "555555",
        "align_header": "left", "h1_caps": True, "h1_size": 11, "h1_color": "5B2A6E",
        "rule": "single", "rule_color": "5B2A6E", "margins_in": 0.55, "spacing": 0.95,
    },
}

# Word "title" property label by front-matter `doc:` value (first matching prefix wins).
DOC_LABELS = [
    ("cover", "Cover Letter"), ("letter", "Cover Letter"), ("cl", "Cover Letter"),
    ("cv", "CV"), ("resume", "CV"), ("reference", "References"), ("linkedin", "LinkedIn Profile"),
    ("referee", "References"), ("refs", "References"), ("interview", "Interview Prep"), ("case", "Case Study"), ("portfolio", "Portfolio"),
    ("offer", "Offer Review"), ("negotiat", "Negotiation Plan"),
]

PAGES = {  # twips (1/1440 inch)
    "a4": (11906, 16838),
    "letter": (12240, 15840),
}

# --------------------------------------------------------------------------- shared blocks
# These regions are identical in every script that carries them (each skill is standalone).
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


DATE_HINT = re.compile(r"(\d{4}|present|current|now|ongoing|expected|in progress)", re.I)


# --------------------------------------------------------------------------- parsing
def split_frontmatter(text):
    """Return (meta, body, state); see split_front_matter. state 'unclosed' = '---' opened but never closed."""
    return split_front_matter(text)


def clean_for_final(text):
    """Remove draft-only material: notes, citations, footnote defs, comments."""
    text = strip_html_comments(text)
    lines = []
    for line in text.splitlines():
        if line.lstrip().startswith(">"):
            continue
        if re.match(r"^\s*\[\^[^\]]{1,100}\]:", line):
            continue
        lines.append(re.sub(r"\s?\[\^[^\]]{1,100}\]", "", line))
    out = "\n".join(lines)
    out = re.sub(r"\n{3,}", "\n\n", out)
    return out.strip() + "\n"


def find_placeholders(text):
    return placeholder_hits(text)


# >>> shared:invisible
# Characters that are invalid in XML 1.0 (everything except tab, LF, CR and the valid ranges).
_XML_BAD = re.compile("[^\u0009\u000A\u000D\u0020-\uD7FF\uE000-\uFFFD\U00010000-\U0010FFFF]")
# Invisible but not category Cf: combining grapheme joiner, Hangul/Khmer fillers, braille blank.
_INVISIBLE_OTHER = frozenset([0x034F, 0x115F, 0x1160, 0x17B4, 0x17B5, 0x3164, 0xFFA0, 0x2800])
_BIDI_MARKS = frozenset([0x200E, 0x200F, 0x061C])               # LRM, RLM, ALM


def _emoji_like(ch):
    cp = ord(ch)
    return (0x1F000 <= cp <= 0x1FAFF or 0x2190 <= cp <= 0x21FF or 0x2300 <= cp <= 0x23FF
            or 0x25A0 <= cp <= 0x25FF or 0x2600 <= cp <= 0x27BF or 0x2900 <= cp <= 0x297F
            or 0x2B00 <= cp <= 0x2BFF
            or cp in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139, 0x3030, 0x303D, 0x3297, 0x3299))


def _is_rtl(ch):
    return unicodedata.bidirectional(ch) in ("R", "AL")


def _no_joiner_script(ch):
    """Scripts where a joiner never has a purpose between letters (so it can only hide text)."""
    return unicodedata.name(ch, "").split(" ")[0] in (
        "LATIN", "CYRILLIC", "GREEK", "CJK", "HIRAGANA", "KATAKANA", "HANGUL", "FULLWIDTH", "HALFWIDTH")


def _prev_base(out):
    """Last kept character that is not a combining mark or emoji variation selector."""
    j = len(out) - 1
    while j >= 0 and (out[j] == "\ufe0f" or unicodedata.category(out[j]).startswith("M")):
        j -= 1
    return out[j] if j >= 0 else ""


def _keep_joiner(out, text, i, cp):
    """ZWNJ/ZWJ is kept only between letters of a joining script (not Latin+Latin) or, for ZWJ, inside an emoji sequence."""
    prev = _prev_base(out)
    nxt = text[i + 1] if i + 1 < len(text) else ""
    if not prev or not nxt:
        return False
    if cp == 0x200D and _emoji_like(prev) and _emoji_like(nxt):
        return True
    if unicodedata.category(prev).startswith("L") and unicodedata.category(nxt).startswith("L"):
        return not (_no_joiner_script(prev) or _no_joiner_script(nxt))
    return False


def _keep_mark(out, text, i):
    """LRM/RLM/ALM is kept only next to right-to-left text."""
    j = len(out) - 1
    while j >= 0 and (out[j] in " \t" or ord(out[j]) in _BIDI_MARKS):
        j -= 1
    if j >= 0 and _is_rtl(out[j]):
        return True
    k = i + 1
    while k < len(text) and (text[k] in " \t" or ord(text[k]) in _BIDI_MARKS):
        k += 1
    return k < len(text) and _is_rtl(text[k])


def sanitize_text(text):
    """Remove XML-invalid and invisible/format Unicode. Returns (clean_text, removed_count).

    Removed: XML-invalid control characters, lone surrogates, category Cf (zero-width space U+200B, word joiner
    U+2060, BOM U+FEFF, bidi embeddings/overrides U+202A-202E, isolates U+2066-2069, soft hyphen, ...), the tag
    block U+E0000-E007F, variation selectors U+E0100-E01EF, and U+034F, U+115F, U+1160, U+3164, U+FFA0, U+2800.
    Kept: ZWNJ/ZWJ between letters of a joining script (Persian, Indic) and ZWJ inside emoji sequences;
    LRM/RLM next to right-to-left text. Hidden characters can carry instructions aimed at software.
    """
    out, removed = [], 0
    for i, ch in enumerate(text):
        cp = ord(ch)
        if 0x20 <= cp < 0x7F or cp in (9, 10, 13):
            out.append(ch)
            continue
        if _XML_BAD.match(ch) or (cp & 0xFFFE) == 0xFFFE:
            keep = False
        elif cp in (0x200C, 0x200D):
            keep = _keep_joiner(out, text, i, cp)
        elif cp in _BIDI_MARKS:
            keep = _keep_mark(out, text, i)
        else:
            keep = not (unicodedata.category(ch) == "Cf" or cp in _INVISIBLE_OTHER or 0xE0100 <= cp <= 0xE01EF)
        if keep:
            out.append(ch)
        else:
            removed += 1
    return "".join(out), removed
# <<< shared:invisible


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


def parse(body):
    """Return list of blocks: (kind, payload)."""
    blocks = []
    footnotes = []
    para = []

    def flush():
        if para:
            blocks.append(("para", list(para)))
            para.clear()

    for raw in body.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        m = re.match(r"^\[\^([^\]]+)\]:\s*(.*)$", stripped)
        if m:
            flush()
            footnotes.append((m.group(1), m.group(2)))
            continue
        if stripped.startswith("<!--"):
            continue
        if stripped.startswith(">"):
            flush()
            blocks.append(("note", stripped.lstrip("> ").strip()))
            continue
        if line.startswith("# "):
            flush()
            blocks.append(("name", stripped[2:].strip()))
            continue
        if line.startswith("## "):
            flush()
            blocks.append(("h1", stripped[3:].strip()))
            continue
        if line.startswith("### "):
            flush()
            blocks.append(("h2", stripped[4:].strip()))
            continue
        m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", stripped)
        if m:
            flush()
            blocks.append(("figure", m.group(1).strip()))
            continue
        m = re.match(r"^(\s*)[-*+]\s+(.*)$", line)
        if m and not re.match(r"^\s*\*\*", line):
            flush()
            level = 1 if len(m.group(1).replace("\t", "    ")) >= 2 else 0
            blocks.append(("bullet", (level, m.group(2).strip())))
            continue
        if re.fullmatch(r"[-_*]{3,}", stripped):
            flush()
            continue
        para.append(stripped)
    flush()
    return blocks, footnotes


# --------------------------------------------------------------------------- OOXML
def run_xml(text, bold=False, italic=False, sup=False, color=None, size=None, caps=False):
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if caps:
        props.append("<w:caps/>")
    if color:
        props.append('<w:color w:val="%s"/>' % color)
    if size:
        props.append('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (size * 2, size * 2))
    if sup:
        props.append('<w:vertAlign w:val="superscript"/>')
    rpr = "<w:rPr>%s</w:rPr>" % "".join(props) if props else ""
    parts = text.split("\t")
    inner = '<w:tab/>'.join('<w:t xml:space="preserve">%s</w:t>' % escape(p) for p in parts)
    return "<w:r>%s%s</w:r>" % (rpr, inner)


# Inline syntax (spans are length-capped so hostile input cannot cause quadratic matching).
# Emphasis follows flanking rules so that intra-word markers survive:
# jane_doe@x.com, scikit_learn, __init__, 2*3*4. Bare e-mails and URLs are never emphasised.
INLINE_RE = re.compile(
    r"(?P<lit>(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+|https?://[^\s<>\")\]]+)"
    r"|(?P<fn>\[\^[^\]]{1,100}\])"
    r"|(?P<link>\[(?P<label>[^\]]{1,300})\]\((?P<url>[^)]{1,2000})\))"
    r"|\*\*(?=\S)(?P<b1>.{1,600}?)(?<=\S)\*\*"
    r"|(?<![\w])__(?=\S)(?P<b2>.{1,600}?)(?<=\S)__(?![\w])"
    r"|(?<![\w*])\*(?=[^\s*])(?P<i1>[^*]{1,600}?)(?<=[^\s*])\*(?![\w*])"
    r"|(?<![\w])_(?=[^\s_])(?P<i2>.{1,600}?)(?<=[^\s_])_(?![\w])")


def _link_text(label, url):
    bare = lambda u: u.replace("https://", "").replace("http://", "")
    return label if bare(label) == bare(url) else "%s (%s)" % (label, url)


def inline_tokens(text, final=False):
    """Split inline Markdown into (kind, text) tokens: plain, bold, italic, sup (draft citation)."""
    out, pos = [], 0
    for m in INLINE_RE.finditer(text):
        if m.group("b2") is not None and re.fullmatch(r"\w+", m.group("b2")):
            continue  # __init__ style identifiers stay literal
        if m.start() > pos:
            out.append(("plain", text[pos:m.start()]))
        kind = m.lastgroup
        if kind in ("lit",):
            out.append(("plain", m.group("lit")))
        elif kind == "fn":
            if not final:
                out.append(("sup", m.group("fn")[2:-1]))
        elif kind in ("link", "label", "url"):
            out.append(("plain", _link_text(m.group("label"), m.group("url"))))
        elif m.group("b1") is not None or m.group("b2") is not None:
            out.append(("bold", m.group("b1") if m.group("b1") is not None else m.group("b2")))
        else:
            out.append(("italic", m.group("i1") if m.group("i1") is not None else m.group("i2")))
        pos = m.end()
    if pos < len(text):
        out.append(("plain", text[pos:]))
    return out


def inline_plain(text, final=True):
    """Plain text of an inline-Markdown string (what a reader sees)."""
    return "".join(t for k, t in inline_tokens(text, final))


def inline_runs(text, final=False, base_bold=False, base_italic=False, color=None):
    out = []
    for kind, t in inline_tokens(text, final):
        if kind == "bold":
            out.append(run_xml(t, True, base_italic, color=color))
        elif kind == "italic":
            out.append(run_xml(t, base_bold, True, color=color))
        elif kind == "sup":
            out.append(run_xml(t, sup=True, color="7F7F7F"))
        else:
            out.append(run_xml(t, base_bold, base_italic, color=color))
    return "".join(out)


def p_xml(runs, style=None, align=None, tabs=None, keep_next=False, spacing_after=None, shade=None):
    ppr = []
    if style:
        ppr.append('<w:pStyle w:val="%s"/>' % style)
    if keep_next:
        ppr.append("<w:keepNext/>")
    if shade:
        ppr.append('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shade)
    if tabs:
        ppr.append("<w:tabs>%s</w:tabs>" % "".join('<w:tab w:val="right" w:pos="%d"/>' % t for t in tabs))
    if spacing_after is not None:
        ppr.append('<w:spacing w:after="%d"/>' % spacing_after)
    if align:
        ppr.append('<w:jc w:val="%s"/>' % align)
    return "<w:p><w:pPr>%s</w:pPr>%s</w:p>" % ("".join(ppr), runs)


def attr(value):
    """Escape a value for use inside a double-quoted XML attribute."""
    return escape(str(value), {'"': "&quot;"})


def styles_xml(t, lang):
    sz = int(round(t["size"] * 2))
    line = int(240 * t["spacing"])
    border = ""
    if t["rule"]:
        border = ('<w:pBdr><w:bottom w:val="%s" w:sz="%d" w:space="1" w:color="%s"/></w:pBdr>'
                  % (t["rule"], 6 if t["rule"] == "single" else 4, t["rule_color"]))
    caps = "<w:caps/>" if t["h1_caps"] else ""
    tracking = '<w:spacing w:val="%d"/>' % t["h1_tracking"] if t.get("h1_tracking") else ""
    fonts = '<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:eastAsia="{f}" w:cs="{f}"/>'

    def font(f):
        return fonts.format(f=f)

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:docDefaults><w:rPrDefault><w:rPr>{font(t['font'])}<w:color w:val="{t['text']}"/><w:sz w:val="{sz}"/><w:szCs w:val="{sz}"/><w:lang w:val="{attr(lang)}"/></w:rPr></w:rPrDefault>
<w:pPrDefault><w:pPr><w:spacing w:after="60" w:line="{line}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:after="40"/><w:jc w:val="{t['align_header']}"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr>{font(t['head_font'])}<w:b/><w:color w:val="{t['accent'] if t['accent'] != '000000' else t['text']}"/><w:sz w:val="{t['name_size']*2}"/><w:szCs w:val="{t['name_size']*2}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:qFormat/>
<w:pPr><w:spacing w:after="20"/><w:jc w:val="{t['align_header']}"/></w:pPr><w:rPr><w:b/><w:color w:val="{t['muted']}"/><w:sz w:val="{sz+2}"/><w:szCs w:val="{sz+2}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:customStyle="1" w:styleId="Contact"><w:name w:val="Contact"/><w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:after="160"/><w:jc w:val="{t['align_header']}"/></w:pPr><w:rPr><w:color w:val="{t['muted']}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/>{border}<w:spacing w:before="200" w:after="80"/><w:outlineLvl w:val="0"/></w:pPr><w:rPr>{font(t['head_font'])}<w:b/>{caps}{tracking}<w:color w:val="{t['h1_color']}"/><w:sz w:val="{int(t['h1_size']*2)}"/><w:szCs w:val="{int(t['h1_size']*2)}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/>
<w:pPr><w:keepNext/><w:spacing w:before="120" w:after="0"/><w:outlineLvl w:val="1"/></w:pPr><w:rPr>{font(t['head_font'])}<w:b/><w:color w:val="{t['text']}"/><w:sz w:val="{sz+1}"/><w:szCs w:val="{sz+1}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:customStyle="1" w:styleId="RoleMeta"><w:name w:val="Role Meta"/><w:basedOn w:val="Normal"/>
<w:pPr><w:keepNext/><w:spacing w:after="40"/></w:pPr><w:rPr><w:i/><w:color w:val="{t['muted']}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:customStyle="1" w:styleId="SubHeading"><w:name w:val="Sub Heading"/><w:basedOn w:val="Normal"/>
<w:pPr><w:keepNext/><w:spacing w:before="60" w:after="20"/></w:pPr><w:rPr><w:b/><w:color w:val="{t['accent'] if t['accent'] != '000000' else t['text']}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet"><w:name w:val="List Bullet"/><w:basedOn w:val="Normal"/>
<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr><w:spacing w:after="30"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="ListBullet2"><w:name w:val="List Bullet 2"/><w:basedOn w:val="Normal"/>
<w:pPr><w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr><w:spacing w:after="30"/></w:pPr></w:style>
<w:style w:type="paragraph" w:customStyle="1" w:styleId="LetterBody"><w:name w:val="Letter Body"/><w:basedOn w:val="Normal"/>
<w:pPr><w:spacing w:after="200" w:line="{int(line*1.08)}" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="{sz+1}"/><w:szCs w:val="{sz+1}"/></w:rPr></w:style>
<w:style w:type="paragraph" w:customStyle="1" w:styleId="DraftNote"><w:name w:val="Draft Note"/><w:basedOn w:val="Normal"/>
<w:pPr><w:shd w:val="clear" w:color="auto" w:fill="FFF4CE"/><w:spacing w:before="40" w:after="80"/><w:ind w:left="144"/></w:pPr><w:rPr><w:i/><w:color w:val="5C4400"/><w:sz w:val="{max(sz-2,16)}"/></w:rPr></w:style>
</w:styles>"""


def numbering_xml(t):
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="hybridMultilevel"/>
<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="&#8226;"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="300" w:hanging="220"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:color w:val="{t['accent'] if t['accent'] != '000000' else '000000'}"/></w:rPr></w:lvl>
<w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="&#8211;"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="660" w:hanging="220"/></w:pPr><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/></w:rPr></w:lvl>
</w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>"""


def split_role(text):
    """'Title | Company | Location | Dates' -> (title, meta, dates)."""
    parts = [p.strip() for p in re.split(r"\s+\|\s+", text) if p.strip()]
    dates = ""
    if len(parts) > 1 and DATE_HINT.search(parts[-1]):
        dates = parts.pop()
    title = parts[0] if parts else text
    meta = ", ".join(parts[1:])
    return title, meta, dates


def build_document(meta, blocks, footnotes, theme, page, final):
    t = THEMES[theme]
    pw, ph = PAGES[page]
    margin = int(t["margins_in"] * 1440)
    text_width = pw - 2 * margin
    doc_type = meta.get("doc", "cv").lower()
    is_letter = doc_type.startswith(("cover", "letter")) or doc_type == "cl"
    body = []
    header_lines_left = 0
    seen_name = False

    for kind, payload in blocks:
        if kind == "name":
            body.append(p_xml(inline_runs(payload, final), "Title"))
            seen_name = True
            header_lines_left = 2
            continue
        if kind == "para" and seen_name and header_lines_left:
            # Lines directly after the name: headline (optional) + contact line.
            lines = payload
            for ln in lines:
                is_contact = ("@" in ln or "|" in ln or re.search(r"\+?\d[\d ()-]{6,}", ln))
                style = "Contact" if is_contact else "Subtitle"
                body.append(p_xml(inline_runs(ln, final), style))
            header_lines_left = 0
            continue
        header_lines_left = 0
        if kind == "h1":
            body.append(p_xml(inline_runs(payload, final), "Heading1"))
        elif kind == "h2":
            title, rmeta, dates = split_role(payload)
            runs = inline_runs(title, final)
            if dates:
                runs += run_xml("\t") + run_xml(dates, bold=False, color=t["muted"])
            body.append(p_xml(runs, "Heading2", tabs=[text_width]))
            if rmeta:
                body.append(p_xml(inline_runs(rmeta, final), "RoleMeta"))
        elif kind == "bullet":
            level, txt = payload
            body.append(p_xml(inline_runs(txt, final), "ListBullet2" if level else "ListBullet"))
        elif kind == "figure":
            label = ("Figure: " + payload) if payload else "Figure"
            body.append(p_xml(run_xml(label + " (image not embedded)", italic=True, color=t["muted"]), "RoleMeta"))
        elif kind == "note":
            if not final:
                note = re.sub(r"^(draft\s+)?note:\s*", "", payload, flags=re.I)
                body.append(p_xml(run_xml("Draft note: ", bold=True) + inline_runs(note, False), "DraftNote"))
        elif kind == "para":
            if len(payload) == 1 and re.fullmatch(r"\*\*[^*]+\*\*:?", payload[0]):
                # A line that is entirely bold, e.g. "**Key Achievements**", is a sub-heading.
                label = payload[0].replace("**", "").strip()
                if is_letter:  # subject / RE line in a letter
                    body.append(p_xml(run_xml(label, bold=True), "LetterBody"))
                else:
                    body.append(p_xml(run_xml(label), "SubHeading"))
                continue
            style = "LetterBody" if is_letter else None
            joined = '<w:r><w:br/></w:r>'.join(inline_runs(ln, final) for ln in payload)
            body.append(p_xml(joined, style))

    if footnotes and not final:
        body.append(p_xml(run_xml("Draft sources (removed in final)"), "Heading1"))
        for key, val in footnotes:
            body.append(p_xml(run_xml("[%s] " % key, bold=True) + inline_runs(val, False), "DraftNote"))

    sect = ('<w:sectPr><w:pgSz w:w="%d" w:h="%d"/><w:pgMar w:top="%d" w:right="%d" w:bottom="%d" '
            'w:left="%d" w:header="432" w:footer="432" w:gutter="0"/></w:sectPr>'
            % (pw, ph, margin, margin, margin, margin))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            "<w:body>%s%s</w:body></w:document>" % ("".join(body), sect))


def write_docx(path, document, styles, numbering, title, author, lang):
    now = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    files = {
        "[Content_Types].xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>""",
        "_rels/.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>""",
        "word/_rels/document.xml.rels": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>""",
        "word/settings.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:defaultTabStop w:val="720"/><w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat></w:settings>""",
        "docProps/core.xml": f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<dc:title>{escape(title)}</dc:title><dc:creator>{escape(author)}</dc:creator><dc:language>{escape(lang)}</dc:language>
<dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>""",
        "docProps/app.xml": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>career-consultant-skills</Application></Properties>""",
        "word/document.xml": document,
        "word/styles.xml": styles,
        "word/numbering.xml": numbering,
    }
    for name in ("word/document.xml", "word/styles.xml", "word/numbering.xml", "docProps/core.xml"):
        minidom.parseString(files[name].encode("utf-8"))  # raises if malformed
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)


def docx_text(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = re.findall(r"<w:p>(.*?)</w:p>", xml, flags=re.S)
    out = []
    for p in paras:
        p = p.replace("<w:tab/>", "\t").replace("<w:br/>", "\n")
        out.append(re.sub(r"<[^>]+>", "", p))
    import html
    return html.unescape("\n".join(out))


LANG_RE = re.compile(r"^[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*\Z")


class CliError(Exception):
    """A user-facing error: printed as 'Error: ...' with exit code 2."""


def same_path(a, b):
    try:
        return os.path.samefile(a, b)
    except OSError:
        return os.path.realpath(a) == os.path.realpath(b)


def read_input(path):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            return fh.read()
    except FileNotFoundError:
        raise CliError("input file not found: %s" % path)
    except IsADirectoryError:
        raise CliError("input is a directory, not a file: %s" % path)
    except UnicodeDecodeError:
        raise CliError("%s is not valid UTF-8 text. Re-save it as UTF-8 (in Word: Save As > Plain Text > UTF-8)." % path)
    except OSError as e:
        raise CliError("cannot read %s: %s" % (path, e.strerror or e))


# --------------------------------------------------------------------------- output-path guard
PROTECTED_DIRS = frozenset((".agents", ".kiro", ".claude", ".ssh", ".git"))
ALLOWED_EXT = {"-o": (".docx",), "--clean-md": (".md", ".txt")}


def _path_parts(p):
    return [c for c in re.split(r"[\\/]+", p) if c and c not in (".", "..")]


def _inside(root, path):
    try:
        return os.path.commonpath([os.path.normcase(root), os.path.normcase(path)]) == os.path.normcase(root)
    except ValueError:  # different drives
        return False


def allowed_root():
    """<cwd>/artifacts/output if that folder exists, else <cwd> (symlinks resolved)."""
    cwd = os.path.realpath(os.getcwd())
    out = os.path.join(cwd, "artifacts", "output")
    return os.path.realpath(out) if os.path.isdir(out) else cwd


def check_write_target(path, flag, allow_outside=False):
    """Validate a file this script is about to write. Returns the resolved path or raises CliError (exit 2).

    Refused always: wrong extension, symlinks, any folder named .agents/.kiro/.claude/.ssh/.git, artifacts/input,
    and any folder tree containing a SKILL.md. Refused unless --allow-outside: anything outside allowed_root().
    """
    if not path or "\x00" in path:
        raise CliError("%s needs a file path." % flag)
    absp = os.path.abspath(os.path.expanduser(path))
    exts = ALLOWED_EXT[flag]
    if os.path.splitext(absp)[1].lower() not in exts:
        raise CliError("refusing to write %s %r: the file name must end with %s." % (flag, path, " or ".join(exts)))
    if os.path.basename(absp).lower() == "skill.md":
        raise CliError("refusing to write %s %r: SKILL.md files are protected." % (flag, path))
    if os.path.islink(absp):
        raise CliError("refusing to write %s %r: it is a symbolic link. Choose a normal file path." % (flag, path))
    real = os.path.realpath(absp)
    for cand in (absp, real):
        parts = [c.lower() for c in _path_parts(cand)]
        bad = sorted(set(parts) & PROTECTED_DIRS)
        if bad:
            raise CliError("refusing to write %s %r: the path goes through protected folder %s." % (flag, path, bad[0]))
        if any(x == "artifacts" and y == "input" for x, y in zip(parts, parts[1:])):
            raise CliError("refusing to write %s %r: artifacts/input holds your source files and is never an output location." % (flag, path))
    d = os.path.dirname(real)
    while True:
        if os.path.exists(os.path.join(d, "SKILL.md")):
            raise CliError("refusing to write %s %r: %s belongs to a skill (it contains SKILL.md)." % (flag, path, d))
        up = os.path.dirname(d)
        if up == d:
            break
        d = up
    if os.path.isdir(real):
        raise CliError("%s %r is a directory; give a file name." % (flag, path))
    root = allowed_root()
    if not allow_outside and not _inside(root, real):
        raise CliError("refusing to write %s %r: it is outside the allowed output folder %s. "
                       "Write inside it, or pass --allow-outside if you really mean it "
                       "(protected folders stay blocked either way)." % (flag, path, root))
    if flag == "-o" and os.path.isfile(real):
        try:
            with open(real, "rb") as fh:
                head = fh.read(4)
        except OSError:
            head = b"PK\x03\x04"
        if head and head != b"PK\x03\x04":
            raise CliError("refusing to overwrite %r: it exists and is not a .docx file." % path)
    return real


def write_text(path, text, label):
    """Write UTF-8 text atomically (temp file in the same folder, then rename). `path` must already be guarded."""
    parent = os.path.dirname(path)
    tmp = None
    try:
        os.makedirs(parent, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        um = os.umask(0)
        os.umask(um)
        os.chmod(tmp, 0o666 & ~um)
        os.replace(tmp, path)
        tmp = None
    except OSError as e:
        raise CliError("cannot write %s %s: %s" % (label, path, e.strerror or e))
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)


EMAIL_RE = re.compile(r"(?<![\w.+-])[\w.+-]+@[\w-]+\.[\w.]+")


def run(a, ap):
    if a.list_templates:
        for k in sorted(THEMES):
            print("%-10s %s" % (k, THEMES[k]["label"]))
        return 0
    if not a.input or not a.output:
        ap.error("INPUT and -o OUTPUT are required")

    # Validate every path we will write BEFORE doing anything else.
    out_path = check_write_target(a.output, "-o", a.allow_outside)
    clean_path = check_write_target(a.clean_md, "--clean-md", a.allow_outside) if a.clean_md else None
    if same_path(a.input, out_path):
        raise CliError("output path is the same as the input file (%s); refusing to overwrite your source." % a.input)
    if clean_path and (same_path(a.input, clean_path) or same_path(out_path, clean_path)):
        raise CliError("--clean-md path must differ from the input file and the .docx output.")

    raw = read_input(a.input)
    raw, removed = sanitize_text(raw)
    if removed:
        sys.stderr.write("Warning: removed %d invisible or XML-invalid character(s) (zero-width, bidi/format, "
                         "control or tag characters) from the text. If this was not intended, re-check the source.\n" % removed)
    if not raw.strip():
        raise CliError("%s is empty; there is nothing to render." % a.input)
    meta, body, fm_state = split_frontmatter(raw)
    if fm_state == "unclosed":
        sys.stderr.write("Warning: the file starts with '---' but the front matter is never closed with a second '---'; "
                         "treating the whole file as body text.\n")
    theme = (a.template or meta.get("template", "modern")).strip().lower()
    if theme not in THEMES:
        raise CliError("unknown template %r; choose from %s" % (theme, ", ".join(sorted(THEMES))))
    page = (a.page or meta.get("page", "a4")).lower()
    if page not in PAGES:
        raise CliError("page must be a4 or letter")
    lang = a.lang or meta.get("lang", "en-GB")
    if not LANG_RE.match(lang):
        raise CliError("invalid language tag %r; use a BCP 47 tag such as en-GB, en-US or fr." % lang)

    # Comments (including multi-line ones) never reach the document, in draft or final.
    body = strip_html_comments(body)
    if "<!--" in body:
        sys.stderr.write("Warning: unterminated '<!--' comment; the text after it is NOT treated as a comment.\n")

    doc_key = meta.get("doc", "").lower()
    scan = ref_scan(body, doc_key)
    if not doc_key:
        doc_key = "references" if scan["looks_like"] else "cv"
    if a.clean_md and not a.final:
        raise CliError("--clean-md requires --final")

    if a.final:
        problems, n_refs, looks_like, why = referee_consent_problems(body, meta.get("doc", ""))
        if problems:
            sys.stderr.write("Refusing --final render of a reference sheet: referee consent is missing or invalid.\n")
            for pr in problems:
                sys.stderr.write("  - %s\n" % pr)
            sys.stderr.write("Ask each referee, then record '> Consent: confirmed [by email|phone|in person|message|"
                             "call|video] YYYY-MM-DD' under that referee. No output was written.\n")
            return 2
        body = clean_for_final(body)
        hits = find_placeholders(body)
        if hits and not a.allow_placeholders:
            sys.stderr.write("Refusing --final render: unfilled placeholders found:\n")
            for ln, h in hits[:30]:
                sys.stderr.write("  line %d: %s\n" % (ln, h))
            sys.stderr.write("Fill them in, or pass --allow-placeholders (not recommended: the file would contain template text).\n")
            return 2
        if hits and a.allow_placeholders:
            sys.stderr.write("WARNING: --allow-placeholders is set; %d placeholder(s) remain in the FINAL document "
                             "(e.g. %s). Do not send this file.\n" % (len(hits), hits[0][1]))

    blocks, footnotes = parse(body)
    if not blocks:
        raise CliError("nothing to render: %s has no text after removing front matter%s." % (
            a.input, ", notes and comments" if a.final else " and comments"))
    name = next((p for k, p in blocks if k == "name"), None)
    name_plain = inline_plain(name, a.final) if name is not None else None
    kind = next((label for prefix, label in DOC_LABELS if doc_key.startswith(prefix)), "Document")
    document = build_document(dict(meta, doc=doc_key), blocks, footnotes, theme, page, a.final)

    # Build into a temp file next to the target; only move it into place if the self-check passes.
    out_dir = os.path.dirname(out_path)
    tmp = None
    try:
        os.makedirs(out_dir, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=out_dir, suffix=".docx.tmp")
        os.close(fd)
        um = os.umask(0)
        os.umask(um)
        os.chmod(tmp, 0o666 & ~um)  # mkstemp creates 0600; a CV is meant to be shared
    except OSError as e:
        raise CliError("cannot write to output folder %s: %s" % (out_dir, e.strerror or e))
    try:
        write_docx(tmp, document, styles_xml(THEMES[theme], lang), numbering_xml(THEMES[theme]),
                   "%s - %s" % (name_plain, kind) if name_plain else kind, name_plain or "", lang)
        # Self-check: confirm the text survives in reading order.
        text = docx_text(tmp)
        problems = []
        if name_plain is not None and name_plain not in text:
            problems.append("name missing from body text")
        # Images are not embedded, so an "@2x" file name in ![alt](logo@2x.png) is not an e-mail address.
        text_only = re.sub(r"^!\[[^\]]*\]\([^)]*\)\s*$", "", body, flags=re.M)
        for email in EMAIL_RE.findall(text_only):
            if email not in text and email.rstrip(".") not in text:
                problems.append("email %s missing" % email)
        if problems:
            sys.stderr.write("Self-check problems: %s\nNo output file was written.\n" % "; ".join(problems))
            return 1
        os.replace(tmp, out_path)
        tmp = None
    except OSError as e:
        raise CliError("cannot write %s: %s" % (a.output, e.strerror or e))
    except ExpatError as e:
        raise CliError("could not build well-formed XML from this input (%s). Please report this file." % e)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    if clean_path:  # only after the self-check passed and the .docx is in place
        fm = "---\n" + "".join("%s: %s\n" % (k, v) for k, v in meta.items()) + "---\n\n" if meta else ""
        write_text(clean_path, fm + body, "--clean-md")
    words = len(re.findall(r"\b\w+\b", text))
    print("Wrote %s  (template=%s, page=%s, lang=%s, mode=%s, ~%d words)"
          % (a.output, theme, page, lang, "final" if a.final else "draft", words))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", nargs="?")
    ap.add_argument("-o", "--output", help="output .docx (must be inside the output folder; see 'Where files may be written')")
    ap.add_argument("--template", metavar="{%s}" % ",".join(sorted(THEMES)), help="visual template (see --list-templates)")
    ap.add_argument("--page", metavar="{a4,letter}", help="paper size (default a4)")
    ap.add_argument("--lang")
    ap.add_argument("--final", action="store_true", help="strip notes/citations; block on placeholders (and on missing referee consent)")
    ap.add_argument("--clean-md", help="also write the cleaned final Markdown (.md or .txt) to this path; requires --final")
    ap.add_argument("--allow-placeholders", action="store_true",
                    help="render --final even with placeholders (prints a loud warning)")
    ap.add_argument("--allow-outside", action="store_true",
                    help="allow -o/--clean-md outside <cwd>/artifacts/output (or <cwd> if that folder is absent). "
                         "Only lifts that root restriction: .agents/.kiro/.claude/.ssh/.git folders, artifacts/input, "
                         "SKILL.md trees, symlinks and wrong extensions are still refused")
    ap.add_argument("--list-templates", action="store_true")
    a = ap.parse_args(argv)
    try:
        return run(a, ap)
    except CliError as e:
        sys.stderr.write("Error: %s\n" % e)
        return 2


if __name__ == "__main__":
    sys.exit(main())
