#!/usr/bin/env python3
"""Mechanical checks for a CV or cover letter. Zero dependencies (stdlib only).

Usage:
  doc_lint.py FILE [--type cv|letter] [--job JOB_AD.txt] [--json] [--strict]
  doc_lint.py FILE --text          print the plain text of FILE and exit 0 (no metrics)

FILE may be .md, .txt or .docx (PDF/.doc: convert or extract text first, e.g. `pdftotext -layout`).
The linter only measures; it never judges fit or quality on its own. Use its output
as evidence inside the reviewer rubric, not as the review itself.

Also reports hidden-content signals (hidden or white/tiny text, invisible Unicode, text that addresses
an AI reader). They are warnings to investigate, not proof of intent. With --strict, any warning or
placeholder makes the exit code 1 (default exit code is 0).

--text prints the readable text of a .md, .txt or .docx file so you can read a Word document without other tools:
paragraphs are separated by blank lines, headings carry Markdown "#" markers and list items "- ". Hidden
(w:vanish) runs, tracked deletions, comments and invisible Unicode are NOT printed (a note on stderr says how many
were left out); header/footer text is appended under a label. It prints no metrics and exits 0.
On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import collections
import io
import json
import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile
import zlib

MAX_DOCX_BYTES = 20 * 1024 * 1024  # total uncompressed size we are willing to read from a .docx
MAX_XML_ELEMENTS = 1000000        # cap on XML elements parsed from one .docx

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


def fail(msg):
    sys.stderr.write("Error: %s\n" % msg)
    raise SystemExit(2)


def read_plain(path, what="file"):
    """Read a UTF-8 (BOM tolerated) text file; exit 2 with a friendly message on any I/O problem."""
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except FileNotFoundError:
        fail("%s not found: %s" % (what, path))
    except IsADirectoryError:
        fail("%s is a directory, not a file." % path)
    except OSError as e:
        fail("cannot read %s %s: %s" % (what, path, e.strerror or e))
    if raw.startswith(b"%PDF"):
        fail("%s is a PDF. Extract text first (for example `pdftotext -layout file.pdf out.txt`) and lint that." % path)
    if raw.startswith(b"PK\x03\x04"):
        fail("%s looks like a zip/Office file but is not named .docx. Rename it to .docx or export to .md/.txt." % path)
    if raw.startswith(b"\xd0\xcf\x11\xe0"):
        fail("%s is a legacy .doc file. Save it as .docx (or .txt) and lint that." % path)
    if b"\x00" in raw[:4096]:
        fail("%s looks like a binary file. doc_lint reads .docx, .md and .txt only." % path)
    try:
        return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except UnicodeDecodeError:
        fail("%s is not valid UTF-8 text. Re-save it as UTF-8." % path)


CLICHES = [
    "team player", "hard-working", "hardworking", "results-driven", "results-oriented",
    "detail-oriented", "go-getter", "self-starter", "think outside the box", "synergy",
    "dynamic", "passionate about", "proven track record", "excellent communication skills",
    "strong work ethic", "fast learner", "quick learner", "highly motivated", "best of breed",
    "go-to person", "people person", "track record of success", "wear many hats",
    "seasoned professional", "thought leader", "rockstar", "ninja", "guru",
    "at all levels", "value-add", "value add", "rapidly changing", "to whom it may concern",
    "i am writing to apply", "i am writing to express", "it is with great enthusiasm",
    "please find attached", "perfect fit", "ideal candidate",
]
WEAK_OPENERS = [
    "responsible for", "duties included", "duties include", "tasked with", "worked on",
    "helped", "assisted with", "involved in", "participated in", "successfully",
    "in charge of", "handled", "played a key role", "played a pivotal role", "instrumental in",
]
PERSONAL_DATA = {
    "date of birth / age": r"\b(date of birth|d\.?o\.?b\.?|born on|age:\s*\d{2})\b",
    "marital status": r"\b(marital status|civil status)\b|\b(married|divorced|widowed)\b",
    "religion": r"\breligion\s*:",
    "gender": r"\b(gender|sex)\s*:",
    "national ID": r"\b(nric|ssn|social security( number)?|passport (no|number)|national id)\b",
    "photo reference": r"\b(photo|photograph)\s*:",
    "salary": r"\b(expected salary|current salary|salary expectation)\b",
}
US_UK = [("organization", "organisation"), ("optimize", "optimise"), ("analyze", "analyse"),
         ("color", "colour"), ("center", "centre"),
         ("behavior", "behaviour"), ("modeling", "modelling"),
         ("prioritize", "prioritise"), ("realize", "realise"), ("specialize", "specialise"),
         ("recognize", "recognise"), ("utilize", "utilise"), ("traveled", "travelled")]
# ("license"/"licence" is deliberately absent: UK English uses "license" as the verb, "licence" as the noun.)


def spelling_regex(word):
    """Whole-word regex for a spelling variant, allowing common inflections (colour/colours, optimise/optimised)."""
    if word.endswith(("ize", "ise", "yze", "yse")):
        return re.compile(r"\b" + re.escape(word[:-1]) + r"(?:e|es|ed|er|ers|ing|ation|ations)\b")
    return re.compile(r"\b" + re.escape(word) + r"(?:s|es|ed|ing|ers?)?\b")


US_UK_RE = [(u, spelling_regex(u), b, spelling_regex(b)) for u, b in US_UK]

# --------------------------------------------------------------------------- placeholders
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


METRIC = re.compile(r"(\d|%|\$|€|£|¥|₹|\bpercent\b|\bmillion\b|\bbillion\b|\bthousand\b|\b\d+[kKmMbB]\b|\bx\d|\d+x\b)")
DATE_RANGE = re.compile(
    r"\b((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+)?((?:19|20)\d{2})\s*[-–—to]+\s*"
    r"((?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*\.?\s+)?((?:19|20)\d{2}|present|current|now)",
    re.I)
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


def _read_member(z, name, budget):
    """Read one zip member, never more than `budget` bytes (guards against zip bombs)."""
    with z.open(name) as fh:
        data = fh.read(budget + 1)
    if len(data) > budget:
        fail("the .docx expands to more than %d MB; refusing to read it." % (MAX_DOCX_BYTES // (1024 * 1024)))
    return data


_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_LIGHT_THEME = frozenset(("background1", "bg1", "window", "light1", "lt1"))
_PR_CHANGE = frozenset(("rPrChange", "pPrChange", "sectPrChange", "tblPrChange", "tcPrChange", "trPrChange",
                        "tblPrExChange", "tblGridChange", "numberingChange"))


def _toggle_on(el):
    return (el.get(_W + "val") or "true").strip().lower() not in ("0", "false", "off")


def _is_near_white(hexval):
    """True for colours at or above #F8F8F8 on every channel."""
    h = (hexval or "").strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return False
    try:
        return min(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)) >= 0xF8
    except ValueError:
        return False


