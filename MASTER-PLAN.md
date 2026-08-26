# Miami Papa Noel — Master Operational Plan

**Single source. Supersedes the copies in the repo and anything in `PapaNoel_MarketingKit`.**
Merged 26 Aug 2026 from both chats. Target: **25 bookings** — 8 commercial/HOA, 12 private/family,
5 studio & events. Critical window: **26–31 August**, the South Florida HOA December budget lock.

---

## ✅ RESOLVED 26 AUG — the price sheet is the researched one, and it is live in the repo

Decided: **ship the researched sheet.** The 3-tier version from the merged plan would have made $195 —
a capped weekday promo traded for a review — the standard one-hour rate, cut $325 from "first hour" to
"1.5–2 hours", and left Christmas Eve, schools, corporate and photographer blocks with no rate at all.
Roughly $6,000 across 25 bookings.

**Adopted rate card:**

| Tier | Rate | When |
|---|---|---|
| Entry — "Jingle" | $195 / 45 min | Mon–Thu daytime, **Dec 1–18 only, cap ~12**, traded for a review + photo release |
| Standard | **$325 first hour**, $150 / extra half hour | Everything else through Dec 18, daytimes Dec 19–23 |
| HOA / community | **$550 / 2 hours** | Two-hour minimum |
| School / daycare | **$275 / hour** | Weekday daytime |
| Corporate | **$450 first hour** | Budget-funded buyers; they do not haggle |
| Photographer block | **$600 / 4 hrs** · $850 / day | The photographer is the client, not the family |
| **Peak** | **$425 first hour** | **Dec 12, 13, 19, 20 after 4pm. No discounts, no exceptions.** |
| **Christmas Eve** | **$500 per 45-min slot** | Until 8pm. Sold in slots — 5–6 slots is $2,500–$3,000 in one evening |
| Christmas Eve late | $375 / 15 min | After 9pm "sneak-a-peek" |

**Patched 26 Aug — all 49 instances across 13 files, English and Spanish:**

| Page | Was | Now |
|---|---|---|
| Family Visit card (`index`, `checkout`, `book`) | From $125 · 20-30 min | **From $325 · first hour** |
| Event Visit card | From $225 · 45-60 min | **From $450 · first hour** |
| Christmas Eve card | From $250 · scheduled window | **From $500 · 45-minute slot** |
| `hoa-apartments.html` | From $225 · 45-60 min | **From $550 · 2-hour minimum** |
| `schools-daycares.html` | From $225 · 45-60 min | **From $275 · weekday daytime, 1 hour** |
| `events.html` | From $225 · 45-60 min | **From $450 · first hour** |
| `christmas-eve.html` | From $250 · scheduled window | **From $500 · 45-minute slot** |
| `summer-santa.html` | From $225 for events | **From $325 for events** |
| `index.html` schema.org `priceRange` | $125+ | **$195+** |
| `packages-and-pricing.md` | three "suggested" lines | full rate card appended |
| `business/` — directory kit, reply bank, offer sheet, flyer | old trio | matched to the sheet, EN + ES |

Verified: no old price remains anywhere in the repo, every page's JavaScript still parses, and the
Spanish dictionaries were updated alongside the English. Uncommitted — review and push.

> The merged plan said 34 instances; it was **49 across 13 files**.

---

## Part 1 — The six setup blockers

### 1. Commercial liability insurance — DO FIRST, 15 min
**Insurance Canopy**, entertainers annual policy, **$199/yr**. GL $2M aggregate / **$1M each occurrence**,
$1M personal & advertising injury, $5K medical, $300K damage to premises. **Santas are a named covered
class.** Annual includes **unlimited additional insureds at no charge** (event policies charge $5 each) —
that is the reason to buy annual, because every school, church, HOA and mall will demand to be named.
Certificates are self-serve and instant.
→ https://www.insurancecanopy.com/entertainment-insurance/performers/santa-claus

*If a school contract demands abuse/molestation coverage (some Florida districts do, and basic GL
excludes it): call Francis L. Dean, 800-745-2409 — they list Santas and offer it as an option.*

### 2. Background screening — the self-serve path is closed
**You cannot register for Florida VECHS as an individual.** FDLE: the applicant *"must be an
organization, not an individual."* **The school or daycare is the qualified entity and submits you
through their own ORI number.**

