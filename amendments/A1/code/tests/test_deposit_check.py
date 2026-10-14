"""Tests for the shared real-data guard deposit_check.py (DECISIONS.md 2026-10-13,
"Deposit-line format and a single shared check"; attack strings from
reviews/CODE-T04T07__review_3.md finding 2 and review 2 finding 3).

Run: .tabpfn_env/bin/python -m pytest experiments/revision_r1/tests/test_deposit_check.py -q
(no TabPFN needed; also runs under ./.venv)
"""
import datetime
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import deposit_check as dc  # noqa: E402

CANONICAL = "https://doi.org/10.5281/zenodo.17345678 (2026-10-20)"
TODAY = datetime.date(2026, 10, 20)       # injected "today": tests are time-stable


REAL_TODAY = dc._today                    # the module's real UTC clock


@pytest.fixture(autouse=True)
def fixed_today(monkeypatch):
    """Pin the upper-bound reference date (deposit_check._today) for every
    test; test_real_plan_is_closed restores the real clock itself."""
    monkeypatch.setattr(dc, "_today", lambda: TODAY)


def plan(tmp_path, cell, line=8, raw_row=None):
    """A plan file whose line `line` is the Public-timestamp row with `cell`."""
    lines = [f"filler {i}" for i in range(1, 12)]
    lines[line - 1] = raw_row if raw_row is not None else f"| Public timestamp | {cell} |"
    p = tmp_path / "P.md"
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return str(p)


CLOSED = [
    # placeholders and the current wording
    "**PENDING (user action).** Before step 1 of either queue ...",
    "PENDING", "pending", "Pending", "TBD", "tbd", "", " ", "to be filled", "to be filled at deposit",
    "https://doi.org/10.5281/zenodo.NNNNNNN (2026-10-20)",
    "https://doi.org/10.5281/zenodo.XXXXXXX (2026-10-20)",
    "https://doi.org/10.5281/zenodo... (2026-10-20)",
    "https://doi.org/<DOI> (YYYY-MM-DD)",
    "https://doi.org/10.5281/zenodo.17345678 (YYYY-MM-DD)",
    "https://doi.org/10.5281/zenodo.17345678 (2026-13-45)",          # not a date
    # free text around a URL or DOI (review 3 probe table)
    "not yet 10.5281/zenodo.17345678",
    "Zenodo upload in progress https://zenodo.org/x",
    "awaiting DOI (will be 10.5281/zenodo.NNNNNNN)",
    "https://doi.org/10.5281/zenodo.NNNNNNN once uploaded",
    "https://doi.org/10.5281/zenodo.17345678 once uploaded",
    "(user action) https://zenodo.org/deposit/new",
    "draft record https://zenodo.org/deposit/123 (unpublished)",
    "https://zenodo.org/deposit/17345678 (2026-10-20)",               # unpublished draft URL
    "https://zenodo.org/records/17345678 (2026-10-20)",               # not the doi.org form
    "https://osf.io/abcd2/ (2026-10-20)",
    "10.5281/zenodo.17345678 (2026-10-20)",                           # bare DOI
    "https://doi.org/10.5281/zenodo.17345678",                        # no date
    "https://doi.org/10.5281/zenodo.17345678 (2026-10-20) see README",  # trailing text
    "see https://doi.org/10.5281/zenodo.17345678 (2026-10-20)",       # leading text
    "https://doi.org/10.5281/zenodo.17345678  (2026-10-20)",          # two spaces
    "https://doi.org/10.5281/zenodo.17345678(2026-10-20)",            # no space
    "http://doi.org/10.5281/zenodo.17345678 (2026-10-20)",            # http
    "https://dx.doi.org/10.5281/zenodo.17345678 (2026-10-20)",        # other host
    "https://doi.org.evil.com/10.5281/zenodo.17345678 (2026-10-20)",
    "https://evil.com/https://doi.org/10.5281/zenodo.17345678 (2026-10-20)",
    "https://doi.org/11.5281/zenodo.17345678 (2026-10-20)",           # not a DOI prefix
    "**https://doi.org/10.5281/zenodo.17345678 (2026-10-20)**",       # bold
    "<!-- https://doi.org/10.5281/zenodo.17345678 (2026-10-20) -->",  # HTML comment
    "~~https://doi.org/10.5281/zenodo.17345678 (2026-10-20)~~",       # strikethrough
    "`https://doi.org/10.5281/zenodo.17345678 (2026-10-20)`",         # code span
    "[DOI](https://doi.org/10.5281/zenodo.17345678) (2026-10-20)",    # markdown link
    "https://doi.org/10.5281/zenodo.17345678 (2026-10-20T06:47:47Z)",  # not the date form
    "https://doi.org/10.5281/zenodo.17345678 (2026-10-20); PENDING",
]
OPEN = [
    CANONICAL,
    "https://doi.org/10.17605/OSF.IO/ABCD2 (2026-10-20)",
    "https://doi.org/10.5281/zenodo.1 (2026-10-13)",                   # first allowed day
]