def _light_colour(el):
    """White, near-white (>= #F8F8F8) or light theme colour (background1, bg1, window) in a w:color element."""
    if _is_near_white(el.get(_W + "val")):
        return True
    theme = (el.get(_W + "themeColor") or "").lower()
    if theme in _LIGHT_THEME:
        shade = el.get(_W + "themeShade")
        if shade:
            try:
                return int(shade, 16) >= 0xF8
            except ValueError:
                return False
        return True
    return False


def _check_xml_bytes(data):
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
        fail("a part of this .docx declares a DTD or XML entities, which Word never writes; refusing to read it.")


def hidden_style_ids(data):
    """Style ids (from word/styles.xml) whose run properties hide the text (w:vanish)."""
    _check_xml_bytes(data)
    ids, cur, n = set(), None, 0
    try:
        for ev, el in ET.iterparse(io.BytesIO(data), events=("start",)):
            n += 1
            if n > MAX_XML_ELEMENTS:
                break
            if el.tag == _W + "style":
                cur = el.get(_W + "styleId")
            elif el.tag in (_W + "vanish", _W + "webHidden") and cur and _toggle_on(el):
                ids.add(cur)
    except ET.ParseError:
        pass
    return ids


def walk_docx_xml(data, hidden_styles=()):
    """Stream through one WordprocessingML part in linear time (capped at MAX_XML_ELEMENTS elements).

    Returns paragraphs (visible text), text of hidden / tracked-deleted runs and counts of hidden, white or tiny runs.
    """
    _check_xml_bytes(data)
    res = {"paras": [], "hidden": 0, "tiny": 0, "hidden_samples": [], "tiny_samples": [], "hidden_text": [],
           "deleted": [], "tables": False, "text_boxes": False}
    pstack, rstack = [], []
    in_ppr = in_rpr = in_change = n = 0
    try:
        for ev, el in ET.iterparse(io.BytesIO(data), events=("start", "end")):
            n += 1
            if n > 2 * MAX_XML_ELEMENTS:
                fail("the .docx has more than %d XML elements; refusing to read it." % MAX_XML_ELEMENTS)
            tag = el.tag
            if not isinstance(tag, str) or not tag.startswith(_W):
                continue
            t = tag[len(_W):]
            if ev == "start":
                if t == "p":
                    pstack.append({"parts": [], "style": ""})
                elif t == "r":
                    rstack.append({"parts": [], "hidden": False, "light": False, "sz": None, "style": ""})
                elif t == "pPr":
                    in_ppr += 1
                elif t == "rPr":
                    in_rpr += 1
                elif t in _PR_CHANGE:
                    in_change += 1
                elif t == "tbl":
                    res["tables"] = True
                elif t == "txbxContent":
                    res["text_boxes"] = True
                elif t == "pStyle" and pstack:
                    pstack[-1]["style"] = el.get(_W + "val") or ""
                elif in_rpr and rstack and not in_ppr and not in_change:
                    run = rstack[-1]
                    if t in ("vanish", "webHidden"):
                        run["hidden"] = run["hidden"] or _toggle_on(el)
                    elif t == "color":
                        run["light"] = run["light"] or _light_colour(el)
                    elif t == "sz":
                        try:
                            run["sz"] = int(el.get(_W + "val"))
                        except (TypeError, ValueError):
                            pass
                    elif t == "rStyle":
                        run["style"] = el.get(_W + "val") or ""
                continue
            # ev == "end"
            if t == "t":
                if rstack:
                    rstack[-1]["parts"].append(el.text or "")
                elif pstack:
                    pstack[-1]["parts"].append(el.text or "")
            elif t == "delText":
                res["deleted"].append(el.text or "")
            elif t in ("tab", "br", "cr") and rstack and not in_ppr and not in_rpr:
                rstack[-1]["parts"].append("\t" if t == "tab" else "\n")
            elif t == "r" and rstack:
                run = rstack.pop()
                txt = "".join(run["parts"])
                pstyle = pstack[-1]["style"] if pstack else ""
                hid = run["hidden"] or (run["style"] in hidden_styles) or (pstyle in hidden_styles and bool(pstyle))
                if txt.strip():
                    tiny = run["light"] or (run["sz"] is not None and run["sz"] < 14)
                    if hid:
                        res["hidden"] += 1
                        res["hidden_text"].append(txt)
                        if len(res["hidden_samples"]) < 3:
                            res["hidden_samples"].append(txt.strip()[:60])
                    elif tiny:
                        res["tiny"] += 1
                        if len(res["tiny_samples"]) < 3:
                            res["tiny_samples"].append(txt.strip()[:60])
                if not hid and pstack:
                    pstack[-1]["parts"].append(txt)
            elif t == "p" and pstack:
                p = pstack.pop()
                txt = "".join(p["parts"])
                if txt.strip():
                    res["paras"].append((p["style"], txt))
            elif t == "pPr":
                in_ppr -= 1
            elif t == "rPr":
                in_rpr -= 1
            elif t in _PR_CHANGE:
                in_change -= 1
            el.clear()
    except ET.ParseError:
        raise ValueError("unreadable XML")
    return res


