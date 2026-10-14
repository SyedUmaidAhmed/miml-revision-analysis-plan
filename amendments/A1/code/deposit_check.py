r"""The single real-data guard shared by every revision tool (T02, T03, T04/T07).

DECISIONS.md, 2026-10-13, "Deposit-line format and a single shared check":
after the deposit, the Public-timestamp cell of PREREGISTERED.md (line 8) is
written in exactly this form

    https://doi.org/<DOI> (YYYY-MM-DD)

where <DOI> matches 10\\.\\d{4,9}/[A-Za-z0-9._;()/:-]+ and is the published
(not draft) record. `deposit_recorded()` accepts only a whole-cell fullmatch of
that grammar on line 8. Anything else (free text, drafts, other hosts, bold,
comments, trailing text, placeholders) keeps every real-data run refused.

Row and cell (CODE-T02 review 5): line 8 must start with the exact prefix
"| Public timestamp |" (so "| Public timestamps |" or "| Public timestamp
(planned) |" are not the row) and end with " |"; the cell is the text between
the two. An escaped pipe "\|" inside the cell stays part of the cell, so text
after it can never be split off as a separate column.

The grammar is compiled with re.ASCII (Unicode digits never match \d) and
the DOI suffix must end in [A-Za-z0-9] (review 4, DECISIONS.md newest row).

Closing-only checks inside the grammar (they never open the guard):
  - the date must be a real calendar date, on or after 2026-10-13 (the date
    the final plan was frozen; no deposit can be older) and on or before the
    current UTC date at check time (DECISIONS.md "Deposit-line date upper
    bound"; a deposit cannot be dated in the future);
  - the DOI must not look like a placeholder (a run of three or more N or X,
    or "..."), because the character class otherwise admits zenodo.NNNNNNN;
  - the DOI must not be a test DOI: the DataCite test prefix 10.5072 (which
    the Zenodo sandbox issues) or any DOI naming "sandbox".

Amendments (AMENDMENT.md A1, review A1-1 finding 5; close-only): the deposited
plan governs until an amendment is itself deposited (§1.8), so a real-data run
must not start while any amendment is undeposited. AMENDMENT.md, in the plan's
directory, is read. Every section headed "## A<n>" must contain exactly one
line beginning "**Deposited:**", of exactly the form

    **Deposited:** https://doi.org/<DOI> (YYYY-MM-DD)

with the same grammar and closing checks as line 8. The DOI must also differ
from the plan's DOI (compared case-insensitively; a new Zenodo version has its
own DOI), and the date must not precede the plan's. A missing, malformed or
duplicated line keeps the guard closed.
Fail-closed structure (A1 reviews 2-5): after one level-1 title, the only
headings allowed are dated "## A<n> (YYYY-MM-DD)" and "## E<n> (YYYY-MM-DD)"
(a §6.5/§6.7 cap or budget decision, exempt from deposit); a heading date must
be a real date between MIN_DATE and today. An A section's deposit DOI must be
used by no other A section, and its date must not precede the heading date.
Closing conditions: a code fence, HTML comment, <pre> or <h1>..<h6> tag
anywhere; a line starting an HTML block (also inside a blockquote); any other
heading-like line, including one inside a blockquote or list item; a setext
heading (any "=" or "-" underline, also inside a blockquote or list item); a
duplicated section; a "**Deposited:**" line outside an A section; a missing
section of REQUIRED_SECTIONS (real plan only; a missing file counts as empty);
an unreadable file.

API:
    deposit_recorded(plan_path=PLAN, required=None) -> bool   (line 8 AND every A section)
    deposit_reference(plan_path=PLAN) -> (doi, date) or None   (line 8 only)
    amendment_status(plan_path=PLAN, required=None)
        -> {"A1": (doi, date) or None, "E1": "exempt", ...} or None (unsafe/unreadable)
"""
import datetime
import os
import re

PLAN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PREREGISTERED.md")
ROW_LINE = 8                                   # 1-based line of the row
ROW_PREFIX = "| Public timestamp |"
# re.ASCII: \d is [0-9] only (review 4 #1: Unicode digits opened the registrant).
# The DOI suffix must end in [A-Za-z0-9] (DECISIONS.md newest row), so trailing
# punctuation . ; ) - / never belongs to an accepted DOI.
CELL_RE = re.compile(
    r"https://doi\.org/(10\.\d{4,9}/[A-Za-z0-9._;()/:-]*[A-Za-z0-9]) \((\d{4}-\d{2}-\d{2})\)",
    re.ASCII)
