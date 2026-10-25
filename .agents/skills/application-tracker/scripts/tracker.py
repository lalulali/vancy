#!/usr/bin/env python3
"""Job application tracker backed by one CSV file. Zero dependencies (stdlib only).

The CSV opens in Excel, Numbers and Google Sheets, so the user can also edit it by hand.
It contains personal job-search data: keep it local and do not commit or share it.

Usage:
  tracker.py [--file FILE.csv] COMMAND ...

Default file (when --file is not given): artifacts/output/job-applications.csv if the folder
artifacts/output exists in the current directory (project convention: read artifacts/input, write
artifacts/output), otherwise job-applications.csv in the current directory.

Commands:
  init                                   create the file (and parent folders) with the header row
  add     --company C --role R [--location L] [--url U] [--ad FILE] [--applied YYYY-MM-DD]
          [--cv NAME] [--letter NAME] [--status S] [--next TEXT] [--next-date YYYY-MM-DD]
          [--contact TEXT] [--pay TEXT] [--note TEXT]
  update  ID [--status S] [--next TEXT] [--next-date YYYY-MM-DD] [--note TEXT] [--contact TEXT]
          [--pay TEXT] [--cv NAME] [--letter NAME] [--applied YYYY-MM-DD]
  list    [--status S[,S]] [--active] [--company TEXT]
  due     [--days N] [--follow-up-days N]  what needs action now or soon
  stats                                   funnel counts and response rates
  show    ID                              all fields of one application
  export  [--out FILE.md|FILE.csv]        Markdown table
  delete  ID --yes

Global options (put them before the command):
  --file FILE.csv    the tracker file
  --allow-outside    let --file / export --out point outside the allowed folder (see Safety). It never lifts
                     the protected-path refusals.

Statuses: wishlist, preparing, applied, screening, interviewing, assessment, offer, negotiating,
          accepted, rejected, withdrawn, ghosted
Test hook: --today YYYY-MM-DD overrides today's date.

Safety: the CSV is private to you (mode 0600). Cells that start with = + - @ TAB or CR are stored with a
leading single quote so spreadsheets cannot run them as formulas; the quote is removed again when read.
Dates in the file are read as ISO (YYYY-MM-DD); d/m/Y or m/d/Y only when unambiguous, otherwise the row is
skipped with a warning. Excel's BOM and short rows are handled.
Path safety: --file and export --out must resolve (realpath) inside artifacts/output when that folder exists,
otherwise inside the current folder; anything else is refused with exit 2 unless --allow-outside is given. These
are always refused, with or without --allow-outside: a path with a folder named .agents .kiro .claude .ssh or .git,
artifacts/input, any folder that holds a SKILL.md, or an existing symlink. --file must end in .csv; --out must end
in .md or .csv, and may never overwrite the tracker file or any existing .csv file.
Writes are serialised with a lock file (<file>.lock) and replace the CSV atomically.
On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import contextlib
import csv
import datetime as dt
import fnmatch
import os
import re
import statistics
import sys
import tempfile
import time

STATUSES = ["wishlist", "preparing", "applied", "screening", "interviewing", "assessment",
            "offer", "negotiating", "accepted", "rejected", "withdrawn", "ghosted"]
ACTIVE = {"wishlist", "preparing", "applied", "screening", "interviewing", "assessment", "offer", "negotiating"}
RESPONDED = {"screening", "interviewing", "assessment", "offer", "negotiating", "accepted", "rejected"}
FIELDS = ["id", "company", "role", "location", "url", "ad_file", "applied_date", "cv_version", "letter_version",
          "status", "first_response_date", "next_action", "next_action_date", "contact", "pay", "notes", "last_updated"]
DEFAULT_FILE = "job-applications.csv"


def fail(msg):
    sys.stderr.write("Error: %s\n" % msg)
    raise SystemExit(2)


def today(args):
    if getattr(args, "today", None):
        return parse_date(args.today, "--today")
    return dt.date.today()


ISO_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$")


def parse_date(s, label="date"):
    """Strict YYYY-MM-DD (same behaviour on every Python version; no 20240115 or week dates)."""
    m = ISO_RE.match((s or "").strip())
    if m:
        try:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass
    fail("%s must be a real date in YYYY-MM-DD form, got %r" % (label, s))


def tolerant_date(s):
    """Date from a cell that may have been edited in a spreadsheet. ISO always; d/m/Y or m/d/Y only if
    unambiguous. Returns None when it cannot be read safely."""
    s = (s or "").strip()
    if not s:
        return None
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})(?:[ T].*)?$", s)
    try:
        if m:
            return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        m = re.match(r"^(\d{1,2})[/.-](\d{1,2})[/.-](\d{4})$", s)
        if m:
            a, b, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a > 12 and b <= 12:
                return dt.date(y, b, a)       # d/m/Y
            if b > 12 and a <= 12:
                return dt.date(y, a, b)       # m/d/Y
            if a == b and a <= 12:
                return dt.date(y, a, b)
    except ValueError:
        return None
    return None


_warned = set()


def row_date(r, field):
    """Read a date cell; warn once and return None if it cannot be read."""
    v = r.get(field, "")
    if not v:
        return None
    d = tolerant_date(v)
    if d is None and (r.get("id"), field, v) not in _warned:
        _warned.add((r.get("id"), field, v))
        sys.stderr.write("Warning: #%s %s %r is not a clear date (use YYYY-MM-DD); skipped.\n" % (r.get("id", "?"), field, v))
    return d


# ---- spreadsheet formula-injection guard -------------------------------------------------
TRIGGERS = ("=", "+", "-", "@", "\t", "\r")


def esc_cell(v):
    v = "" if v is None else str(v)
    if v.lstrip("'")[:1] in TRIGGERS and (v[:1] in TRIGGERS or v[:1] == "'"):
        return "'" + v
    return v


def unesc_cell(v):
    if v[:1] == "'" and v.lstrip("'")[:1] in TRIGGERS:
        return v[1:]
    return v


def secure_chmod(path):
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass  # e.g. Windows or a filesystem without modes


@contextlib.contextmanager
def locked(path, timeout=10.0):
    """Exclusive lock around load-modify-save, via an O_EXCL lock file next to the CSV."""
    lock = os.path.abspath(path) + ".lock"
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            os.write(fd, str(os.getpid()).encode("ascii"))
            os.close(fd)
            break
        except FileExistsError:
            try:
                if time.time() - os.path.getmtime(lock) > 60:  # left behind by a crashed run
                    os.remove(lock)
                    continue
            except OSError:
                continue
            if time.time() > deadline:
                fail("another tracker command seems to be running (lock file %s). If none is, delete that file and retry." % lock)
            time.sleep(0.1)
        except OSError as e:
            fail("cannot create lock file %s: %s" % (lock, e.strerror or e))
    try:
        yield
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def load(path):
    if not os.path.exists(path):
        fail("No tracker at %s. Run: tracker.py --file %s init" % (path, path))
    if os.path.isdir(path):
        fail("%s is a directory, not a CSV file." % path)
    try:
        with open(path, newline="", encoding="utf-8-sig") as fh:  # utf-8-sig: Excel adds a BOM
            rd = csv.reader(fh)
            header = next(rd, None)
            if header is None:
                fail("%s is empty. Run: tracker.py --file %s init (on a new name) or restore it from a backup." % (path, path))
            hdr = [h.strip().lower() for h in header]
            # known columns are matched case-insensitively; columns the user added keep their own spelling
            keys = [h if h in FIELDS else orig.strip() for h, orig in zip(hdr, header)]
            if "id" not in hdr or "company" not in hdr:
                fail("%s does not look like a tracker file: the header row must contain 'id' and 'company' columns "
                     "(found: %s). If you saved it from Excel, use 'CSV UTF-8' and keep the first row." % (path, ", ".join(hdr[:6]) or "nothing"))
            rows = []
            for rec in rd:
                if not rec or not any(c.strip() for c in rec):
                    continue
                if len(rec) > len(hdr) and any(c.strip() for c in rec[len(hdr):]):
                    sys.stderr.write("Warning: a row has more cells than the header; extra cells ignored.\n")
                rec = (rec + [""] * len(hdr))[:len(hdr)]  # short rows: missing cells become ''
                rows.append({k: unesc_cell(v) for k, v in zip(keys, rec) if k})
    except UnicodeDecodeError:
        fail("%s is not valid UTF-8. Save it from your spreadsheet as 'CSV UTF-8'." % path)
    except csv.Error as e:
        fail("%s is not a readable CSV file: %s" % (path, e))
    except OSError as e:
        fail("cannot read %s: %s" % (path, e.strerror or e))
    for r in rows:
        for f in FIELDS:
            r.setdefault(f, "")
    seen = {}
    for r in rows:
        seen[r["id"]] = seen.get(r["id"], 0) + 1
    dups = sorted(i for i, n in seen.items() if n > 1)
    if dups:
        sys.stderr.write("Warning: duplicate id(s) in %s: %s. Commands act on the first match; fix the id column.\n"
                         % (path, ", ".join(i or "(blank)" for i in dups)))
    return rows


def save(path, rows):
    d = os.path.dirname(os.path.abspath(path))
    extra = []
    for r in rows:
        for k in r:
            if k not in FIELDS and k not in extra:
                extra.append(k)  # keep columns the user added in their spreadsheet
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")  # created 0600
    done = False
    try:
        with os.fdopen(fd, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS + extra)
            for r in rows:
                w.writerow([esc_cell(r.get(f, "")) for f in FIELDS + extra])
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        done = True
        secure_chmod(path)
    except OSError as e:
        fail("cannot write %s: %s" % (path, e.strerror or e))
    finally:
        if not done and os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass


PROTECTED_NAMES = (".agents", ".kiro", ".claude", ".ssh", ".git")


def _split(p):
    return [x for x in re.split(r"[\\/]", p) if x]


def _inside(path, root):
    try:
        return os.path.commonpath([path, root]) == root
    except ValueError:
        return False


def allowed_root():
    """Folder that --file and --out must stay in: artifacts/output when it exists, else the current folder."""
    cwd = os.path.realpath(os.getcwd())
    out = os.path.join(cwd, "artifacts", "output")
    return os.path.realpath(out) if os.path.isdir(out) else cwd


def guard_path(given, flag, exts, allow_outside, tracker=None):
    """Refuse paths that prompt-injected text could use to overwrite files that matter. Returns the path to use.
    The protected-path refusals apply even with --allow-outside; that flag only lifts the root restriction."""
    if not given or not given.strip():
        fail("%s needs a file name." % flag)
    p = os.path.expanduser(given)
    lex = os.path.abspath(p)
    real = os.path.realpath(p)
    root = allowed_root()
    why = "refusing %s %s: " % (flag, given)
    if os.path.islink(lex):
        fail(why + "it is a symbolic link. Use a normal file.")
    if not p.lower().endswith(exts):
        fail(why + "the name must end in %s." % " or ".join(exts))
    if not allow_outside and not _inside(real, root):
        fail(why + "it is outside the allowed folder %s. Use a path inside it (add --allow-outside only if you "
             "really mean it, and the user asked for that location)." % root)
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
    if tracker is not None:  # an export target: never clobber the tracker or any existing CSV
        if os.path.lexists(real):
            if real.lower().endswith(".csv"):
                fail(why + "an existing .csv file is never overwritten by export.")
            if os.path.exists(tracker) and os.path.samefile(real, tracker):
                fail(why + "that is the tracker file itself.")
        if os.path.realpath(tracker) == real:
            fail(why + "that is the tracker file itself.")
    return p


def resolve_path(given):
    """--file if given; else artifacts/output/job-applications.csv when that folder exists, else cwd."""
    if given:
        return given
    if os.path.isdir(os.path.join("artifacts", "output")):
        return os.path.join("artifacts", "output", DEFAULT_FILE)
    return DEFAULT_FILE


def find_repo_root(start):
    cur = os.path.abspath(start)
    while True:
        if os.path.exists(os.path.join(cur, ".git")):
            return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return None
        cur = parent


def _read_rules(directory):
    """Rules of <directory>/.gitignore as (negated, anchored, dir_only, pattern) tuples; [] if unreadable."""
    try:
        with open(os.path.join(directory, ".gitignore"), encoding="utf-8-sig") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError):
        return []
    rules = []
    for line in lines:
        line = line.rstrip("\r\n")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        line = line.strip()
        neg = line.startswith("!")
        pat = line[1:] if neg else line
        if pat[:1] == "\\":
            pat = pat[1:]  # \# or \! : a literal first character
        dir_only = pat.endswith("/")
        pat = pat.rstrip("/")
        anchored = "/" in pat
        pat = pat.lstrip("/")
        if pat.startswith("**/"):
            pat, anchored = pat[3:], False
        if pat:
            rules.append((neg, anchored, dir_only, pat))
    return rules


def gitignored(root, abspath):
    """Rough .gitignore check with fnmatch (no subprocess). Reads .gitignore in the repo root, in every folder
    between it and the file (e.g. artifacts/.gitignore), later and deeper rules winning; once a parent folder is
    ignored, everything under it is. True if some rule seems to cover the file."""
    try:
        rel = os.path.relpath(abspath, root).replace(os.sep, "/")
    except ValueError:
        return False
    parts = [x for x in rel.split("/") if x and x != "."]
    if not parts or parts[0] == "..":
        return False
    cache = {}
    for i in range(1, len(parts) + 1):
        is_dir = i < len(parts)
        ignored = False
        base = root
        for j in range(0, i):  # folders root, root/parts[0], ... that are ancestors of parts[:i]
            if base not in cache:
                cache[base] = _read_rules(base)
            sub = parts[j:i]  # path of the candidate relative to this .gitignore's folder
            for neg, anchored, dir_only, pat in cache[base]:
                if dir_only and not is_dir:
                    continue
                if anchored:
                    hit = fnmatch.fnmatchcase("/".join(sub), pat)
                else:
                    hit = fnmatch.fnmatchcase(sub[-1], pat)
                if hit:
                    ignored = not neg
            base = os.path.join(base, parts[j])
        if ignored:
            return True
    return False


def next_id(rows):
    ids = []
    for r in rows:
        v = str(r.get("id", "")).strip()
        if v.isdecimal():  # not isdigit(): '²' is a digit but int('²') raises
            try:
                ids.append(int(v))
            except ValueError:
                pass
    return str(max(ids, default=0) + 1)


def find(rows, rid):
    for r in rows:
        if r["id"] == str(rid):
            return r
    fail("No application with id %s" % rid)


def check_status(s):
    s = s.lower().strip()
    if s not in STATUSES:
        fail("Unknown status %r. Use one of: %s" % (s, ", ".join(STATUSES)))
    return s


def add_note(r, text, day):
    entry = "%s: %s" % (day.isoformat(), text.strip())
    r["notes"] = (r["notes"] + " | " + entry) if r["notes"] else entry


def apply_status(r, status, day):
    prev = r["status"]
    r["status"] = status
    if status == "applied" and not r["applied_date"]:
        r["applied_date"] = day.isoformat()
    if status in RESPONDED and prev not in RESPONDED and not r["first_response_date"]:
        r["first_response_date"] = day.isoformat()


def cmd_init(a, path):
    if os.path.exists(path):
        fail("%s already exists." % path)
    save(path, [])
    print("Created %s" % path)
    print("Note: this file holds personal job-search data (names, contacts, pay). Keep it local; do not share or commit it.")
    root = find_repo_root(os.getcwd())
    ap = os.path.abspath(path)
    if root and ap.startswith(root + os.sep) and not gitignored(root, ap):
        print("Warning: the current folder is inside a git repository (%s) and %s does not appear in .gitignore. "
              "Add it (and %s.lock) to .gitignore before committing." % (root, os.path.relpath(ap, root), os.path.basename(path)))


def cmd_add(a, path):
    rows = load(path)
    day = today(a)
    status = check_status(a.status or ("applied" if a.applied else "wishlist"))
    r = {f: "" for f in FIELDS}
    r.update({"id": next_id(rows), "company": a.company, "role": a.role, "location": a.location or "",
              "url": a.url or "", "ad_file": a.ad or "", "cv_version": a.cv or "", "letter_version": a.letter or "",
              "next_action": a.next or "", "contact": a.contact or "", "pay": a.pay or "", "last_updated": day.isoformat()})
    if a.next_date:
        r["next_action_date"] = parse_date(a.next_date, "--next-date").isoformat()
    if a.applied:
        r["applied_date"] = parse_date(a.applied, "--applied").isoformat()
    apply_status(r, status, parse_date(a.applied) if a.applied else day)
    if a.note:
        add_note(r, a.note, day)
    dup = [x for x in rows if x["company"].lower() == a.company.lower() and x["role"].lower() == a.role.lower()
           and x["status"] in ACTIVE]
    rows.append(r)
    save(path, rows)
    print("Added #%s: %s - %s [%s]" % (r["id"], r["company"], r["role"], r["status"]))
    if dup:
        print("Warning: an active application for this company and role already exists (#%s)." % dup[0]["id"])


def cmd_update(a, path):
    rows = load(path)
    day = today(a)
    r = find(rows, a.id)
    if a.status:
        apply_status(r, check_status(a.status), day)
    if a.applied:
        r["applied_date"] = parse_date(a.applied, "--applied").isoformat()
    for attr, field in (("next", "next_action"), ("contact", "contact"), ("pay", "pay"),
                        ("cv", "cv_version"), ("letter", "letter_version")):
        v = getattr(a, attr)
        if v is not None:
            r[field] = v
    if a.next_date is not None:
        r["next_action_date"] = parse_date(a.next_date, "--next-date").isoformat() if a.next_date else ""
    if a.note:
        add_note(r, a.note, day)
    if r["status"] not in ACTIVE:  # closed: clear stale next steps, but keep anything supplied in this command
        if a.next is None:
            r["next_action"] = ""
        if a.next_date is None:
            r["next_action_date"] = ""
    r["last_updated"] = day.isoformat()
    save(path, rows)
    print("Updated #%s: %s - %s [%s]" % (r["id"], r["company"], r["role"], r["status"]))


def table(rows, cols):
    widths = [max(len(c), *(len(str(r.get(c, ""))[:40]) for r in rows)) if rows else len(c) for c in cols]
    line = "  ".join(c.upper().ljust(w) for c, w in zip(cols, widths))
    out = [line, "  ".join("-" * w for w in widths)]
    for r in rows:
        out.append("  ".join(str(r.get(c, ""))[:40].ljust(w) for c, w in zip(cols, widths)))
    return "\n".join(out)


def cmd_list(a, path):
    rows = load(path)
    if a.status:
        want = {check_status(s) for s in a.status.split(",")}
        rows = [r for r in rows if r["status"] in want]
    if a.active:
        rows = [r for r in rows if r["status"] in ACTIVE]
    if a.company:
        rows = [r for r in rows if a.company.lower() in r["company"].lower()]
    if not rows:
        print("No matching applications.")
        return
    print(table(rows, ["id", "company", "role", "status", "applied_date", "next_action_date", "next_action"]))


def cmd_due(a, path):
    rows = load(path)
    t = today(a)
    horizon = t + dt.timedelta(days=a.days)
    overdue, soon, follow = [], [], []
    for r in rows:
        if r["status"] not in ACTIVE:
            continue
        d = row_date(r, "next_action_date")
        if d is not None:
            if d < t:
                overdue.append((d, r))
            elif d <= horizon:
                soon.append((d, r))
        applied_on = row_date(r, "applied_date") if r["status"] == "applied" and not r["first_response_date"] else None
        if applied_on is not None:
            age = (t - applied_on).days
            if age >= a.follow_up_days and not any(x is r for _, x in overdue + soon):
                follow.append((age, r))
    if not (overdue or soon or follow):
        print("Nothing due in the next %d days." % a.days)
        return
    if overdue:
        print("OVERDUE")
        for d, r in sorted(overdue, key=lambda x: x[0]):
            print("  #%s %s - %s: %s (was due %s, %d days ago)" % (r["id"], r["company"], r["role"], r["next_action"] or "check in", d, (t - d).days))
    if soon:
        print("DUE SOON (next %d days)" % a.days)
        for d, r in sorted(soon, key=lambda x: x[0]):
            print("  #%s %s - %s: %s (%s)" % (r["id"], r["company"], r["role"], r["next_action"] or "check in", d))
    if follow:
        print("NO REPLY YET - consider one polite follow-up (applied %d+ days ago, none sent)" % a.follow_up_days)
        for age, r in sorted(follow, key=lambda x: -x[0]):
            print("  #%s %s - %s: applied %d days ago" % (r["id"], r["company"], r["role"], age))


def pct(n, d):
    return "%d%%" % round(100 * n / d) if d else "n/a"


def cmd_stats(a, path):
    rows = load(path)
    if not rows:
        print("No applications yet.")
        return
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in STATUSES}
    print("Applications: %d (active: %d)" % (len(rows), sum(1 for r in rows if r["status"] in ACTIVE)))
    print("By status: " + ", ".join("%s %d" % (s, n) for s, n in counts.items() if n))
    applied = [r for r in rows if r["applied_date"] or r["status"] not in ("wishlist", "preparing")]
    resp = [r for r in applied if r["first_response_date"] or r["status"] in RESPONDED]
    interviews = [r for r in applied if r["status"] in ("interviewing", "assessment", "offer", "negotiating", "accepted")]
    offers = [r for r in applied if r["status"] in ("offer", "negotiating", "accepted")]
    print("\nFunnel (applied = %d)" % len(applied))
    print("  Any response:   %d (%s)" % (len(resp), pct(len(resp), len(applied))))
    print("  Reached interview+: %d (%s)" % (len(interviews), pct(len(interviews), len(applied))))
    print("  Offers:         %d (%s)" % (len(offers), pct(len(offers), len(applied))))
    days = []
    for r in applied:
        d1, d2 = row_date(r, "applied_date"), row_date(r, "first_response_date")
        if d1 is not None and d2 is not None:
            days.append((d2 - d1).days)
    if days:
        print("  Median days to first response: %g (n=%d)" % (statistics.median(days), len(days)))
    by_cv = {}
    for r in applied:
        k = r["cv_version"] or "(unlabelled)"
        by_cv.setdefault(k, [0, 0])
        by_cv[k][0] += 1
        by_cv[k][1] += 1 if (r["first_response_date"] or r["status"] in RESPONDED) else 0
    if len(by_cv) > 1:
        print("\nResponse by CV version")
        for k, (n, rsp) in sorted(by_cv.items()):
            print("  %-28s %d applied, %d responded (%s)" % (k, n, rsp, pct(rsp, n)))
    if len(applied) < 20:
        print("\nCaution: fewer than 20 applications. Percentages are noisy; do not read much into differences between versions.")


def cmd_show(a, path):
    r = find(load(path), a.id)
    for f in FIELDS:
        print("%-20s %s" % (f + ":", r[f]))


def cmd_export(a, path):
    rows = load(path)
    cols = ["id", "company", "role", "status", "applied_date", "cv_version", "letter_version", "next_action_date", "next_action"]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(" ".join(str(r[c]).split()).replace("|", "/") for c in cols) + " |")
    text = "\n".join(lines) + "\n"
    if a.out:
        try:
            fd = os.open(a.out, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as e:
            fail("cannot write %s: %s" % (a.out, e.strerror or e))
        secure_chmod(a.out)
        print("Wrote %s" % a.out)
    else:
        print(text)


def cmd_delete(a, path):
    rows = load(path)
    r = find(rows, a.id)
    if not a.yes:
        fail("Refusing to delete #%s (%s - %s) without --yes. Prefer setting status to withdrawn." % (r["id"], r["company"], r["role"]))
    same = [x for x in rows if x["id"] == r["id"]]
    if len(same) > 1:
        sys.stderr.write("Warning: %d rows share id %s; deleting only the first one (%s - %s). Fix the id column.\n"
                         % (len(same), r["id"], r["company"], r["role"]))
    save(path, [x for x in rows if x is not r])  # by row identity, never by id equality
    print("Deleted #%s" % a.id)


def build():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=None,
                    help="tracker CSV. Default: artifacts/output/job-applications.csv if artifacts/output exists "
                         "here, else job-applications.csv in the current folder")
    ap.add_argument("--allow-outside", action="store_true",
                    help="allow --file and export --out outside the allowed folder (artifacts/output if it exists, "
                         "else the current folder). Never overrides the protected-path refusals (.agents .kiro "
                         ".claude .ssh .git, artifacts/input, skill folders, symlinks). Put it before the command.")
    ap.add_argument("--today", help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    p = sub.add_parser("add")
    p.add_argument("--company", required=True)
    p.add_argument("--role", required=True)
    for n in ("location", "url", "ad", "applied", "cv", "letter", "status", "next", "next-date", "contact", "pay", "note"):
        p.add_argument("--" + n)
    p = sub.add_parser("update")
    p.add_argument("id")
    for n in ("status", "next", "next-date", "note", "contact", "pay", "cv", "letter", "applied"):
        p.add_argument("--" + n)
    p = sub.add_parser("list")
    p.add_argument("--status")
    p.add_argument("--active", action="store_true")
    p.add_argument("--company")
    p = sub.add_parser("due")
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--follow-up-days", type=int, default=7)
    sub.add_parser("stats")
    p = sub.add_parser("show")
    p.add_argument("id")
    p = sub.add_parser("export")
    p.add_argument("--out", help="write the Markdown table to this .md (or new .csv) file, inside the allowed "
                                 "folder; never the tracker file or an existing .csv")
    p = sub.add_parser("delete")
    p.add_argument("id")
    p.add_argument("--yes", action="store_true")
    return ap


def main(argv=None):
    a = build().parse_args(argv)
    handlers = {"init": cmd_init, "add": cmd_add, "update": cmd_update, "list": cmd_list, "due": cmd_due,
                "stats": cmd_stats, "show": cmd_show, "export": cmd_export, "delete": cmd_delete}
    if a.today:
        parse_date(a.today, "--today")  # friendly error before doing anything
    path = guard_path(resolve_path(a.file), "--file", (".csv",), a.allow_outside)
    if a.cmd == "export" and a.out:
        a.out = guard_path(a.out, "--out", (".md", ".csv"), a.allow_outside, tracker=path)
    try:
        if a.cmd == "init":
            parent = os.path.dirname(os.path.abspath(path))
            os.makedirs(parent, exist_ok=True)
            with locked(path):
                handlers[a.cmd](a, path)
        elif a.cmd in ("add", "update", "delete"):
            if not os.path.exists(path):
                fail("No tracker at %s. Run: tracker.py --file %s init" % (path, path))
            with locked(path):  # load -> modify -> save must not interleave with another command
                handlers[a.cmd](a, path)
        else:
            handlers[a.cmd](a, path)
    except OSError as e:
        fail("%s: %s" % (getattr(e, "filename", None) or path, e.strerror or e))
    return 0


if __name__ == "__main__":
    sys.exit(main())