def _style_prefix(style):
    s = re.sub(r"[\s_-]+", "", style or "").lower()
    if s == "title":
        return "# "
    m = re.fullmatch(r"heading([1-6])", s)
    if m:
        return "#" * (int(m.group(1)) + 1) + " "
    return "- " if "list" in s else ""


def read_text(path):
    if path.lower().endswith(".docx"):
        try:
            z = zipfile.ZipFile(path)
        except FileNotFoundError:
            fail("file not found: %s" % path)
        except IsADirectoryError:
            fail("%s is a directory, not a file." % path)
        except zipfile.BadZipFile:
            try:
                with open(path, "rb") as fh:
                    if fh.read(4) == b"%PDF":
                        fail("%s is a PDF, not a .docx. Extract text first (for example `pdftotext -layout`)." % path)
            except OSError:
                pass
            fail("%s is not a valid .docx (corrupt, or an old .doc renamed). Re-save it as .docx from Word." % path)
        except OSError as e:
            fail("cannot read %s: %s" % (path, e.strerror or e))
        with z:
            infos = z.infolist()
            if sum(i.file_size for i in infos) > MAX_DOCX_BYTES:
                fail("the .docx expands to more than %d MB; refusing to read it." % (MAX_DOCX_BYTES // (1024 * 1024)))
            names = [i.filename for i in infos]
            if "word/document.xml" not in names:
                fail("%s has no word/document.xml; it is not a Word document." % path)
            budget = MAX_DOCX_BYTES
            try:
                doc_bytes = _read_member(z, "word/document.xml", budget)
                budget -= len(doc_bytes)
                hidden_styles = set()
                if "word/styles.xml" in names and budget > 0:
                    sb = _read_member(z, "word/styles.xml", budget)
                    budget -= len(sb)
                    hidden_styles = hidden_style_ids(sb)
                extra_parts = []
                for n in names:
                    if budget > 0 and re.match(r"word/(header|footer|comments)\d*\.xml\Z", n):
                        pb = _read_member(z, n, budget)
                        budget -= len(pb)
                        extra_parts.append((n, pb))
            except (zipfile.BadZipFile, zlib.error):
                fail("%s contains unreadable XML parts; it may be corrupt." % path)
        try:
            main = walk_docx_xml(doc_bytes, hidden_styles)
            header_text, comment_text, hid_extra = [], [], []
            hidden, tiny = main["hidden"], main["tiny"]
            samples, tiny_samples = list(main["hidden_samples"]), list(main["tiny_samples"])
            deleted = list(main["deleted"])
            for n, pb in extra_parts:
                part = walk_docx_xml(pb, hidden_styles)
                body = " ".join(t for _, t in part["paras"])
                (comment_text if "/comments" in n else header_text).append(body)
                hidden += part["hidden"]
                tiny += part["tiny"]
                samples += part["hidden_samples"][:max(0, 3 - len(samples))]
                tiny_samples += part["tiny_samples"][:max(0, 3 - len(tiny_samples))]
                hid_extra += part["hidden_text"]
                deleted += part["deleted"]
        except ValueError:
            fail("%s contains unreadable XML parts; it may be corrupt." % path)
        lines = []
        for style, txt in main["paras"]:
            pre = _style_prefix(style)
            lines.append(pre + txt.strip() if pre else txt.strip())
        media = [n for n in names if n.startswith("word/media/")]
        hf = " ".join(x for x in header_text if x.strip()).strip()
        comments = " ".join(x for x in comment_text if x.strip()).strip()
        deleted_words = len(re.findall(r"\S+", " ".join(deleted)))
        extra = "\n".join(main["hidden_text"] + hid_extra + deleted + ([comments] if comments else []))
        info = {"tables": main["tables"], "text_boxes": main["text_boxes"],
                "header_footer_text": hf[:120], "images": len(media),
                "_hidden_runs": hidden, "_tiny_or_white_runs": tiny, "_hidden_samples": samples,
                "_tiny_samples": tiny_samples, "_deleted_words": deleted_words,
                "_comment_words": len(comments.split()), "_extra_text": extra, "_header_footer_full": hf[:2000]}
        return "\n\n".join(lines), info
    return read_plain(path), {}


def strip_md(text):
    """Body of a Markdown document: front matter and HTML comments removed (CRLF-safe, linear time)."""
    return strip_html_comments(split_front_matter(text)[1])


def bullets(text):
    return [re.sub(r"^\s*[-*+•]\s+", "", l).strip() for l in text.splitlines() if re.match(r"^\s*[-*+•]\s+", l)]


def month_index(mon, year):
    m = MONTHS.get((mon or "jan").strip().lower()[:3], 1)
    return int(year) * 12 + m


def date_checks(text):
    ranges = []
    for m in DATE_RANGE.finditer(text):
        sm, sy, em, ey = m.groups()
        start = month_index(sm, sy)
        if ey.lower() in ("present", "current", "now"):
            end = 10 ** 6
        else:
            end = month_index(em or "dec", ey)
        ranges.append((m.group(0), start, end))
    issues = [r[0] for r in ranges if r[2] < r[1]]
    styles = set()
    for r in ranges:
        s = r[0]
        styles.add(("month" if re.match(r"[A-Za-z]", s) else "year") + ("–" if "–" in s else "—" if "—" in s else "-" if "-" in s else "to"))
    return {"date_ranges_found": len(ranges), "end_before_start": issues,
            "date_formats_used": sorted(styles), "mixed_date_formats": len(styles) > 1}


MISSING_NOTE = "Missing terms: add only if true of the candidate; coverage is information, not a target."


def keywords(job_text, doc_text, top=25):
    stop = set("""a an the and or for to of in on at by with from as is are be will you your our we this that
    it its their they who what which role job team work working experience years year ability strong
    skills skill including include etc must should can able new across within more other such per
    candidate company about all any has have help helps well looking based plus nice also us part join get
    make using use used best great good high level knowledge understanding excellent responsible
    responsibilities requirements required preferred qualifications position opportunity need needs want
    ideal ideally between over under into out up one two three own run days day today office hybrid remote
    partner report weekly senior junior lead manager apply send cover letter short close closes applications
    benefits offer pension holiday health competitive salary learning budget markets european proven running
    familiarity exposure right ref fictional example resemblance coincidental figures names reuse small
    fast-paced ambitious""".split())
    clean_job = "\n".join(l for l in strip_md(job_text).splitlines() if not l.lstrip().startswith(">"))
    raw_toks = [w.strip(".-/") for w in re.findall(r"[a-zA-Z][a-zA-Z+#./-]{2,}", clean_job.lower())]
    toks = [w for w in raw_toks if len(w) > 2 and w not in stop]
    bigr = collections.Counter(" ".join(p) for p in zip(toks, toks[1:]))
    counts = collections.Counter(toks) + collections.Counter({b: c for b, c in bigr.items() if c > 1})
    terms = [t for t, _ in counts.most_common(top * 2)][:top]
    low = doc_text.lower()
    present = [t for t in terms if t in low]
    missing = [t for t in terms if t not in low]
    return {"job_terms_checked": len(terms), "present": present, "missing": missing,
            "coverage_pct": round(100 * len(present) / max(1, len(terms))),
            "missing_terms_note": MISSING_NOTE}


SUSPICIOUS = [
    re.compile(r"\b(?:ignore|disregard|forget|override)\s+(?:(?:all|any|every|the|your|these|those|my)\s+){0,2}"
               r"(?:(?:previous|prior|above|earlier|preceding|former|system|original)\s+){1,2}"
               r"(?:instructions?|prompts?|rules|directions?|criteria|guidelines?|context)", re.I),
    re.compile(r"\b(?:ignore|disregard)\s+(?:all|any|every)\s+(?:instructions?|rules|criteria)\b", re.I),
    re.compile(r"\bignore\s+(?:all|any|every|previous|prior|above|the above|earlier)\b[^.\n]{0,40}\binstructions?", re.I),
    re.compile(r"\bdisregard\s+(?:all|any|the|previous|prior|above)\b[^.\n]{0,40}\b(?:instructions?|rules|criteria)", re.I),
    re.compile(r"\bforget\s+(?:everything|all|anything)\s+(?:above|before|previously|prior|you\s+(?:know|were\s+told))", re.I),
    re.compile(r"\bdisregard\s+(?:the|all|any)\s+(?:previous|prior|above|earlier|preceding)\b", re.I),
    re.compile(r"\bnew\s+instructions?\s*:", re.I),
    re.compile(r"\byou\s+must\s+(?:rank|recommend|score|rate|select|hire|shortlist|advance)\b", re.I),
    re.compile(r"\bsystem prompt\b", re.I),
    re.compile(r"\brank this candidate\b|\b(?:recommend|hire|select|shortlist|advance) this candidate\b", re.I),
    re.compile(r"\byou are an? (?:ai|a\.i\.|assistant|llm|language model|chatbot)\b", re.I),
    re.compile(r"\b(?:top|highest|best)[- ](?:rank|ranked|score|scoring)\b[^.\n]{0,30}\bcandidate", re.I),
]


def invisible_count(text):
    """Number of invisible/format characters, using exactly the set that render_docx.py removes."""
    return sanitize_text(text)[1]


def hidden_content(raw_text, docx_info):
    """Signals that content may be invisible to a human reader. Returns (fields, warnings)."""
    info = docx_info or {}
    hidden = info.get("_hidden_runs", 0)
    tiny = info.get("_tiny_or_white_runs", 0)
    comments = [c for c in html_comments(raw_text) if c.strip()]
    css_hidden = re.findall(r"(?:display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0|color\s*:\s*(?:#?f{3,6}|white)\b)",
                            raw_text, flags=re.I)
    if not docx_info:
        hidden += len(comments) + len(css_hidden)
    extra = info.get("_extra_text", "")                        # hidden runs, tracked deletions, comments (.docx)
    scan = raw_text + "\n" + extra if extra else raw_text
    inv = invisible_count(scan)
    phrases = sorted({" ".join(m.group(0).split()).lower() for rx in SUSPICIOUS for m in rx.finditer(scan)})
    deleted = info.get("_deleted_words", 0)
    fields = {"hidden_text": hidden, "tiny_or_white_text": tiny, "deleted_text": deleted, "invisible_unicode": inv,
              "suspicious_phrases": phrases}
    warnings = []
    if hidden:
        what = "hidden (w:vanish) runs" if docx_info else "HTML comment(s) / hidden-style markup"
        extra = " e.g. %s" % "; ".join(repr(x) for x in info.get("_hidden_samples", [])) if info.get("_hidden_samples") else ""
        warnings.append("hidden_text: %d %s.%s Text a human cannot see can still be read by software." % (hidden, what, extra))
    if tiny:
        extra = " e.g. %s." % "; ".join(repr(x) for x in info.get("_tiny_samples", [])) if info.get("_tiny_samples") else ""
        warnings.append("tiny_or_white_text: %d run(s) are white, near-white (>= #F8F8F8, or a light theme colour) or smaller than 7 pt.%s Check they are not hiding keywords." % (tiny, extra))
    if deleted:
        warnings.append("deleted_text: %d word(s) of tracked deletions are still stored in the file and can be recovered. Accept all changes before sending." % deleted)
    if info.get("_comment_words"):
        warnings.append("comments: the .docx holds %d word(s) of review comments. Remove them before sending." % info["_comment_words"])
    if inv:
        warnings.append("invisible_unicode: %d invisible/format character(s) (zero-width, bidi controls, tag characters)." % inv)
    if phrases:
        warnings.append("suspicious_phrases: text that addresses an automated reader: %s" % "; ".join(repr(p) for p in phrases[:5]))
    if docx_info and docx_info.get("text_boxes"):
        warnings.append("text_boxes: text boxes are often skipped or scrambled by applicant tracking systems.")
    if docx_info and docx_info.get("tables"):
        warnings.append("tables: tables can be parsed out of order by applicant tracking systems.")
    return fields, warnings


def lint(text, doc_type, job=None, docx_info=None):
    body = strip_md(text)
    low = body.lower()
    words = re.findall(r"\b[\w'’-]+\b", body)
    wc = len(words)
    blts = bullets(body)
    r = {"type": doc_type, "word_count": wc}

    r["placeholders"] = sorted(set(h for _, h in placeholder_hits(body)))
    r["citation_markers_left"] = len(re.findall(r"\[\^[^\]]{1,100}\]", body))
    r["draft_notes_left"] = len([l for l in body.splitlines() if l.lstrip().startswith(">")])
    r["cliches"] = sorted({c for c in CLICHES if c in low})
    r["personal_data_flags"] = sorted(k for k, rx in PERSONAL_DATA.items() if re.search(rx, low))
    us = [u for u, urx, b, brx in US_UK_RE if urx.search(low)]
    uk = [b for u, urx, b, brx in US_UK_RE if brx.search(low)]
    r["spelling"] = {"us_forms": us, "uk_forms": uk, "mixed": bool(us and uk)}
    r["emails"] = sorted(set(e.rstrip(".") for e in re.findall(r"(?<![\w.+-])[\w.+-]+@[\w-]+\.[\w.]+", body)))
    r["phones"] = sorted(set(
        p.strip() for p in re.findall(r"\+?\d[\d ()-]{7,}\d", body)
        if len(re.sub(r"\D", "", p)) >= 8 and not re.fullmatch(r"\s*(19|20)\d{2}\s*[-–]\s*(19|20)\d{2}\s*", p)
        and not re.fullmatch(r"\s*\d{4}-\d{2}(?:-\d{2})?(?:\s*[-–]\s*\d{4}-\d{2}(?:-\d{2})?)?\s*", p)))
    if docx_info:
        r["docx_layout"] = {k: v for k, v in docx_info.items() if not k.startswith("_")}

    if doc_type == "cv":
        quant = [b for b in blts if METRIC.search(b)]
        weak = [b for b in blts if any(b.lower().startswith(w) for w in WEAK_OPENERS)]
        long_b = [b for b in blts if len(b.split()) > 40]
        first_person = re.findall(r"\b(I|me|my)\b", body)
        r.update({
            "bullets": len(blts),
            "bullets_with_metric": len(quant),
            "metric_ratio_pct": round(100 * len(quant) / max(1, len(blts))),
            "weak_opener_bullets": weak[:15],
            "bullets_over_40_words": long_b[:10],
            "first_person_pronouns": len(first_person),
            "est_pages": round(wc / 450, 1),
            "repeated_bullet_openers": [w for w, c in collections.Counter(
                b.split()[0].lower() for b in blts if b.split()).most_common(5) if c >= 4],
        })
        r.update(date_checks(body))
        heads = [h.strip().lower() for h in re.findall(r"^#{2}\s+(.+)$", body, flags=re.M)]
        r["sections"] = heads
        r["references_line"] = bool(re.search(r"references (are )?available (up)?on request", low))
    else:
        sal = re.search(r"^\s*(dear|hello|hi)\b.*$", body, flags=re.I | re.M)
        so = None
        for so in re.finditer(r"^\s*(sincerely|yours sincerely|yours faithfully|kind regards|best regards|regards|respectfully|best wishes|thank you),?\s*$", body, flags=re.I | re.M):
            pass
        core = body[sal.end() if sal else 0: so.start() if so else len(body)]
        core = "\n".join(l for l in core.splitlines() if not l.lstrip().startswith((">", "[^")))
        paras = [p for p in re.split(r"\n\s*\n", core) if p.strip()]
        wc = len(re.findall(r"\b[\w'’-]+\b", core))
        r["body_word_count"] = wc
        i_count = len(re.findall(r"\bI\b", body))
        you_count = len(re.findall(r"\b(you|your|yours)\b", low))
        sentences = re.split(r"(?<=[.!?])\s+", body)
        r.update({
            "paragraphs": len(paras),
            "i_count": i_count,
            "you_your_count": you_count,
            "i_to_you_ratio": round(i_count / max(1, you_count), 1),
            "sentences_starting_with_I": sum(1 for s in sentences if s.strip().startswith("I ")),
            "has_salutation": bool(re.search(r"^\s*(dear|hello|hi)\b", body, flags=re.I | re.M)),
            "generic_salutation": bool(re.search(r"to whom it may concern|dear sir or madam|dear sir/madam", low)),
            "has_signoff": bool(re.search(r"(sincerely|regards|faithfully|respectfully|best wishes|thank you),?\s*$", body, flags=re.I | re.M)),
            "numbers_in_letter": len(re.findall(r"(?<![\w.])[$€£¥₹]?\d[\d,.]*\s?(%|k|m|bn|x|percent)?(?![\w])", core, flags=re.I)),
            "length_band": "short" if wc < 200 else "ideal" if wc <= 400 else "long" if wc <= 500 else "too long",
        })
        if re.search(r"yours faithfully", low) and re.search(r"dear (mr|ms|mrs|mx|dr|prof)\.?\s+\w", low):
            r["signoff_mismatch"] = "'Yours faithfully' used with a named recipient (UK convention: 'Yours sincerely')"
    if job:
        r["keyword_match"] = keywords(job, body)
    fields, warnings = hidden_content(text, docx_info)
    r.update(fields)
    r["warnings"] = warnings
    return r


def to_text(r):
    out = []
    for k, v in r.items():
        if k == "warnings" or (isinstance(v, (list, dict)) and not v):
            continue
        out.append("%-26s %s" % (k + ":", json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v))
        if k == "keyword_match":
            out.append("%-26s %d%% coverage. %s" % ("", v["coverage_pct"], MISSING_NOTE))
    for w in r.get("warnings", []):
        out.append("WARNING: " + w)
    return "\n".join(out)


def print_text(text, info):
    """--text: readable text only, invisible characters removed, no metrics. Exit code 0."""
    clean, removed = sanitize_text(text)
    out = clean.rstrip() + "\n"
    hf = (info or {}).get("_header_footer_full", "")
    if hf:
        out += "\n[Header/footer text]\n" + sanitize_text(hf)[0] + "\n"
    if getattr(sys.stdout, "buffer", None) is not None:
        sys.stdout.buffer.write(out.encode("utf-8"))      # UTF-8 on every console, including Windows
    else:
        sys.stdout.write(out)
    sys.stdout.flush()
    notes = []
    if removed:
        notes.append("%d invisible character(s)" % removed)
    if info:
        if info.get("_hidden_runs"):
            notes.append("%d hidden (w:vanish) run(s)" % info["_hidden_runs"])
        if info.get("_deleted_words"):
            notes.append("%d word(s) of tracked deletions" % info["_deleted_words"])
        if info.get("_comment_words"):
            notes.append("%d word(s) of comments" % info["_comment_words"])
    if notes:
        sys.stderr.write("Note: left out of the text above: %s. Run without --text for the full hidden-content report.\n"
                         % ", ".join(notes))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--type", choices=["cv", "letter"])
    ap.add_argument("--job", help="job ad text file for keyword coverage")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if there are any warnings (hidden content, ...) or placeholders")
    ap.add_argument("--text", action="store_true",
                    help="print the plain text of FILE (.md, .txt or .docx) and exit 0, without metrics")
    a = ap.parse_args(argv)
    text, info = read_text(a.file)
    if a.text:
        return print_text(text, info)
    doc_type = a.type
    if not doc_type:
        doc_type = "letter" if re.search(r"^\s*dear\b", text, flags=re.I | re.M) or split_front_matter(text)[0].get("doc", "").lower().startswith(("cover", "letter")) else "cv"
    job = read_plain(a.job, "job ad file") if a.job else None
    r = lint(text, doc_type, job, info)
    print(json.dumps(r, indent=2, ensure_ascii=False) if a.json else to_text(r))
    if a.json and r["warnings"]:
        for w in r["warnings"]:
            sys.stderr.write("WARNING: %s\n" % w)
    if a.strict and (r["warnings"] or r["placeholders"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
