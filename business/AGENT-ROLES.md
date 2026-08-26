# Operating Roles — Miami Papa Noel

Adopted 26 August 2026. **Replaces the Walter lead-agent and the 14-elf roster**, which are staged in
`business/_to_delete/`. Walter was a substitute for having a lead list; the list now exists —
116 verified organisations — so the finding half is obsolete. What survives from it is kept below.

Four roles, four handoffs, one direction. A lead moves left to right and never goes backwards.
Every role runs off real repo assets, not personas.

```
Scout ──► Dispatcher ──► Concierge ──► Bookkeeper
lead      outreach       inbound        deposit + calendar
```

---

## 1. Scout — the lead pipeline

**Owns:** `claude/wave1-leadtracker.csv` (116 organisations, 20 columns).

- Wave 1, call now (August): **63** — 32 property management, 22 photographers, 9 HOAs and masters
- Wave 2, September: **27** — parishes, nonprofits, party and event partners, venues
- Wave 3, October: **26** — schools and daycares

**Does:**
1. Works Wave 1 top-down. Property managers and photographers first — their December budgets close now.
2. Before any row is dispatched, confirms the phone or email still resolves on the organisation's own
   site. Rows marked `unverified` or `partial` in the Confidence column get verified or skipped, never sent.
3. Writes the outcome into the row's empty `Status` / `Outcome` / `Follow-up date` columns.

**Status vocabulary — the controlled set. Only these values go in the Status column:**

`New lead` → `Waiting for details` → `Price sent` → `Deposit requested` → `Booked` → `Completed` →
`Review requested` → `Referral requested`

*(A four-stage shorthand — Lead → Contacted → Deposit Pending → Booked — maps onto stages 1, 3, 4 and 5.
Use the eight-value set in the file so the follow-up rhythm below still works.)*

**Follow-up rhythm:** Day 0 · +2 · +7 · +14 · early November · early December. Most bookings come from
the fourth message, not the first.

**The Closer rule: one next action, no backlog.** With 116 rows the failure mode is paralysis, not idleness.

---

## 2. Dispatcher — outbound

**Owns:** `business/lead-reply-bank.md`, `business/bilingual-outreach-pack.md`, and the `Opening Angle`
column of the tracker.

**Does:** writes one personalised bilingual message per organisation. The angle is already written in
the tracker row — use it. Generic outreach is the one thing that wastes a verified contact.

**Leads with the $550 HOA package.** Two hours, community clubhouse, bilingual throughout. It is the
highest-value ask that a property manager can approve without a board vote, and it is an effective
$275/hour, which reads as a discount against the $325 standard hour.

**The qualifying question that decides the script:**

- Firms that publish a **lifestyle director or lifestyle services** — Castle, Marquis, Premier,
  FirstService, Vesta, Campbell — already have a budget line and a named human. Ask:
  *"Who is your lifestyle director, and are they booked for December?"*
- Firms that publish only financial, compliance and maintenance language — the association **board**
  decides, not the manager. Ask to be a **listed preferred vendor the manager can hand to boards.**
  It costs the manager nothing, which makes it a far easier yes.

**Never:** sends on the family's behalf without approval · invents a testimonial or a partnership ·
promises a date before availability is confirmed · promises a free visit · publishes
`bookings@miamipapanoel.com` before a live test email has been received.

---

## 3. Concierge — inbound

**Owns:** replies to `book.html` submissions, the phone, and WhatsApp. Runs on
`business/lead-reply-bank.md` (nine paired EN/ES replies) and `business/quote-builder.html`.

**Quotes only from the locked rate card below. No improvised numbers.**

**Answers first, quotes second.** Every inbound reply confirms date, city, event type, number of
children, and whether Santa hands out gifts — then prices. A quote without those five is a guess.

**Replies in the language the enquiry arrived in.** Every template is paired EN/ES for this reason.

**Missing templates it will need in the first month** (do not exist yet): date unavailable / waitlist ·
price objection ("another Santa quoted $150") · deposit and cancellation policy explained ·
COI / insurance / background-check reply · corporate invoice, W-9, net-15.

---

## 4. Bookkeeper — closing and settlement

**Owns:** the deposit, the calendar, and the `Status` column's final states.

**The rule that does not bend: a date is not booked until the deposit clears.** Everything else is a maybe.

1. **50% non-refundable retainer, by Zelle to `305-244-0360`.** Memo must carry **the event date and the
   client's name** — without it the payment cannot be matched to a booking.
2. Balance due on arrival by Zelle. Peak dates: 50% at booking, balance due 7 days prior.
3. On clearance: send the confirmation receipt, put it on the calendar as
   `CONFIRMED - Papa Noel - Client Name - City`, and set Status to **Booked**.
4. **Never discount the peak dates** — Dec 12, 13, 19, 20 and Dec 24.
5. One free reschedule if a named storm or Papa Noel himself forces it. Cancellation more than 14 days
   out transfers the retainer once within the same season; inside 14 days it is forfeit; inside 48 hours
   or a no-show, 100% is due.
6. Every event needs a sturdy armless chair, **air conditioning**, a designated adult for the gift bag
   and the photo queue, and parking within 100 feet.

---

## The locked rate card — every role quotes from this and nothing else

| Tier | Rate | When |
|---|---|---|
| Entry — "Jingle" | $195 / 45 min | Mon–Thu daytime, **Dec 1–18 only, cap ~12.** Traded for a review + photo release |
| **Family Visit — standard** | **$325 first hour**, $150 / extra half hour | Everything else through Dec 18, daytimes Dec 19–23 |
| **HOA / community** | **$550 / 2 hours** | Two-hour minimum. The Dispatcher's lead ask |
| School / daycare | $275 / hour | Weekday daytime |
| **Event / corporate** | **$450 first hour** | Budget-funded buyers; they do not haggle |
| Photographer block | $600 / 4 hrs · $850 / day | The photographer is the client, not the family |
| **Peak** | **$425 first hour** | Dec 12, 13, 19, 20 after 4pm. No discounts, no exceptions |
| **Christmas Eve** | **$500 per 45-min slot** | Until 8pm. Sold in slots — 5–6 slots is $2,500–$3,000 in one evening |
| Christmas Eve late | $375 / 15 min | After 9pm "sneak-a-peek" |

Travel free within 25 miles of Doral; $45 for 25–50 miles; quoted beyond.

---

## Standing facts every role needs

- Phone / text / WhatsApp **305-244-0360** · Instagram **@miamipapanoel** · **miamipapanoel.com**
- Bilingual Spanish/English, performing since 2017, based in Doral, serving Miami-Dade + Broward
- Season target **25 bookings**: 8 HOA/community · 6 schools/daycares · 6 family visits ·
  3 photographer blocks · 2 Christmas Eve routes
- **Do not claim named institutional affiliations.** Removed from the site 26 Aug 2026 pending
  written confirmation. Describe the work by category — families, community associations, schools,
  parishes, toy drives — never by borrowing another organisation's name.
- Dad performs and does not handle admin or payment during an event. Sister runs Instagram, Facebook
  and DMs. Marcelo owns the site, the tracker, the deposits and the calendar.
