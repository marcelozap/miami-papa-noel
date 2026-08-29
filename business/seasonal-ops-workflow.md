# Miami Papa Noel Seasonal Operations Workflow

This is the practical operating lane for the December season. It keeps one performer,
one calendar, one payment trail, and one lead tracker aligned without turning the
business into a SaaS project.

Private customer data stays local. Do not commit real family names, addresses, phone
numbers, payment memos, or customer notes. The checked-in tracker is for public
prospects and schema only.

## StateGraph

Every lead moves through the same path:

`lead -> quote -> schedule -> payment receipt -> confirmation -> follow-up`

Use these operational states:

| State | Meaning | Allowed next step |
| --- | --- | --- |
| `lead` | A family, school, HOA, photographer, or company asks about availability. | `quote` |
| `quote` | Correct locked price and terms were sent. | `schedule` or close lost |
| `schedule` | A date/time or premium slot is selected but not fully confirmed. | `payment receipt` |
| `payment receipt` | Zelle retainer is matched to the client/date memo. | `confirmation` |
| `confirmation` | Calendar, tracker, slot board, and customer message agree. | `follow-up` |
| `follow-up` | Review, referral, photo permission, or next-season lead is requested. | closed |

Premium date slots use the stricter slot states from `../schedules/peak_slots_2026.json`:

`OPEN -> HOLD_48HR -> DEPOSIT_PAID -> CONFIRMED`

Rules:

- `OPEN` means the slot can be offered.
- `HOLD_48HR` means a client asked for it but no money has cleared.
- `DEPOSIT_PAID` means the 50% Zelle retainer cleared and the memo can be matched.
- `CONFIRMED` means the slot, payment, calendar, and customer message all agree.
- A slot is not sold until it reaches `CONFIRMED`.

## Role Agents

These are roles, not separate products. One person can do all of them by following
the checklist.

| Role | Job | Output |
| --- | --- | --- |
| Intake | Capture the request and missing facts. | Lead row with event type, date, city, contact, and next action. |
| Scheduling | Check capacity, travel, peak slots, and route order. | Date/time decision or unavailable reply. |
| Outreach | Send bilingual replies, follow-ups, and referral requests. | Customer-facing message from the approved templates. |
| Payment | Match Zelle deposit to client, date, and memo. | Deposit status and memo ID, never a screenshot in git. |
| Operator review | Human final check before a booking is treated as real. | Calendar event, confirmed slot, and sendable confirmation. |

## Required Fields

For every active booking or held premium slot, collect:

- Client or organization name
- Contact name when different from client name
- Phone, email, or Instagram
- Event date and requested time
- Address or neighborhood
- Event type
- Package/rate quoted
- Deposit status
- Zelle memo ID after payment clears
- Notes for parking, gifts, chair, air conditioning, and crowd flow

## Validation Gates

Run the gate before confirming any premium date slot:

```powershell
python scripts/validate_slot_confirmations.py
```

The gate must fail closed for:

- Double-booking: two active leads cannot lock the same `time_slot_id`.
- Missing payment: `DEPOSIT_PAID` or `CONFIRMED` requires `deposit_status` = `PAID`.
- Over-capacity: a date cannot exceed the slots defined in `../schedules/peak_slots_2026.json`.
- Incomplete customer info: an active held or booked slot needs a name, contact method, and area/address note.
- Unknown slot: `time_slot_id` must exist in the peak slot schedule.
- Date mismatch: `target_date` must match the date attached to the slot ID.

If the script fails, fix the tracker first. Do not send a confirmation while the gate
is red.

## Manual Fallback

If AI, the internet, or a hosted account is unavailable:

1. Open `../lead-tracker.csv`.
2. Open `../schedules/peak_slots_2026.json`.
3. Find the lead row.
4. Fill the required fields.
5. For premium dates, copy the exact `slot_id` into `time_slot_id`.
6. Set `state` to `HOLD_48HR` only if the slot is being held without cleared money.
7. After Zelle clears, set `deposit_status` to `PAID` and enter the memo in `zelle_memo_id`.
8. Run `python scripts/validate_slot_confirmations.py`.
9. If validation passes, create or update the calendar event.
10. Send the confirmation message.
11. After the visit, send the after-visit review/referral message.

## Payment Rules

Customer payment intake is Zelle-only:

- 50% non-refundable retainer due at booking.
- Zelle to `305-244-0360`.
- Memo format: `[EVENT DATE] - [CLIENT NAME]`.
- Balance follows the current locked terms for the package/date.
- Do not publish Cash App, Venmo, wire, or other payment methods on customer surfaces.

## Insurance Preflight

Do not send messages claiming insured, fully insured, COI, certificate of insurance,
or additional insured until `insurance-and-wave1-preflight.md` is resolved and the
policy is verified active.

## What Gets Committed

Safe to commit:

- Docs
- Empty schemas
- Validators
- Public prospect lists
- Template language
- Slot definitions without real customer data

Do not commit:

- Real customer names tied to bookings
- Home addresses
- Phone numbers from private inquiries
- Payment screenshots
- Bank or Zelle screenshots
- Private notes about families or children