@pytest.mark.parametrize("cell", CLOSED)
def test_closed(tmp_path, cell):
    assert dc.deposit_recorded(plan(tmp_path, cell)) is False


@pytest.mark.parametrize("cell", OPEN)
def test_open(tmp_path, cell):
    assert dc.deposit_recorded(plan(tmp_path, cell)) is True


def test_reference_returned(tmp_path):
    assert dc.deposit_reference(plan(tmp_path, CANONICAL)) == ("10.5281/zenodo.17345678",
                                                               "2026-10-20")
    assert dc.deposit_reference(plan(tmp_path, "PENDING")) is None


def test_cell_padding_is_tolerated_but_nothing_else(tmp_path):
    raw = f"| Public timestamp |   {CANONICAL}   |"
    assert dc.deposit_recorded(plan(tmp_path, None, raw_row=raw)) is True
    raw = f"| Public timestamp | {CANONICAL} | extra |"
    assert dc.deposit_recorded(plan(tmp_path, None, raw_row=raw)) is False
    raw = f"| Public timestamp | {CANONICAL}"                     # row not closed
    assert dc.deposit_recorded(plan(tmp_path, None, raw_row=raw)) is False


def test_only_line_8_counts(tmp_path):
    for line in (7, 9, 1):
        assert dc.deposit_recorded(plan(tmp_path, CANONICAL, line=line)) is False
    raw = f"| Deposited version | {CANONICAL} |"                    # right line, wrong row
    assert dc.deposit_recorded(plan(tmp_path, None, raw_row=raw)) is False
    raw = f"|Public timestamp| {CANONICAL} |"                      # different row spelling
    assert dc.deposit_recorded(plan(tmp_path, None, raw_row=raw)) is False


def test_missing_or_short_file(tmp_path):
    assert dc.deposit_recorded(str(tmp_path / "absent.md")) is False
    p = tmp_path / "short.md"
    p.write_text(f"| Public timestamp | {CANONICAL} |\n")
    assert dc.deposit_recorded(str(p)) is False


@pytest.mark.skipif(not os.path.exists(dc.PLAN),
                    reason="the real plan is not beside deposit_check.py (e.g. in the public deposit)")
def test_real_plan_records_the_deposit(monkeypatch):
    """Was test_real_plan_is_closed until the deposit (2026-10-13, commit 9b17f00).
    Line 8 holds exactly the published record (real clock). The guard as a whole
    is open only if every amendment in AMENDMENT.md also carries its own deposit
    (A1 review 1, finding 5)."""
    monkeypatch.setattr(dc, "_today", REAL_TODAY)
    with open(dc.PLAN, encoding="utf-8") as fh:
        assert fh.read().split("\n")[7] == \
            "| Public timestamp | https://doi.org/10.5281/zenodo.23341630 (2026-10-13) |"
    ref = dc.deposit_reference()
    assert ref == ("10.5281/zenodo.23341630", "2026-10-13")
    status = dc.amendment_status()
    assert status is not None and "A1" in status
    expected = all(v is not None and v[0] != ref[0] and v[1] >= ref[1] for v in status.values())
    assert dc.deposit_recorded() is expected


