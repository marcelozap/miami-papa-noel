# Agent Workflow Architecture

Miami Papa Noel seasonal operations, 2026 season.

Every component below carries a build state. Nothing is described as running
unless it runs.

| State | Meaning |
|---|---|
| **LIVE-AI** | Deployed software with a successful, configured model-assisted step |
| **LIVE-AUTOMATED** | Deployed deterministic software step that runs without a model |
| **LIVE-MANUAL** | Operating today, performed by a human following a documented procedure |
| **DESIGNED** | Specified in the repository, not yet built |
| **PLANNED** | Intended after the first deployment proves out |

**Prior season:** the role-based workflow operated during the 2025 Christmas
season per `docs/operator-attestation-2025-season.md`. The 2026 architecture
below is a strengthening of that workflow, not a first attempt at it.

---

## 1. Canonical state graph

```
   lead ──▶ quote ──▶ schedule ──▶ payment receipt ──▶ confirmation ──▶ follow-up
```

Expanded to the real operational path, with build state per step:

```
  inbound inquiry  (Instagram DM · WhatsApp · email · phone · web form · referral)
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ INTAKE + TRIAGE          LIVE-AI / AUTOMATED │  tools/triage/triage.py
  │  language · date · category · location       │
  │  contact status · missing fields             │
  └──────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ SCHEDULE / CAPACITY RISK FLAG   LIVE-AUTOMATED│  first-to-fill dates,
  │  high · elevated · moderate · low · unknown  │  December weekend weighting
  └──────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ SLOT CHECK                     LIVE-MANUAL   │  business/december-slot-board.html
  │  operator reads the board before promising   │  scripts/validate_slot_confirmations.py
  └──────────────────────────────────────────────┘
        │
        ├── conflict ──▶ offer alternative dates ──▶ (loop) or END
        │
        ▼ open | tight
  ┌──────────────────────────────────────────────┐
  │ QUOTE + PRICING GUARD         LIVE-AUTOMATED │  locked pricing.json v2026-08-28.1
  │  base · travel · deposit 50%                 │  FAIL on any unlocked figure
  └──────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ BILINGUAL DRAFT (EN + ES)   LIVE-AI / AUTOMATED│  parity enforced
  └──────────────────────────────────────────────┘
        │
        ▼
  ╔══════════════════════════════════════════════╗
  ║ OPERATOR REVIEW                LIVE-MANUAL   ║  ◀── mandatory, unskippable
  ║  APPROVE / reject. Nothing auto-sends.       ║      no send path exists
  ╚══════════════════════════════════════════════╝
        │ approved
        ▼
  ┌──────────────────────────────────────────────┐
  │ SEND                           LIVE-MANUAL   │  operator copies into the channel
  │  sent_at recorded by hand                    │
  └──────────────────────────────────────────────┘
        │
        ├── no deposit ──▶ FOLLOW-UP ×2 ──▶ release hold ──▶ LAPSED   LIVE-MANUAL
        │
        ▼ Zelle deposit received
  ┌──────────────────────────────────────────────┐
  │ PAYMENT RECEIPT                LIVE-MANUAL   │  match amount · sender · date
  │  Zelle only, human-verified                  │  business/booking-sop.md
  └──────────────────────────────────────────────┘
        │
        ▼
  ┌──────────────────────────────────────────────┐
  │ CONFIRMATION                   LIVE-MANUAL   │  gates G1 + G2 + G3
  │  only a human confirms                       │
  └──────────────────────────────────────────────┘
        │
        ▼
  LOGISTICS / ROUTE  LIVE-MANUAL  ──▶  EVENT  (human)  ──▶  BALANCE  LIVE-MANUAL
        │
        ▼
  FOLLOW-UP → REVIEW / REFERRAL  LIVE-MANUAL  ──▶  ANALYTICS  PLANNED
```

---

## 2. Roles

### 2a. Operating roles — `business/AGENT-ROLES.md` (2026-08-26)

The four roles the business runs on. Each is a **defined responsibility with a
documented procedure**, performed by the operator, now partly tool-assisted.

| Role | Owns | Tool support today |
|---|---|---|
| **Scout** | Lead pipeline, prospect research, outreach lists | `LIVE-MANUAL` |
| **Dispatcher** | Outbound campaigns, batches, follow-up cadence | `LIVE-MANUAL` |
| **Concierge** | Inbound inquiries, quoting, bilingual replies | **`LIVE-AI` when configured; `LIVE-AUTOMATED` fallback** — triage tool |
| **Bookkeeper** | Closing, deposits, receipts, settlement | `LIVE-MANUAL` |

