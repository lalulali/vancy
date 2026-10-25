#!/usr/bin/env python3
"""Offer comparison and range-positioning calculator. Zero dependencies (stdlib only).

Two subcommands:

  compare OFFERS.json [--format md|json]
      Normalise one or more offers to a comparable annual figure and show every assumption.

  position --range LOW,MID,HIGH --offer N [--current N] [--target-pct P]
      Show where an offer sits inside a researched pay range, the gap to the middle and high end,
      and a candidate counter band. You supply the range; this tool never looks up market pay.
      --range also accepts LOW,HIGH (the middle is then the midpoint). --offer is a BASE salary figure:
      compare it with a range for base pay, not with a total-compensation number. If the offer is at or
      above the top of your range there is no counter band: negotiate non-salary terms instead.

OFFERS.json (a non-empty list of objects, or {"offers": [...]}; a single object also works.
Every field is optional except name and base_annual. Numbers must be finite and not negative):
  {
    "name": "Northwind", "currency": "GBP",
    "base_annual": 85000,                # the 12-month contractual base
    "base_payments_per_year": 12,        # 13 or 14 where a 13th/14th-month salary is also paid (cash = base x n/12)
    "bonus_target_pct": 10,              # target bonus as % of base
    "bonus_confidence_pct": 70,          # how likely you think the target payout is (default 100)
    "sign_on": 5000,                     # one-time cash
    "sign_on_clawback_months": 12,       # note only
    "equity_grant_value": 40000,         # grant value at today's price
    "equity_vest_years": 4,
    "equity_type": "public",             # optional: public | private | options (see below)
    "equity_haircut_pct": 50,            # 0-100 discount for risk / illiquidity; if given it always wins (default 50)
    "employer_retirement_pct": 5,        # employer retirement contribution as % of base
    "allowances_annual": 2400,           # housing / transport / phone etc, taxable or not as you decide
    "benefits_value_annual": 3000,       # health etc, only what you would otherwise pay for
    "extra_leave_days": 2,               # days of leave beyond what you would otherwise have (valued at base / 260)
    "annual_costs": 1800,                # commute, parking, relocation amortised, etc
    "notes": "hybrid 3 days"
  }

Equity type: with "public" (listed RSUs) the suggested haircut is 15%; with "private" 70%; with no equity_type
the default stays 50%. "options" needs your own equity_haircut_pct: this tool does not model strike prices, so
enter equity_grant_value as your own estimate of what the options are worth today (after the strike) and the
haircut you want. equity_vest_years must be greater than 0.

Currency: ISO codes in any case (gbp -> GBP) or the symbols £ € $ (read as USD) ¥ (read as JPY); write the ISO
code for anything else. Mixing labelled and unlabelled offers is an error.

All amounts must be in the same currency, and BEFORE tax. Comparisons across countries are not valid without
tax, cost of living and social-benefit adjustments, which this tool does not make. Treat results as a prompt for
questions, not a verdict. In the comparison, "Base (cash)" is one line of the table; the "total" rows add bonus,
equity, retirement and the rest, so never set a total against a base-salary range.

On Windows use `py` or `python` instead of `python3`.
"""
import argparse
import json
import math
import sys

CURRENCY_SYMBOLS = {"£": "GBP", "€": "EUR", "$": "USD", "US$": "USD", "¥": "JPY", "₹": "INR", "₩": "KRW"}
EQUITY_SUGGESTED_HAIRCUT = {"public": 15.0, "private": 70.0}
EQUITY_TYPES = ("public", "private", "options")


def fail(msg):
    sys.stderr.write("Error: %s\n" % msg)
    raise SystemExit(2)


def norm_currency(v):
    s = str(v or "").strip()
    if not s:
        return ""
    return CURRENCY_SYMBOLS.get(s, CURRENCY_SYMBOLS.get(s.upper(), s.upper()))


def finite(x, label):
    if isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x):
        fail("%s must be a finite number, got %r" % (label, x))
    return float(x)


def num(d, k, default=0.0, lo=0.0, hi=None, strict_gt=False):
    """Read a finite number from offer d. Default minimum is 0 (no negatives)."""
    v = d.get(k, default)
    label = "Offer '%s': %s" % (d.get("name", "?"), k)
    if isinstance(v, bool):
        fail("%s must be a number, got %r" % (label, v))
    try:
        f = float(v)
    except (TypeError, ValueError):
        fail("%s must be a number, got %r" % (label, v))
    except OverflowError:
        fail("%s is too large to be a real amount" % label)
    if not math.isfinite(f):
        fail("%s must be a finite number, got %r" % (label, v))
    if lo is not None and (f <= lo if strict_gt else f < lo):
        fail("%s must be %s %g, got %g" % (label, "greater than" if strict_gt else "at least", lo, f))
    if hi is not None and f > hi:
        fail("%s must be at most %g, got %g" % (label, hi, f))
    return f


