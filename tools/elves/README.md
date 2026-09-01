# Elf Outreach - Public-Prospect Research and Manual-Send Drafts

Phase 5: research public prospects, generate bilingual outreach drafts, and
track the manual-send workflow. **This tool sends nothing, ever.**

**What it does:** records PUBLIC business prospects (schools, HOAs,
businesses, nonprofits, community events) researched through a public contact
path, and generates one deterministic English + Spanish outreach draft per
prospect from a per-category template. Every draft introduces Miami Papa Noel
santa visits, the bilingual service, the public phone 786-975-9557 and
santa@miamipapanoel.com, and asks who coordinates holiday events.

**What it never does:** send, post, publish, call, or submit anything
anywhere. There is no send path and no bulk path. A human sends each approved
draft manually via the prospect's public contact path, one at a time, and
records the fact afterwards. It never claims an affiliation, partnership,
endorsement, or insurance - those words are refused even in operator-supplied
custom lines.

---

## The state machine

```
RESEARCHED -> DRAFTED -> APPROVED_FOR_MANUAL_SEND -> SENT_BY_HUMAN
                  DO_NOT_CONTACT (terminal, reachable from any state)
```

- `SENT_BY_HUMAN` is recorded **after the fact** with `--operator` and
  `--sent-via`. The tool cannot cause a send; it can only record that a
  human made one.
- `DO_NOT_CONTACT` (the `suppress` command) is terminal and sticky. A
  suppressed prospect is never drafted, approved, or contacted again.

## The guards

| Guard | Refuses |
|---|---|
| Contact path | Any prospect without a public contact path (URL, public form, or public email) |
| Personal email | `firstname.lastname` at gmail/yahoo/hotmail/outlook - public org addresses (`info@`, `office@`, `frontdesk@`) and org domains are fine |
| Category | Anything outside school, hoa, business, nonprofit, community_event |
| Org name | Names containing "job board", "indeed", "linkedin jobs", "craigslist" |
| Draft cap | Drafting when 15 prospects already sit in DRAFTED (anti-spam: drafts get sent and recorded, not stockpiled) |
| Custom line | "affiliated", "official partner", "endorsed", "on behalf of", "insured", "certificate of insurance" |

**Do not edit the guards to get past a refusal. The refusal is the product.**

---

## Daily use

```powershell
cd "C:\Users\Green Machine\miami-papa-noel"

# 1. Record a researched prospect (public contact path required)
python tools\elves\outreach.py add --org "Example Elementary School" --category school --city Doral --contact "frontdesk@example-school.org" --notes "PTA runs a winter fair"

# 2. Generate the bilingual draft (prints it; sends nothing)
python tools\elves\outreach.py draft --ref P-001

# 3. A human reads the draft and approves it
python tools\elves\outreach.py approve --ref P-001 --operator "Marcelo"

# 4. The human sends it MANUALLY via the public contact path, then records it
python tools\elves\outreach.py record-sent --ref P-001 --operator "Marcelo" --sent-via "school contact form"

# A prospect that must never be contacted (terminal)
python tools\elves\outreach.py suppress --ref P-002 --reason "asked not to be contacted"

# Overview and audit trail
python tools\elves\outreach.py list
python tools\elves\outreach.py audit
```

`draft --custom-line "..."` adds one operator-written line to the draft;
lines containing affiliation or insurance claims are refused.

## Storage

Prospect records live OUTSIDE the repository, never committed:

| Path | Contents |
|---|---|
| `%LOCALAPPDATA%\MiamiPapaNoel\elves\prospects.json` | Current record per prospect |
| `%LOCALAPPDATA%\MiamiPapaNoel\elves\outreach-log.jsonl` | Append-only audit trail |

Override the directory with the `MPN_ELVES_DIR` environment variable
(the tests always do; they never touch the real store).

---

## Tests

```powershell
python -m pytest tools\elves\test_elves.py -q
```

16 tests, all synthetic: contact-path and personal-email guards, job-board
and category refusals, the sticky DO_NOT_CONTACT state, the 15-draft cap,
bilingual draft content (phone + email present, affiliation words absent,
ASCII only, deterministic), forbidden custom lines, operator requirements,
the full legal path to SENT_BY_HUMAN, and a source-level check that the tool
imports no network or send capability.

## Files

| File | Purpose |
|---|---|
| `outreach.py` | The operator tool |
| `test_elves.py` | 16 tests, all synthetic |
| `README.md` | This file |
