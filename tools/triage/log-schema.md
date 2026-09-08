# Production Log Schema

One JSON object per line (JSONL), append-only. This is the implementation's
operational evidence format, not a format mandated by OPN. Records support
the submission but do not by themselves prove genuine or continuous use.

## Location

**Production logs live outside the repository and are never committed.**

| Log | Path | Counts toward 15 days |
|---|---|---|
| Production | `%LOCALAPPDATA%\MiamiPapaNoel\triage\production-log.jsonl` | Only valid model-backed reviewed/sent records establish the clock |
| Synthetic | `%LOCALAPPDATA%\MiamiPapaNoel\triage\synthetic-log.jsonl` | **No, never** |

Override the directory with `MPN_LOG_DIR`. `.gitignore` excludes `*.jsonl`
except the redacted example in `tools/triage/examples/`.

## Fields

| Field | Type | Meaning |
|---|---|---|
| `inquiry_id` | string | `MPN-YYYYMMDD-XXXXXX`. Stable handle for one inquiry |
| `received_at` | ISO 8601 | When the operator entered the inquiry; not by itself a production launch |
| `channel` | enum | `instagram_dm` · `whatsapp` · `email` · `phone` · `web_form` · `referral` |
| `language` | `en` \| `es` | Detected language of the customer's message |
| `requested_date` | ISO date \| null | Event date. `null` when the customer did not state one — never inferred from a bare month |
| `category` | enum \| null | `family_visit` · `event_visit` · `christmas_eve` · `christmas_eve_late` · `jingle` · `photographer` · `hoa_community` · `school_daycare` · `corporate` |
| `missing_fields` | array | What the customer still has to supply |
| `model` | string | **Exact** model id that ran, or `offline-rules-v1` for deterministic mode. Never a guess |
| `prompt_version` | string | Version of the triage prompt/logic, e.g. `triage-v1.0.0` |
| `reviewer` | string \| null | Operator who approved. `null` until approval |
| `approved_at` | ISO 8601 \| null | When the operator typed `APPROVE`. `null` means never approved |
| `sent_at` | ISO 8601 \| null | When the operator actually sent it in the customer channel. Recorded only after the operator types `SENT` following the manual send |
| `fallback_used` | bool | `true` when the deterministic offline path produced the draft |
| `outcome` | enum | `pending_review` · `approved_awaiting_send` · `approved_and_sent` · `rejected_by_operator` · `blocked_by_validation` |
| `error_code` | string \| null | `VALIDATION_FAIL`, `MODEL_UNAVAILABLE`, `MODEL_HTTP_ERROR`, `MODEL_PARSE_ERROR`, `MODEL_SCHEMA_ERROR`, `MODEL_OUTPUT_VALIDATION_FAIL`, `MODEL_CATEGORY_AMBIGUOUS`, `PAID_CALLS_DISABLED`, `BUDGET_CAP_REACHED`, `TOOL_UNAVAILABLE`, or `null` |

Supporting fields also written: `location`, `contact_status`, `schedule_risk`,
`schedule_risk_reason`, `price_list_version`, `real_customer`, and `validation`
(the named gate results, including level and detail).

## What is deliberately NOT logged

- **The customer's message text.** Never stored.
- **The drafted replies.** Stripped before the line is written — verified by
  `test_log_line_excludes_draft_bodies`.
- Names, phone numbers, emails, street addresses, payment memos.

`location` holds a coarse area only (`Doral`, `Kendall`), never a street
address. `contact_status` records *whether* a phone or email was supplied, never
the value.

## Metrics this log yields

These metrics derive from recorded actions. Customer outcomes, continuous
availability and actual manual sends still need corroborating business evidence:

| Metric | Derivation |
|---|---|
| Inquiries handled | count of rows |
| Elapsed evidence window | Full elapsed days since the first valid real model-backed reviewed/sent record's `sent_at`; not proof of continuous operation |
| Median first-response time | median of `sent_at - received_at` |
| Approval rate | `approved_at not null` / total; the log does not prove whether the operator edited a reply |
| Rejection rate | `outcome = rejected_by_operator` ÷ total |
| Validation blocks | `outcome = blocked_by_validation` |
| Fallback rate | `fallback_used = true` ÷ total |
| Language split | group by `language` |
| Schedule risk hit rate | group by `schedule_risk` |

## Example

A redacted five-line sample is at
[`examples/inquiry-redacted.jsonl`](examples/inquiry-redacted.jsonl). It is
**synthetic** — illustrative structure only, not evidence of production use.

## Production clock

    python tools/triage/triage.py --status

Reports the first evidenced model-backed manual send and a review target 15
full days later. The shared `production_evidence.py` rule requires a true real
customer flag, non-fallback model, no model error, named reviewer, all six gate
results without failures, `approved_and_sent`, and ordered non-future inquiry,
approval and send times. Incomplete records cannot move the start earlier.

Status never declares `QUALIFIED`; `ELAPSED WINDOW REACHED` means review the
evidence, not that OPN acceptance or continuous operation has been certified.
Malformed JSON, synthetic rows or duplicate IDs make status fail closed.
All status checks are read-only. **Never edit or backdate the evidence.**

New real CLI records include UTC offsets. Legacy offset-free CLI timestamps
are interpreted in the operator machine's local timezone; keep that timezone
correct when reviewing older records. Status displays UTC timestamps. The
submission validator shares the same starting-record and elapsed-time rules.