def all_finite(pairs, where):
    """Stop with a friendly error when a computed figure overflowed to infinity or NaN."""
    for label, v in pairs:
        if not math.isfinite(v):
            fail("%s: %s is too large to calculate (the numbers entered overflow). Check the inputs." % (where, label))


def normalise(o):
    name = " ".join(str(o.get("name") or "Offer").split())
    o = dict(o, name=name)
    base = num(o, "base_annual", strict_gt=True)
    pays = num(o, "base_payments_per_year", 12, strict_gt=True)
    # base_annual is the 12-month base; a 13th or 14th payment adds base/12 each.
    base_cash = base * (pays / 12.0)
    bonus_pct = num(o, "bonus_target_pct")
    conf = num(o, "bonus_confidence_pct", 100, 0, 100) / 100.0
    bonus_target = base_cash * bonus_pct / 100.0
    bonus_expected = bonus_target * conf
    sign_on = num(o, "sign_on")
    eq_val = num(o, "equity_grant_value")
    eq_years = num(o, "equity_vest_years", 4, strict_gt=True)
    eq_type = o.get("equity_type")
    if eq_type is not None:
        eq_type = str(eq_type).strip().lower()
        if eq_type not in EQUITY_TYPES:
            fail("Offer '%s': equity_type must be one of %s, got %r" % (name, ", ".join(EQUITY_TYPES), o.get("equity_type")))
    if "equity_haircut_pct" in o:
        haircut_pct, haircut_src = num(o, "equity_haircut_pct", 50, 0, 100), "explicit equity_haircut_pct"
    elif eq_type in EQUITY_SUGGESTED_HAIRCUT:
        haircut_pct, haircut_src = EQUITY_SUGGESTED_HAIRCUT[eq_type], "suggested for %s equity" % eq_type
    elif eq_type == "options" and eq_val > 0:
        fail("Offer '%s': equity_type 'options' needs your own equity_haircut_pct (0-100). This tool does not model "
             "strike prices: enter equity_grant_value as your estimate of what the options are worth today." % name)
    else:
        haircut_pct, haircut_src = 50.0, "default"
    haircut = haircut_pct / 100.0
    equity_annual = (eq_val / eq_years) * (1 - haircut)
    retirement = base_cash * num(o, "employer_retirement_pct") / 100.0
    allowances = num(o, "allowances_annual")
    benefits = num(o, "benefits_value_annual")
    day_value = base_cash / 260.0  # working days per year
    leave_value = day_value * num(o, "extra_leave_days")
    costs = num(o, "annual_costs")

    recurring = base_cash + bonus_expected + equity_annual + retirement + allowances + benefits + leave_value - costs
    first_year = recurring + sign_on
    all_finite([("base cash", base_cash), ("expected bonus", bonus_expected), ("target bonus", bonus_target),
                ("equity per year", equity_annual), ("employer retirement", retirement), ("allowances", allowances),
                ("benefits", benefits), ("leave value", leave_value), ("annual costs", costs),
                ("recurring total", recurring), ("first-year total", first_year)], "Offer '%s'" % name)
    return {
        "name": name,
        "currency": norm_currency(o.get("currency", "")),
        "base_cash": round(base_cash),
        "bonus_expected": round(bonus_expected),
        "bonus_target": round(bonus_target),
        "equity_annual_after_haircut": round(equity_annual),
        "employer_retirement": round(retirement),
        "allowances": round(allowances),
        "benefits_value": round(benefits),
        "extra_leave_value": round(leave_value),
        "annual_costs": round(costs),
        "recurring_annual_total": round(recurring),
        "sign_on_one_time": round(sign_on),
        "first_year_total": round(first_year),
        "notes": str(o.get("notes", "") or ""),
        "assumptions": {
            "payments_per_year": pays, "bonus_confidence_pct": conf * 100 if bonus_pct else None,
            "equity_haircut_pct": haircut * 100 if eq_val else None, "equity_vest_years": eq_years if eq_val else None,
            "equity_type": eq_type, "equity_haircut_source": haircut_src if eq_val else None,
            "working_days_per_year": 260,
        },
        "clawback": ("sign-on repayable if you leave within %g months" % num(o, "sign_on_clawback_months")
                     if num(o, "sign_on_clawback_months") else ""),
    }