# ------------------------------------------- amendments (A1 reviews 1-3)
A_OK = "**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-20)"
A2_OK = A_OK.replace("17345699", "17345700")
H1 = "## A1 (2026-10-13): x"
H2 = "## A2 (2026-10-14): y"
A1_OK = (f"# Amendments\n\nintro mentions `**Deposited:** https://doi.org/<DOI> (YYYY-MM-DD)`"
         f" and `## A<n>`\n\n---\n\n{H1}\n\n{A_OK}\n\nbody\n")


def plan_with_amendment(tmp_path, body, newline="\n"):
    p = plan(tmp_path, CANONICAL)
    (tmp_path / "AMENDMENT.md").write_bytes(body.replace("\n", newline).encode("utf-8"))
    return p


def test_no_amendment_file_adds_no_condition(tmp_path):
    assert dc.deposit_recorded(plan(tmp_path, CANONICAL)) is True
    assert dc.amendment_status(plan(tmp_path, CANONICAL)) == {}


def test_file_without_sections_adds_no_condition(tmp_path):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, "# Amendments\n\ntext\n")) is True


def test_reference_file_opens(tmp_path):
    p = plan_with_amendment(tmp_path, A1_OK)
    assert dc.amendment_status(p) == {"A1": ("10.5281/zenodo.17345699", "2026-10-20")}
    assert dc.deposit_recorded(p) is True


@pytest.mark.parametrize("newline", ["\r\n", "\r"])
def test_crlf_and_cr_files(tmp_path, newline):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, A1_OK, newline)) is True
    pending = A1_OK.replace(A_OK, "**Deposited:** pending")
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, pending, newline)) is False
    second = A1_OK + f"\n{H2}\n\nno deposit\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, second, newline)) is False


@pytest.mark.parametrize("line", [
    "**Deposited:** pending (Zenodo v1.1)",
    "**Deposited:** https://doi.org/10.5281/zenodo.NNNNNNN (2026-10-20)",
    "**Deposited:** https://doi.org/10.5072/zenodo.17345699 (2026-10-20)",       # sandbox
    "**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-21)",       # future
    "**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-20) and more",
    "**Deposited:**https://doi.org/10.5281/zenodo.17345699 (2026-10-20)",        # no space
    "**Deposited:** https://doi.org/10.5281/zenodo.17345678 (2026-10-20)",       # = plan DOI
    "**Deposited:** https://doi.org/10.5281/ZENODO.17345678 (2026-10-20)",       # = plan DOI, case
    " **Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-20)",      # indented
    "Deposited: https://doi.org/10.5281/zenodo.17345699 (2026-10-20)",           # not the form
    "**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-12)",       # before heading
])
def test_undeposited_amendment_closes(tmp_path, line):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, f"{H1}\n{line}\n")) is False


def test_amendment_dated_before_plan_closes(tmp_path):
    p = plan(tmp_path, "https://doi.org/10.5281/zenodo.17345678 (2026-10-15)")
    (tmp_path / "AMENDMENT.md").write_text(
        "## A1 (2026-10-13)\n**Deposited:** https://doi.org/10.5281/zenodo.17345699 (2026-10-14)\n")
    assert dc.deposit_recorded(p) is False


def test_every_section_needs_its_own_line_and_doi(tmp_path):
    cases = {
        f"{H1}\n{A_OK}\n{H2}\nno line here\n": False,
        f"{H1}\n{A_OK}\n{A_OK}\n": False,                                  # two lines
        f"{H1}\n{A_OK}\n## A1 (2026-10-14) again\n{A2_OK}\n": False,       # duplicate name
        f"{H1}\n{A_OK}\n{H2}\n{A_OK}\n": False,                            # A1's line copied into A2
        f"{H1}\n{A_OK}\n{H2}\n{A_OK.replace('zenodo', 'ZENODO')}\n": False,  # copied, case changed
        f"{H1}\n{A_OK}\n{H2}\n{A2_OK}\n": True,
        f"{H1}\n{A_OK}\n## A2 (2026-10-21): later\n{A2_OK}\n": False,       # deposit before heading
    }
    for body, want in cases.items():
        assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is want, body


