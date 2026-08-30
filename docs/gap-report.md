# Gap Report

**Prepared:** 2026-08-29
**Subject:** Miami Papa Noel bilingual inquiry triage deployment

What stands between today and an OpenAI Partner Network qualification, and what
closes each item.

---

## Status summary

| # | Requirement | Status |
|---|---|---|
| 1 | Active customer AI deployment in a real workflow | **BUILT, NOT YET RUNNING ON REAL INQUIRIES** |
| 2 | Launch date / production status | **PENDING** — set by the first real inquiry |
| 3 | Operational owner | **MET** — Marcelo Zapata |
| 4 | Live AI functionality | **BUILT** — configured Responses API path plus deterministic fallback, triage, extraction, risk flagging, bilingual drafting, and 6 enforced gates; production model use is still to be recorded |
| 5 | Concrete outcome | **PENDING** — metrics derive automatically once rows exist |
| 6 | Production model(s) | **PENDING** — recorded verbatim per log line; deterministic mode is the default |
| 7 | How components work together | **MET** — `docs/agent-workflow-architecture.md` |
| 8 | Testing and release approval | **MET** — 43 passing tests, `docs/release-checklist.md`, and local OPN preflight validator |
| 9 | Production monitoring | **BUILT** — logging layer tested; awaiting real rows |
| 10 | Failure handling | **MET** — automatic fallback plus a full manual procedure |
| 11 | ≥15 days production operation | **NOT MET** — clock starts on the first real inquiry |

**The main evidence gap is real production evidence and elapsed time.** The model-backed path is built,
tested, and documented, but a production model is not recorded until the
operator configures one and a real inquiry passes through it. What does not
yet exist is 15 days of real inquiries flowing through the deployment, and
that cannot be manufactured or backdated.

---

## Blocker 1 — the production clock has not started

**What closes it:** process one real customer inquiry with `--real`.

```powershell
python tools\triage\triage.py --message "<real inquiry text>" --channel instagram_dm --real
```

That first line's `received_at` is the launch date. Fifteen days later the
requirement is met.

| Milestone | Date |
|---|---|
| First real inquiry | `[TO FILL]` — earliest 2026-08-29 |
| Qualification | first real inquiry + 15 days |
| If started 2026-08-29 | **2026-09-13** |

Timing is favorable: September is when HOA, school, and corporate inquiries
begin arriving for December, so the deployment will see genuine volume rather
than manufactured traffic. Do not pass `--real` while testing — synthetic runs
are excluded by design, and a polluted log is worse than a short one.

## Blocker 2 — measured outcome

**What closes it:** the same 15 days. Every metric derives from the log with no
additional tracking — inquiries handled, median first-response time, share of
drafts approved unedited, rejection rate, validation blocks, fallback rate,
language split, schedule-risk distribution.

Reviewers respond to a real number with a real denominator. Twenty inquiries
with a median response time is stronger than a large claim with no log.

## Blocker 3 — model to be recorded for an AI-backed claim

**What closes it:** either decision is acceptable, and both are honest.

- **Use deterministic mode.** Logs record `offline-rules-v1` and
  `fallback_used: true`. This is a real, working, human-approved operational
  fallback, but it is not the model evidence for an AI deployment.
- **Enable AI mode.** Set `MPN_MODEL` to an exact model id and provide the key.
  The tool calls the Responses API, validates the result locally, and records
  the exact model only after a successful response.

Do not write a model name into any document before it has run. The log is the
only place that field gets filled.

---

## Safety findings requiring action

Three came out of the pre-implementation audit. Two are now closed in this
working tree; the pricing documentation item remains open before the Wave 1
outreach window.

### 1. Unverified insurance claims on customer surfaces — RESOLVED

`business/insurance-and-wave1-preflight.md` states plainly that no customer
message may claim "insured", COI, certificate of insurance, or additional
insured until a commercial policy is verified. Deadline recorded there:
**2026-10-26**.

The affected surfaces were corrected:

| Location | Content |
|---|---|
| `checkout.html` | Policy-neutral coverage wording; no `$1M` claim |
| `business/content-engine.html` | Policy-neutral insurance wording and no ready-to-send COI claim |

`business/lead-reply-bank.md:577` remains correctly gated with a
`[VERIFY POLICY ACTIVE]` marker.

**The triage tool refuses to emit insurance language in any form** while the
policy is unverified, and the website and campaign copy now follow the same
rule.

**Remaining rule:** only restore verified insurance/COI language after the
preflight document records an active policy.

### 2. Non-Zelle payment methods recommended internally — RESOLVED

`business/account-setup-checklist.md` now lists Zelle only and explicitly
prohibits Cash App, Venmo, Square, Stripe, card, and wire instructions.

Customer-facing surfaces remain Zelle-only, and the tool blocks every other
method.

### 3. Pricing documentation out of sync — RESOLVED

`business/offer-and-pricing.md` now matches `checkout.html` and
`tools/triage/pricing.json`, including $195, $425, $275, $550, $600, $850, and
the $45 travel fee.

The tool and public price table are now aligned. The validator checks every
customer-surface dollar figure against the locked list.

---

## Prior season history

The role-based workflow operated during the 2025 Christmas season per
`docs/operator-attestation-2025-season.md`. That attestation is the project's
history of record and is not a blocker for this submission.

Ten evidence fields are listed there for anyone who wants to strengthen the
record — season window, channels, volume, outcome, dated artifacts. They sit in
message history, calendar entries, and payment records rather than in this
repository, which began 2026-06-10. Filling them is optional and additive; the
submission does not depend on it.

---

## What to submit, and when

**Now:** the architecture, the running tool, the test results, the release and
monitoring documentation, the evidence intake, and the local preflight — with
the qualification date stated plainly.

**On qualification:** the production log, launch date, model, and measured
outcomes.

Suggested framing:

> The bilingual inquiry triage deployment is built, tested, and instrumented.
> It enters production on `[DATE]` and reaches 15 days of continuous operation
> on `[DATE + 15]`. We are submitting the architecture, controls, and test
> results now, and will provide the production log and measured outcomes on
> qualification.