def render_compare(rows):
    cur = rows[0]["currency"]
    cell = lambda t: str(t).replace("|", "\\|")
    lines = ["# Offer comparison (%s, pre-tax)" % (cur or "same currency"), "",
             "Base (cash) is the salary alone; the totals below add bonus, equity, retirement and the rest. "
             "Do not compare a total with a base-salary range.", "",
             "| Component | " + " | ".join(cell(r["name"]) for r in rows) + " |",
             "|---|" + "---|" * len(rows)]
    comps = [("Base (cash)", "base_cash"), ("Bonus (expected)", "bonus_expected"),
             ("Equity / yr (after haircut)", "equity_annual_after_haircut"),
             ("Employer retirement", "employer_retirement"), ("Allowances", "allowances"),
             ("Benefits you would otherwise buy", "benefits_value"), ("Extra leave value", "extra_leave_value"),
             ("Annual costs (-)", "annual_costs"), ("**Recurring annual total (base + extras)**", "recurring_annual_total"),
             ("Sign-on (one-time)", "sign_on_one_time"), ("**First-year total (incl. sign-on)**", "first_year_total")]
    for label, key in comps:
        lines.append("| %s | %s |" % (label, " | ".join("{:,}".format(r[key]) for r in rows)))
    best = max(rows, key=lambda r: r["recurring_annual_total"])
    lines += ["", "**Highest recurring total:** %s ({:,})".format(best["recurring_annual_total"]) % cell(best["name"]), ""]
    lines.append("## Assumptions you should challenge")
    for r in rows:
        a = r["assumptions"]
        parts = ["%g base payments/yr" % a["payments_per_year"]]
        if a["bonus_confidence_pct"] is not None:
            parts.append("bonus counted at %g%% of target" % a["bonus_confidence_pct"])
        if a["equity_haircut_pct"] is not None:
            parts.append("equity discounted %g%% (%s) and spread over %g years"
                         % (a["equity_haircut_pct"], a["equity_haircut_source"], a["equity_vest_years"]))
        if r["extra_leave_value"]:
            parts.append("leave valued at base / %g working days" % a["working_days_per_year"])
        tail = (" " + r["clawback"].capitalize() + ".") if r["clawback"] else ""
        tail += (" Note: " + r["notes"] + ".") if r["notes"] else ""
        lines.append("- **%s:** %s.%s" % (r["name"], "; ".join(parts), tail))
    lines += ["", "Not included: tax, cost of living, career growth, learning, manager quality, job security, commute time, "
              "probation terms, notice period, non-compete. Ask about these before deciding."]
    return "\n".join(lines)


def position(rng, offer, current=None, target_pct=None):
    lo, mid, hi = rng
    if not all(math.isfinite(x) for x in rng) or not (lo <= mid <= hi) or lo <= 0:
        fail("--range must be LOW,MID,HIGH (or LOW,HIGH) of finite numbers with 0 < LOW <= MID <= HIGH")
    if not math.isfinite(offer) or offer <= 0:
        fail("--offer must be a finite number greater than 0 (a base annual salary), got %r" % offer)
    try:
        gaps = [100 * (mid - offer) / offer, 100 * (hi - offer) / offer, mid - offer, hi - offer]
    except OverflowError:
        gaps = [float("inf")]
    all_finite([("a gap", g) for g in gaps] + [("the range width", hi - lo)], "--range/--offer")
    if hi > lo:
        where = (offer - lo) / (hi - lo)
    else:
        where = 1.0 if offer >= hi else 0.0  # zero-width range: at or above the top = 100%, below = 0%
    out = {
        "offer": offer, "range": {"low": lo, "mid": mid, "high": hi},
        "offer_basis": "base annual salary; compare only with a base-pay range, not with total compensation",
        "position_in_range_pct": round(100 * where),
        "gap_to_mid": round(mid - offer), "gap_to_mid_pct": round(100 * (mid - offer) / offer, 1),
        "gap_to_high": round(hi - offer), "gap_to_high_pct": round(100 * (hi - offer) / offer, 1),
    }
    if offer >= hi:
        out["counter_band"] = None
        out["note"] = ("Offer is at or above the top of your researched range: no salary counter band. "
                       "Negotiate non-salary terms (sign-on, equity, bonus, leave, start date, title, review date).")
    else:
        # Candidate counter band: from the mid-point (or +5% if already above mid) to the top of the researched range.
        floor_ask = min(max(mid, offer * 1.05), hi)
        out["counter_band"] = {"from": round(floor_ask), "to": round(hi)}
    out["reading"] = ("Offer is below the middle of your researched range." if offer < mid else
                      "Offer is at or above the middle of your researched range." if offer < hi else
                      "Offer is at or above the top of your researched range; negotiate non-salary terms.")
    if current:
        vs = 100 * (offer - current) / current
        all_finite([("the change against --current", vs)], "--current")
        out["vs_current_pct"] = round(vs, 1)
    if target_pct is not None:
        ask = offer * (1 + target_pct / 100.0)
        all_finite([("the target ask", ask)], "--target-pct")
        out["target_ask"] = round(ask)
    out["cautions"] = [
        "The range comes from YOU (and your sources), not from this tool. Use at least three independent sources.",
        "An ambitious but justified first number can anchor the talk; one that is far above the employer's band can end it. Tie it to evidence.",
        "Check local law before discussing past pay: some jurisdictions restrict employers from asking.",
    ]
    return out