MIN_DATE = datetime.date(2026, 10, 13)       # no deposit can predate the final plan
PLACEHOLDER_RE = re.compile(r"N{3,}|X{3,}|\.{3}", re.IGNORECASE)
TEST_DOI_PREFIXES = ("10.5072/",)            # DataCite test prefix (Zenodo sandbox)


def _today():
    """Reference date of the upper bound: the current UTC date at check time.
    Tests replace this helper to pin "today"."""
    return datetime.datetime.now(datetime.timezone.utc).date()


def _cell(plan_path):
    """The stripped value cell of line 8, or None if line 8 is not the row."""
    try:
        with open(plan_path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
    except (OSError, ValueError):       # unreadable, or not UTF-8 (review 5): closed
        return None
    if len(lines) < ROW_LINE:
        return None
    line = lines[ROW_LINE - 1].rstrip("\r").rstrip()
    if not line.startswith(ROW_PREFIX) or not line.endswith(" |"):
        return None
    # between the exact prefix and the final " |"; an escaped "\|" is cell text
    return line[len(ROW_PREFIX):-2].strip()


def deposit_reference(plan_path=PLAN):
    """(doi, date) when line 8 holds a recorded deposit, else None."""
    cell = _cell(plan_path)
    if cell is None:
        return None
    return _checked(cell)


AMENDMENT_NAME = "AMENDMENT.md"
# Amendment sections the real plan's AMENDMENT.md must contain (grows with each
# committed amendment): deleting, emptying or renaming one closes the guard
# (A1 review 2, F1). Applies only to the real plan (synthetic plans in tests
# declare their own via `required=`).
REQUIRED_SECTIONS = frozenset({"A1"})
# The only heading forms allowed after the single level-1 title (A1 reviews 2-3):
#   "## A<n> (YYYY-MM-DD)..."  an analysis amendment: needs its own deposit line,
#                              with a DOI used by no other section and a date no
#                              earlier than the heading date;
#   "## E<n> (YYYY-MM-DD)..."  a §6.5/§6.7 cap or budget decision (PREREGISTERED.md
#                              :243, :525, :544): changes no analysis rule, needs no
#                              deposit (DECISIONS.md "Budget extensions in AMENDMENT.md").
# <n> has no leading zero; the date is mandatory.
SECTION_RE = re.compile(r"## ([AE][1-9][0-9]*) \((\d{4}-\d{2}-\d{2})\)(?:[ :].*)?", re.ASCII)
TITLE_RE = re.compile(r"# \S.*")
# heading-like: '#' after optional indentation and any blockquote / list markers
HEADING_LIKE_RE = re.compile(r"[ \t]*(?:(?:>|[-*+]|[0-9]+[.)])[ \t]*)*#")
CONTAINER_RE = re.compile(r"[ \t]*(?:(?:>|[-*+]|[0-9]+[.)])[ \t]+|>)*")   # blockquote / list prefixes
SETEXT_RE = re.compile(r"[ \t]*(=+|-+)[ \t]*")
# an HTML block start (any tag at the start of a line, also inside containers):
# such blocks can hide or fake content, so they close the guard
HTML_BLOCK_RE = re.compile(r"[ \t]*(?:>[ \t]*)*<[A-Za-z/!?]")
# constructs that can hide or fake structure are not allowed at all (fail closed)
FORBIDDEN_RE = re.compile(r"```|~~~|<!--|-->|<\s*/?\s*(pre|h[1-6])\b", re.IGNORECASE)
DEPOSITED_PREFIX = "**Deposited:** "


def _checked(cell):
    """(doi, date) if `cell` is a valid deposit cell under every closing check."""
    m = CELL_RE.fullmatch(cell)
    if m is None:
        return None
    doi, date = m.group(1), m.group(2)
    if PLACEHOLDER_RE.search(doi):
        return None
    if doi.startswith(TEST_DOI_PREFIXES) or "sandbox" in doi.lower():
        return None
    try:
        d = datetime.date.fromisoformat(date)
    except ValueError:
        return None
    if d < MIN_DATE or d > _today():
        return None
    return doi, date


def _amendment_lines(text):
    """The lines of AMENDMENT.md (BOM dropped, CRLF/CR normalised), or None if
    the file uses a construct that could hide or fake structure: a code fence,
    an HTML comment, or a <pre> / <h1>..<h6> tag."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    if FORBIDDEN_RE.search(text):
        return None
    return text.split("\n")


def amendment_status(plan_path=PLAN, required=None):
    """{"A<n>": (doi, date) or None, "E<n>": "exempt"} for AMENDMENT.md beside the
    plan, or None if the file is unreadable or structurally unsafe (fail closed):
    a forbidden construct (fence, comment, <pre>, <h*>), any heading-like line
    (also inside a blockquote or list item) other than one level-1 title followed
    by dated "## A<n> (date)" / "## E<n> (date)" sections, a setext heading, a
    duplicated section, a "**Deposited:**" line outside an A section, or a
    required section that is missing (a missing file counts as having none).
    An A section's deposit counts only if its DOI is used by no other A section
    and its date is not earlier than the section's heading date.
    `required` defaults to REQUIRED_SECTIONS for the real plan, else to none."""
    plan_abs = os.path.abspath(plan_path)
    if required is None:
        required = REQUIRED_SECTIONS if plan_abs == os.path.abspath(PLAN) else frozenset()
    path = os.path.join(os.path.dirname(plan_abs), AMENDMENT_NAME)
    if not os.path.exists(path):
        return None if required else {}
    try:
        with open(path, encoding="utf-8") as fh:
            lines = _amendment_lines(fh.read())
    except (OSError, ValueError):
        return None
    if lines is None:
        return None
    status, seen, hdate = {}, {}, {}
    current, title_seen, prev = None, False, ""
    for line in lines:
        if HTML_BLOCK_RE.match(line):
            return None                    # an HTML block (script, style, div, ...)
        # rstrip first: "- " / "> - " is a lone "-" underline, not an empty list item
        bare, prev_bare = line.rstrip(), prev.rstrip()
        inner = bare[CONTAINER_RE.match(bare).end():]
        prev_inner = prev_bare[CONTAINER_RE.match(prev_bare).end():]
        if SETEXT_RE.fullmatch(inner) and prev_inner.strip():
            return None                    # "text" + "===" / "---" (also inside a quote): setext heading
        if HEADING_LIKE_RE.match(line):
            m = SECTION_RE.fullmatch(line.rstrip())
            if m:
                try:                       # the heading date must be a real date in range
                    hd = datetime.date.fromisoformat(m.group(2))
                except ValueError:
                    return None
                if hd < MIN_DATE or hd > _today():
                    return None
                current = m.group(1)
                if current in status:      # a duplicated section name
                    return None
                status[current] = "exempt" if current[0] == "E" else None
                seen[current], hdate[current] = 0, m.group(2)
            elif TITLE_RE.fullmatch(line.rstrip()) and not title_seen and current is None:
                title_seen = True
            else:
                return None                # any other heading form: unknown structure
        elif line.lstrip().startswith("**Deposited:**"):
            if current is None or current[0] != "A":
                return None                # a deposit line outside an A section
            seen[current] += 1
            status[current] = (_checked(line[len(DEPOSITED_PREFIX):].rstrip())
                               if line.startswith(DEPOSITED_PREFIX) else None)
        prev = line
    for sec, n in seen.items():
        if sec[0] == "A" and n != 1:
            status[sec] = None
    dois = [v[0].casefold() for sec, v in status.items() if sec[0] == "A" and v is not None]
    for sec, v in list(status.items()):
        if sec[0] != "A" or v is None:
            continue
        if dois.count(v[0].casefold()) > 1 or v[1] < hdate[sec]:
            status[sec] = None             # a shared DOI, or deposited before it was written
    if not set(required) <= set(status):
        return None
    return status


def deposit_recorded(plan_path=PLAN, required=None):
    """True only if line 8 is `| Public timestamp | https://doi.org/<DOI> (YYYY-MM-DD) |`
    and every "## A<n>" section of AMENDMENT.md carries its own valid deposit line,
    whose DOI differs from the plan's (case-insensitively) and is dated no earlier."""
    ref = deposit_reference(plan_path)
    if ref is None:
        return False
    amend = amendment_status(plan_path, required)
    if amend is None:
        return False
    for sec, val in amend.items():
        if sec[0] != "A":
            continue
        if val is None or val[0].casefold() == ref[0].casefold() or val[1] < ref[1]:
            return False
    return True
