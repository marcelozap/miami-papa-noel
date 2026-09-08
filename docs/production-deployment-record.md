# Production Deployment Record

**Deployment:** Miami Papa Noel — AI-assisted bilingual inquiry triage
**Recorded:** 2026-08-29
**Repository:** `miami-papa-noel` (77 commits, 2026-06-10 → 2026-08-29)

---

## Identification

| Field | Value |
|---|---|
| **Deployment name** | Bilingual Inquiry Triage with Human Approval |
| **Operator organization** | XIV (Marcelo Zapata) |
| **Business served** | Miami Papa Noel — bilingual Santa appearance and booking business, Miami-Doral and surrounding areas |
| **Relationship** | Miami Papa Noel is a family business with distinct principals: Walter Zapata owns and operates the Santa visit service; the performers are experienced but not technical. Marcelo Zapata (XIV) designed, built, and operates the AI workflow as **sole technical and operational owner**. It is not an arms-length external enterprise customer, and the packet says so plainly. Describe exactly this arrangement on the form |
| **Prior season history** | The role-based workflow operated in production 2025-11-15 to 2025-12-24 (40 calendar days, inclusive), delivering 14 visits across hospitals, Miami-Dade County sites, Publix locations, fire and police departments, and private families - per `docs/operator-attestation-2025-season.md`. Supporting artifacts in assembly |
| **Production status** | **Per the dated 2025 owner attestation (`docs/operator-attestation-2025-season.md`), a prior seasonal operation ran during the attested 2025 season window (dates in the attestation and the Prior-season row above); the 2026 workflow is rebuilt and NOT STARTED.** Not currently active, and not a year-round service - seasonal by nature. The 2026 triage tool is built and runnable; its own production clock starts on the first real customer inquiry processed through it |
| **Launch date** | `[TO FILL on first real inquiry]` — Launch date = the first real inquiry record (never backdated); the 15-day evidence window is measured from the send timestamp of the first valid real, model-backed, reviewed-and-sent record - fallback or unsent records never start it (shared predicate: `tools/triage/production_evidence.py`) |
| **15-day qualification** | `[NOT YET MET]` — earliest qualification is first real inquiry + 15 days. Run `--status` for the live figure |

## Ownership and approval

| Field | Value |
|---|---|
| **Operational owner** | **Marcelo Zapata — built and operated.** Sole operator; sole committer across the repository history |
| **Reviewer of record** | Marcelo Zapata (`reviewer` field on every log line) |
| **Release approval** | Single-operator. Documented in `docs/release-checklist.md` |
| **Human approval gate** | **Mandatory and unskippable.** The tool has no send path. The operator types `APPROVE`, then copies the draft into the customer channel by hand |

## Implemented functionality

LIVE in this table means implemented and passing the synthetic regression
suite; no production use has occurred and nothing is deployed.

What the tool implements, verified by the synthetic regression suite
(dated results in `docs/santa-agent-workboard.md`):

| Capability | Status |
|---|---|
| Detect English vs. Spanish | **LIVE** |
| Extract requested date (EN and ES formats, ISO, numeric) | **LIVE** |
| Extract service category across 9 package types | **LIVE** |
| Extract location and contact status | **LIVE** |
| Identify missing customer information | **LIVE** |
| Flag schedule / capacity risk against first-to-fill dates | **LIVE** |
| Draft a short reply in both English and Spanish | **LIVE** |
| Enforce locked pricing | **LIVE** — 6 validation gates |
| Enforce official-rails payment terms (Zelle; Stripe Payment Link adopted 2026-08-30, NOT_CONFIGURED until the operator creates the link) | **LIVE** |
| Block booking-confirmation language | **LIVE** |
| Block insurance claims while policy unverified | **LIVE** |
| Append a structured production log line | **LIVE** |
| Send a message to a customer | **NOT BUILT, BY DESIGN** |
| Confirm a booking or acknowledge a deposit | **NOT BUILT, BY DESIGN** |

## Models

| Field | Value |
|---|---|
| **Default mode** | `offline-rules-v1` — deterministic, no network, no key. Logged with `fallback_used: true` |
| **AI-assisted mode** | Opt-in. Activates when `MPN_MODEL` and `OPENAI_API_KEY` are set. One OpenAI Responses API call over stdlib `urllib`, strict JSON schema, `store: false`. **In this mode the inquiry text is sent to the API** |
| **Model output re-validated** | Yes. Model drafts pass through all six gates; any FAIL discards them and falls back to the deterministic path with `error_code: MODEL_OUTPUT_VALIDATION_FAIL`. **A model id is recorded only when its output passed every gate** |
| **Model actually run in production** | `[TO FILL]` — written verbatim to the `model` field on every log line. **Not asserted here in advance** |
| **Prompt version** | `triage-v1.0.0` |
| **Price list version** | `2026-08-28.1` |

Every log line records exactly which of the two paths produced the draft. There
is no configuration in which the log can claim a model that did not run.

## Tools and data touched

| Touched | Not touched |
|---|---|
| Inquiry text pasted by the operator (never stored) | Payment systems — no processor, no card handling |
| `pricing.json` (read-only) | Customer channels — no send integration |
| Production log, outside the repository | Telephony — no call handling |
| | Calendar systems — no integration |

## Outcomes

| Field | Value |
|---|---|
| **Measured outcome** | `[TO FILL]` — produced by the log once real inquiries flow |
| **Metrics available on day 1** | Inquiries handled · median first-response time · share of drafts approved unedited · rejection rate · validation blocks · fallback rate · language split · schedule-risk distribution |
| **Derivation** | All from the production log. See `tools/triage/log-schema.md` |

## Evidence

| Reference | What it shows |
|---|---|
| `tools/triage/triage.py` | The runnable tool |
| `tools/triage/validators.py` | Six enforced safety gates |
| `tools/triage/pricing.json` | Locked, versioned price list |
| `tools/triage/test_triage.py` | Passing synthetic triage regression suite; current results in the dated workboard |
| `tools/triage/log-schema.md` | Log fields and derived metrics |
| `tools/triage/examples/inquiry-redacted.jsonl` | Redacted structural sample (synthetic) |
| `docs/operator-attestation-2025-season.md` | Prior-season history |
| `docs/evidence-index.md` | Every claim traced to source |
| `checkout.html` | Published prices the locked list mirrors |
| `business/AGENT-ROLES.md` | Role architecture (2026-08-26) |

## Unresolved fields

| # | Field | Resolves when |
|---|---|---|
| 1 | Production launch date | First real inquiry is processed |
| 2 | 15-day qualification date | 15 days after that |
| 3 | Model actually run | Operator sets `MPN_MODEL`, or stays on the deterministic path |
| 4 | Concrete measured outcome | Log accumulates real rows |
| 5 | 2025 season supporting artifacts | Attestation evidence fields are filled |
| 6 | Insurance policy status | `business/insurance-and-wave1-preflight.md` records a verified policy (deadline 2026-10-26) |