@pytest.mark.parametrize("heading", [
    "### A2", "##A2", " ## A2", "## A2a", "## Amendment A2: x", "## a2", "# A2", "##\tA2",
    "## A\uff12", "## Budget extension 2026-11-01", "## A02 (2026-10-14)", "#### notes",
    "# Second title", "## A2", "## A2 x", "## A2: x", "## A2 (x)", "## E1", "## E1 budget",
    "> ## A2 (2026-10-14)", ">## A2", "- ## A2 (2026-10-14)", "* ## A2", "+ ## A2",
    "1. ## A2 (2026-10-14)", "2) ## A2", "> - ## A2", "    ## A2 (2026-10-14)", "\t## A2",
])
def test_unknown_heading_closes(tmp_path, heading):
    body = A1_OK + f"\n{heading}\n\ntext without a deposit line\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is False


@pytest.mark.parametrize("snippet", [
    "```\n## A2 (2026-10-14)\n```", "~~~\ntext\n~~~", "    ```\n## A2 (2026-10-14)\n    ```",
    "<!-- note -->", "<!--", "-->", "`<!--` and later `-->`", "<pre>\n" + A2_OK + "\n</pre>",
    "<h2>A2</h2>", "<H3>x</H3>", "< h2 >A2</ h2>", "````\n```\n" + A2_OK + "\n```\n````",
])
def test_forbidden_constructs_close(tmp_path, snippet):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, A1_OK + "\n" + snippet + "\n")) is False


def test_budget_extension_sections_are_exempt(tmp_path):
    body = A1_OK + "\n## E1 (2026-10-15): budget extension for unit X\n\nno deposit line\n"
    p = plan_with_amendment(tmp_path, body)
    assert dc.amendment_status(p)["E1"] == "exempt"
    assert dc.deposit_recorded(p) is True
    bad = A1_OK + "\n## E1 (2026-10-15)\n" + A2_OK + "\n"        # a deposit line in an E section
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, bad)) is False


@pytest.mark.parametrize("body", [
    "\ufeff## A1 (2026-10-13) x\npending\n",                  # BOM before a pending section
    "## A1 (2026-10-13) x\n**Deposited:** pending\n",
    "Amendment one\n=============\n" + A1_OK,                 # setext heading
    "Amendment one\n---\n" + A1_OK,
    f"{A_OK}\n" + A1_OK,                                       # deposit line outside a section
])
def test_unsafe_structure_closes(tmp_path, body):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is False


def test_bom_is_dropped_for_a_valid_file(tmp_path):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, "\ufeff" + A1_OK)) is True


def test_unreadable_amendment_closes(tmp_path):
    p = plan(tmp_path, CANONICAL)
    (tmp_path / "AMENDMENT.md").write_bytes(b"## A1 (2026-10-13)\n\xff\xfe bad\n")
    assert dc.amendment_status(p) is None
    assert dc.deposit_recorded(p) is False


def test_required_sections_explicit(tmp_path):
    p = plan(tmp_path, CANONICAL)
    assert dc.deposit_recorded(p, required={"A1"}) is False         # no file at all
    (tmp_path / "AMENDMENT.md").write_text("", encoding="utf-8")
    assert dc.deposit_recorded(p, required={"A1"}) is False         # empty file
    (tmp_path / "AMENDMENT.md").write_text(A1_OK.replace("## A1", "## A2"), encoding="utf-8")
    assert dc.deposit_recorded(p, required={"A1"}) is False         # A1 renamed
    (tmp_path / "AMENDMENT.md").write_text(A1_OK, encoding="utf-8")
    assert dc.deposit_recorded(p, required={"A1"}) is True