The triage tool is the first role to receive software support. The other three
have documented procedures and are candidates in the same pattern.

### 2b. Automated component — the only one

| Component | Inputs | Outputs | Approval | State |
|---|---|---|---|---|
| **Inquiry triage** | Raw inquiry text, `pricing.json`, channel | Structured fields, risk flag, EN+ES drafts, validation findings, log line | **Human approval required before any use** | `LIVE-AI` when configured; `LIVE-AUTOMATED` fallback |

### 2c. Event and service roles — human, physical

Mr. Claus · Mrs. Claus · elf · photographer, engaged per event. School, HOA,
corporate, and family bookings each carry their own logistics requirements
documented in `business/booking-sop.md`. **None of this is automated and none of
it is proposed for automation.**

### 2d. Explicitly not automated

- **Phone calls** — no telephony integration exists or is planned
- **WhatsApp / Instagram sending** — no messaging integration. Drafts are copied by a person
- **Payment** — **Zelle only, human-initiated and human-verified.** No processor, no card handling, no online payment acceptance. The workflow records a receipt after a human confirms funds arrived; it never moves money
- **Booking confirmation** — only a human confirms, and only after the deposit clears

---

## 3. Human approval points

Three, all mandatory:

1. **Before any message reaches a customer.** Every draft is approved, edited, or rejected by the operator. There is no unattended send path — the tool has no network egress to a customer channel at all.
2. **Before a hold becomes a booking.** The operator confirms the Zelle deposit actually arrived.
3. **Before a validation gate is overridden.** Only the operator can override, and the override is recorded in the log.

Human-in-the-loop is the intended production posture, not a temporary limitation.

---

## 4. Control gates

| Gate | Question | Blocks | State |
|---|---|---|---|
| **G1** | Does this overlap an existing booking, including travel time? | confirmation | `LIVE-MANUAL` + risk flag from `LIVE-AUTOMATED` |
| **G2** | Has the Zelle deposit been received and matched? | confirmation | `LIVE-MANUAL` |
| **G3** | Does the day stay inside capacity limits? | confirmation | `LIVE-MANUAL` |
| **G4** | Is every quoted figure in the locked price list? | draft approval | **`LIVE-AUTOMATED`** — enforced |
| **G5** | Has a human approved this message? | any send | **`LIVE-AUTOMATED`** — enforced |
| **G6** | Was a log line written for this inquiry? | — | **`LIVE-AUTOMATED`** — automatic |
| **G7** | Do EN and ES state identical terms? | draft approval | **`LIVE-AUTOMATED`** — enforced |
| **G8** | Is the draft free of confirmation and insurance language? | draft approval | **`LIVE-AUTOMATED`** — enforced |

Capacity is one person. G1-G3 exist because Santa cannot be in Doral and Kendall
at once, and because a date given away without a deposit is a date sold twice.

---

## 5. Failure states and manual fallback

| Failure | Detection | Response | Fallback |
|---|---|---|---|
| Required fields missing | `missing_information` | Draft asks the customer; never quotes blind | Operator asks the standard questions |
| Date not stated | extractor returns `null` | Risk marked `unknown` — **never guessed** | Operator asks |
| Calendar conflict | G1 / G3 | No quote; offer alternatives | Slot board read directly |
| Unlocked price appears | G4 | `blocked_by_validation`, approval refused | Operator prices from `checkout.html` |
| EN/ES terms diverge | G7 | Blocked | Operator writes both by hand |
| Confirmation or insurance language | G8 | Blocked | Operator rewrites |
| Non-Zelle method appears | `payment_method` | Blocked | Zelle only, always |
| **Model or subscription unavailable** | import/key check | **Automatic fall back to deterministic mode.** Logged `fallback_used: true` | No customer-visible change |
| **Tool entirely unavailable** | — | Manual procedure, `tools/triage/README.md` | Full price table and rules printed there |
| Machine loss | — | Repository clone + published `checkout.html` | Prices are public on the site |

**The fallback is a design constraint.** The business earns most of its year in
six weeks and cannot pause for an outage, so nothing here is permitted to become
load-bearing for something the operator cannot do by hand within the hour.

---

## 6. Audit trail

One append-only JSONL line per inquiry: identity, timing, extraction, risk,
model, prompt version, price list version, reviewer, approval, outcome, error
code, and whether the fallback path ran.

Message bodies and draft bodies are deliberately excluded. Location is a coarse
area, never a street address. Contact status records *whether* a phone or email
was given, never the value.

Schema and derived metrics: `tools/triage/log-schema.md`.