Do this anyway so results are on file before anyone asks: Live Scan at **IDENTICO**, 4012 SW 18th St,
West Park FL 33023 — **(954) 239-8590**, ~25 min from Doral, **$60 employee / $50 volunteer**, 10–15 min
appointment, results **24–72 hrs**. **Call first and say you are a contractor needing Level 2 for school
work** — they will give you the right ORI, and the wrong one means paying twice.

State fees (FDLE, eff. 1 Jan 2025): VECHS Employee $24 state + $36 federal = **$60**. Volunteer = **$28**.

Under **Fla. Stat. 1012.465** (Jessica Lunsford Act) the cost *"may be borne by the district school
board, the contractor, or the person fingerprinted."* **Offer to pay it yourself — it closes bookings.**
When a school books you, ask: *"Do you want me to run Level 2 under your VECHS account, or does M-DCPS
require its own vendor badge?"* Budget for possibly paying twice.

### 3. Pricing parity — **DONE 26 Aug.** See the table at the top of this file.

### 4. Deposit and payment funnel — **DONE 26 Aug**
Bilingual deposit block added to `checkout.html` (17 lines, EN + ES, no prices touched): 50%
non-refundable locks the date, balance on arrival, **Zelle to 305-244-0360 with the event date and client
name in the memo**, one free reschedule if a named storm or Papa Noel himself forces it, and the line
that matters — *a date is not reserved until the deposit clears.* Uncommitted; review the diff and commit.

### 5. Custom domain email — **ImprovMX free tier → Gmail**
Add ImprovMX MX + TXT records to DNS (clean out conflicting MX/SPF first), then configure Gmail
"Send-As" for a branded sender.
> Conflict to clear: `book.html` still posts to **`rubiosally@hotmail.com`** via FormSubmit, with an
> inline comment saying to switch back after **Microsoft 365** DNS is active, and
> `business/microsoft-365-email-runbook.md` documents that path. ImprovMX is free and M365 is not —
> pick ImprovMX and delete the M365 runbook, or the next person to touch this does the wrong one.
> Two places to update when it is live: the `<form action>` and the `mailto:` link in `book.html`.

### 6. Google Business Profile
**Category: `Entertainer`.** Secondary: `Children's party service`, `Entertainment agency`. Do **not**
add `Costume rental service`.

**Name field: type `Miami Papa Noel` and nothing else.** No city, no tagline, no "Bilingual Santa." Google
suspends for this and it is the number one cause of entertainer rejections.

Answer **NO** to "a location customers can visit." Set the service area by **naming cities, not a
radius** — Doral, Miami, Hialeah, Coral Gables, Miami Beach, Kendall, Homestead, Aventura, Fort
Lauderdale, Hollywood, Pembroke Pines, Weston, Davie, Coral Springs, Sunrise, Miramar.

Expect **video verification**: recorded inside the flow on your phone, **one continuous take, no edits**,
60–120 seconds, showing (a) a street sign or house number matching the address, (b) you unlocking the
front door with your key, (c) the suit and anything branded. **Practice on the normal camera app first —
repeated failures can trigger a "No More Ways to Verify" lockout.** Review up to 5 business days.

**Description, ready to paste (743 chars):**

> Professional, bilingual (English & Spanish) Santa Claus experiences across Miami-Dade and Broward
> County. Specializing in authentic holiday magic for HOA community celebrations, private home visits,
> corporate parties, school events, and professional photography mini-sessions. Offering photo-ready
> traditional appearances, interactive storytelling, gift delivery, and personalized holiday moments
> tailored to your gathering. Fully insured with commercial liability coverage and verified background
> credentials. Book early to secure prime November and December holiday dates for your neighborhood or
> family tradition.

Then add **Services** as separate entries (Bilingual Santa Visit, Santa Home Visit, Corporate Santa,
School Santa Visit, Santa Photo Session, Visita de Papá Noel), 10+ real in-costume photos, seasonal
hours, and phone/website matching the site digit for digit.

---

## Part 2 — Wave 1 outreach, 26–31 August

**Verified prospect list:** `claude/wave1-hoa-prospects.md` — 30 community-association management firms
across Miami-Dade and Broward, each confirmed on a live page, sorted Doral-first, sources on every row.

**Call these eight first:**