def load_offers(path):
    try:
        with open(path, encoding="utf-8-sig") as fh:
            text = fh.read()
    except OSError as e:
        fail("cannot read %s: %s" % (path, e.strerror or e))
    except UnicodeDecodeError:
        fail("%s is not valid UTF-8 text. Save it as UTF-8." % path)
    if not text.strip():
        fail("%s is empty. Expected a JSON list of offers (see assets/example-offers.json)." % path)

    def bad_const(c):
        raise ValueError("%s is not allowed; use a real number" % c)
    try:
        data = json.loads(text, parse_constant=bad_const)
    except ValueError as e:
        fail("%s is not valid JSON: %s" % (path, e))
    except RecursionError:
        fail("%s is nested too deeply to be an offers file." % path)
    if isinstance(data, dict):
        data = data["offers"] if isinstance(data.get("offers"), list) else [data]
    if not isinstance(data, list) or not data:
        fail("%s must hold a non-empty JSON list of offer objects, or {\"offers\": [...]}." % path)
    for n, o in enumerate(data, 1):
        if not isinstance(o, dict):
            fail("Offer #%d in %s must be an object like {\"name\": ..., \"base_annual\": ...}, got %s." % (n, path, type(o).__name__))
        if "base_annual" not in o:
            fail("Offer #%d (%s) is missing base_annual." % (n, o.get("name", "?")))
    return data


def main(argv=None):
    try:
        return _main(argv)
    except (OverflowError, RecursionError):
        fail("a number in the input is too large (or the file is nested too deeply) to calculate. "
             "Use realistic annual amounts.")


def _main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("compare")
    c.add_argument("offers")
    c.add_argument("--format", choices=["md", "json"], default="md")
    p = sub.add_parser("position")
    p.add_argument("--range", required=True,
                   help="LOW,MID,HIGH (or LOW,HIGH) researched annual BASE-salary range")
    p.add_argument("--offer", type=float, required=True,
                   help="the offered annual BASE salary (a base figure, not total compensation); must be > 0")
    p.add_argument("--current", type=float, help="current annual base salary, optional (> 0)")
    p.add_argument("--target-pct", type=float, help="optional percent above the offer you want to ask for")
    a = ap.parse_args(argv)

    if a.cmd == "compare":
        data = load_offers(a.offers)
        rows = [normalise(dict(o, name=o.get("name") or "Offer %d" % n)) for n, o in enumerate(data, 1)]
        labelled = [r["currency"] for r in rows if r["currency"]]
        if labelled and len(labelled) != len(rows):
            fail("Some offers have a currency and some do not. Label all offers or none.")
        if len(set(labelled)) > 1:
            fail("Offers use different currencies (%s). Convert and adjust for tax first." % ", ".join(sorted(set(labelled))))
        print(json.dumps(rows, indent=2) if a.format == "json" else render_compare(rows))
    else:
        try:
            nums = [float(x) for x in a.range.split(",")]
        except ValueError:
            fail("--range must be numbers: LOW,MID,HIGH (or LOW,HIGH)")
        if len(nums) == 2:
            nums = [nums[0], (nums[0] + nums[1]) / 2.0, nums[1]]
        if len(nums) != 3:
            fail("--range must be LOW,MID,HIGH (or LOW,HIGH)")
        if a.current is not None and (not math.isfinite(a.current) or a.current <= 0):
            fail("--current must be a finite number greater than 0")
        if a.target_pct is not None and (not math.isfinite(a.target_pct) or a.target_pct < 0):
            fail("--target-pct must be a finite number, 0 or more")
        res = position(tuple(nums), a.offer, a.current, a.target_pct)
        print(json.dumps(res, indent=2))
        if res.get("note"):
            sys.stderr.write("Note: %s\n" % res["note"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
