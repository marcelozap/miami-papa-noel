# Synthetic Model Check - September 10, 2026

Classification: SYNTHETIC TEST EVIDENCE ONLY. Not production, customer use,
launch, approval, send, booking or proof of OPN eligibility.

Source: terminal output Marcelo pasted into the Santa conversation.
This is a transcription of that reported result, not a fresh API execution
or independent access to provider logs. Recorded 2026-09-11 UTC.

| Field | Reported value |
|---|---|
| Test identifier | MPN-20260910-202616 |
| Printed timestamp | 2026-09-10T21:05:16; no timezone offset supplied |
| Input type | Synthetic Spanish family-visit inquiry |
| Model | gpt-5.6-luna |
| Prompt version | triage-v1.1.1 |
| Price-list version | 2026-08-28.1 |
| Extraction | language es; date 2026-12-10; family_visit; Doral |
| Missing information | phone or email, requested in the drafts |
| Gate results | pricing, bilingual_parity, missing_information, unsafe_confirmation, insurance_claim, payment_method: all PASS |
| Final diagnostic | MODEL CHECK PASSED: model-backed EN/ES drafts and all six gates passed |
| Cleanup diagnostic | Paid calls OFF again; key removed from the process environment |

This supports only that the owner's test reported a successful model-backed
result for this case. It does not establish all Spanish cases, unattended
operation, customer outcomes, continuing credentials/balance, current prices,
or a production start. Do not infer the printed timestamp's timezone.

No credential, customer message, bank detail, provider receipt or API usage
amount is included. This note is not inserted into production-log.jsonl or
the private customer evidence index and cannot start the 15-day counter.