def test_real_plan_applies_required_sections_by_default(tmp_path, monkeypatch):
    """A1 review 3, F4: REQUIRED_SECTIONS is applied to the real plan without
    being asked for: with dc.PLAN pointing at a tmp plan, a missing, empty or
    renamed A1 closes the guard under the DEFAULT `required`."""
    p = plan(tmp_path, CANONICAL)
    monkeypatch.setattr(dc, "PLAN", p)
    assert "A1" in dc.REQUIRED_SECTIONS
    assert dc.deposit_recorded(p) is False                           # no AMENDMENT.md
    (tmp_path / "AMENDMENT.md").write_text("", encoding="utf-8")
    assert dc.deposit_recorded(p) is False
    (tmp_path / "AMENDMENT.md").write_text(A1_OK.replace("## A1", "## A2"), encoding="utf-8")
    assert dc.deposit_recorded(p) is False
    (tmp_path / "AMENDMENT.md").write_text(A1_OK, encoding="utf-8")
    assert dc.deposit_recorded(p) is True


@pytest.mark.skipif(not os.path.exists(os.path.join(os.path.dirname(dc.PLAN), "AMENDMENT.md")),
                    reason="the real AMENDMENT.md is not beside deposit_check.py (e.g. in the public deposit)")
def test_real_amendment_file_opens_once_a1_is_deposited(tmp_path):
    """The real AMENDMENT.md, with only its A1 deposit line filled in, opens the
    guard (so the guard will not stay shut after the v1.1 deposit)."""
    real = open(os.path.join(os.path.dirname(dc.PLAN), "AMENDMENT.md"), encoding="utf-8").read()
    pending = [l for l in real.split("\n") if l.startswith("**Deposited:**")]
    assert len(pending) == 1
    filled = real.replace(pending[0], A_OK)
    p = plan_with_amendment(tmp_path, filled)
    assert dc.deposit_recorded(p, required={"A1"}) is True


# ------------------------------------------------- A1 review 4 (N1, N2)
@pytest.mark.parametrize("snippet", [
    "> A2 (2026-10-14)\n> ---",                       # setext heading inside a blockquote
    "> A2\n> ===",
    "- A2\n  ---",
    "<script>\n" + A2_OK + "\n</script>",
    "<style>x</style>",
    "<div hidden>\n" + A2_OK + "\n</div>",
    "> <div>x</div>",
    "<!DOCTYPE x>",
])
def test_review4_hidden_structure_closes(tmp_path, snippet):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, A1_OK + "\n" + snippet + "\n")) is False


@pytest.mark.parametrize("heading", [
    "## A2 (0000-00-00)", "## A2 (2026-02-30)", "## A2 (2026-10-00)", "## E1 (9999-99-99)",
    "## A2 (2026-10-12)",          # before the earliest possible date
    "## E1 (2026-10-21)",          # after today (pinned 2026-10-20)
])
def test_heading_dates_must_be_real_and_in_range(tmp_path, heading):
    body = A1_OK + f"\n{heading}\n" + (A2_OK if heading.startswith("## A") else "text") + "\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is False


def test_plain_list_and_rule_lines_still_allowed(tmp_path):
    body = A1_OK + "\n- item one\n- item two\n\n---\n\n> a quoted line\n\n1. numbered\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is True


# ------------------------------------------------- A1 review 5 (F1 + test gaps)
@pytest.mark.parametrize("snippet", [
    "A2 (2026-10-14): new rule\n-",                     # single-dash setext underline
    "> A2 (2026-10-14): new rule\n> -",
    "- A2 (2026-10-14): new rule\n  -",
    "> A2\n>---",                                        # no space after '>'
])
def test_single_dash_and_compact_setext_close(tmp_path, snippet):
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, A1_OK + "\n" + snippet + "\n")) is False


def test_heading_dated_today_is_accepted(tmp_path):
    body = A1_OK + "\n## A2 (2026-10-20): today\n" + A2_OK + "\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is True


# ------------------------------------------------- A1 review 6 (F3)
@pytest.mark.parametrize("underline", ["- ", "-\t", "> - ", "  - "])
def test_lone_dash_underline_with_trailing_space_closes(tmp_path, underline):
    prev = "> A2 (2026-10-14): new rule" if underline.startswith(">") else "A2 (2026-10-14): new rule"
    body = A1_OK + "\n" + prev + "\n" + underline + "\n"
    assert dc.deposit_recorded(plan_with_amendment(tmp_path, body)) is False