| Firm | Phone | Why |
|---|---|---|
| Miami Management, Inc. | 305-378-0130 | 370+ associations, 70,000+ units, and already runs a Toys for Tots drive |
| Castle Group | 954-792-6000 | Staffed **Lifestyle Services Group** with booking agents — already a buyer |
| Marquis Association Mgmt | 786-655-5155 | Named BD contact: oded.abravanel@marquishoa.com. Luxury portfolio |
| FirstService Residential | 786-319-5204 | Largest in Florida, explicit lifestyle programming |
| Affinity Management | 800-977-6279 | **Headquartered in Doral.** Info@ManagedByAffinity.com |
| KW Property Mgmt | 305-476-9188 | **Also Doral.** Heavy Hispanic-market condo portfolio |
| Premier Association Svcs | 954-797-9007 | Says "dedicated lifestyle directors" — ask for one by title |
| Campbell Property Mgmt | 954-427-8770 | Eight offices, Lifestyle Director on staff |

**The finding that decides the script: "lifestyle" is the qualifying filter, not size.**
About a third of these firms publish a lifestyle director role — they have a budget line, a calendar and
a named human, and the ask is simply *"who is your lifestyle director, and are they booked for
December?"* For the other two-thirds the **association board** decides, not the manager — so ask to be a
**listed preferred vendor the manager can hand to boards.** It costs the manager nothing, which makes it
a far easier yes.

**Do not waste calls on:** Sentry Management (no South Florida office), Lang Management (stops at Boca),
Empire, Beacon, Sunstate (Orlando/Sarasota).

### Scripts

**English — HOA / property manager**
> "Hi [Name], I'm reaching out about holiday event planning for [Community]. I provide professional,
> fully insured, bilingual Santa Claus appearances for community celebrations and tree lightings in
> South Florida. I know December budgets are closing this week, so I wanted to share our availability,
> certificate of insurance, and flat-rate HOA packages before the calendar fills. Who's the best contact
> to send our one-page package to?"

**Spanish — HOA / property manager**
> "Hola [Nombre], le contacto para coordinar los eventos navideños de [Comunidad]. Ofrezco servicios
> profesionales y bilingües de Santa Claus para eventos comunitarios y celebraciones de fin de año en el
> sur de la Florida, con seguro de responsabilidad comercial completo. Sé que están cerrando los
> presupuestos de diciembre esta semana y quería hacerles llegar nuestras fechas disponibles y paquetes
> para comunidades. ¿A qué correo o persona puedo enviarle la información?"

**Photographers** — different ask entirely: *"Are you running Santa mini-sessions this year, and is your
Santa booked?"* Offer the flat block so they can price their own sessions around it.

**Past clients since 2017** — the highest-return hour available. One text each asking for a sentence and
a star rating on the new Google profile. Target 10 reviews by 30 Sep. Competitors carry 25–65; the
reviews page currently has one unattributed quote.

---

## Part 3 — Marketplaces (start now, upgrade in October)

**GigSalad** — sign up free today at gigsalad.com/join. Free members pay a **5%** service fee on
confirmed bookings, paid members 2.5%, and **nothing at all for receiving leads or sending quotes.**
Free approval takes **1–3 business days**; paid is instant. The **Act/Service Name is permanent** — type
`Miami Papa Noel` carefully. Profile photo must be real: **no logos, text, or AI images.** Category is
Variety → Santa Claus. **Upgrade to Featured ($169 for 3 months) on 1 October**, not now — the whole
season is Nov–Dec, and Featured claims 20–28× the leads.

**The Bash** — thebash.com/signup/landing. **5% ($20 min) booking fee**, verified. Membership price is
not published anywhere public; start signup and stop at the payment screen to see it. Their own
benchmarks: top bookers average **1,975 characters** of description and **46 photos**. **Turn Auto-Add
ON — almost 50% of bookings come from auto-added leads.**

**The one asset no competitor has:** a 30–60 second video of Papa Noel in character speaking both
Spanish and English. Shoot it once, use it on GigSalad, The Bash, the GBP and Instagram.

---

## Part 4 — Next concrete actions

1. **Answer the pricing question (A, B or C above).** It blocks the site patch, GBP, and both
   marketplace listings — all three must show the same number.
2. **Buy the Insurance Canopy annual policy.** 15 minutes, $199, gates every booking above $400.
3. **Commit and push the repo.** There are **1,713 uncommitted lines** already sitting there — a
   3,386-line rewrite of `index.html` and **20 new leads** in `lead-tracker.csv`, last commit 16 June.
   That work exists on one disk.
4. **Submit the Google Business Profile.** Longest clock, start it today.
5. **Call the first ten firms in the Tier A table.**
6. **Book the Live Scan appointment** at IDENTICO.
