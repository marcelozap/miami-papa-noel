# Miami Papa Noel

Website and business kit for Papa Noel Santa visits in Miami-Doral and nearby areas.

## Website Pages

- `index.html` - main website
- `checkout.html` - package pricing and reservation path
- `book.html` - booking request funnel
- `links.html` - quick link-in-bio page for Instagram and social profiles
- `events.html` - focused event-visit landing page for schools, HOAs, businesses, and toy drives
- `christmas-eve.html` - focused Christmas Eve gift-delivery landing page for families
- `summer-santa.html` - focused Summer Santa and Christmas-in-July landing page
- `service-areas.html` - focused service-area page for Miami, Doral, Hialeah, Kendall, Sweetwater, Miami Lakes, Coral Gables, and nearby communities
- `schools-daycares.html` - focused school, daycare, and classroom Santa visit landing page
- `hoa-apartments.html` - focused HOA, apartment, condo, and resident event landing page
- `partners.html` - focused referral-partner page for photographers, event vendors, pet businesses, and local family businesses
- `reviews.html` - social proof page with real visit photos, community proof, and review collection guidance
- `after-visit.html` - thank-you page for reviews, approved photo permission, and referrals
- `thank-you.html` - confirmation page after a booking form submission

## Public Contact Details

Use these details consistently across the website, profiles, and outreach:

- Phone: `786-975-9557`
- Email: `santa@miamipapanoel.com` (verified Google Workspace mailbox).
- Primary booking path: `https://miamipapanoel.com/book`
- Instagram: `@miamipapanoel`

## Business Kit

Open `business/` for the operating docs:

- Father's Day launch pack
- Santa lead generation kit
- Passive marketing engine
- Directory profile kit
- Launch command center
- Quote builder
- Follow-up builder
- Account setup checklist
- Brand/profile copy
- Sales funnel
- Local lead research playbook
- Referral partner playbook
- Review and referral system
- Booking SOP
- Client message templates
- Pricing framework
- Launch checklist
- Family roles

## OpenAI Partner Readiness

The local, fail-closed submission workflow lives in `docs/` and `scripts/`:

- `docs/OPN-SUBMISSION.md` - current submission narrative and evidence fields
- `docs/opn-resubmission-field-map.md` - exact assessment sections to update
- `docs/OPN-VALIDATION.md` - preflight, final validation, and packet commands
- `docs/evidence-intake.md` - redaction and receipt-intake procedure
- `scripts/validate_opn_submission.py` - local validator
- `scripts/evidence_index.py` - hash a redacted external artifact into the index
- `scripts/build_opn_packet.py` - build or verify the safe ZIP outside this repo

Production logs and evidence stay outside Git under
`%LOCALAPPDATA%\\MiamiPapaNoel\\`. Run preflight before editing the submission;
run final validation only after real production and evidence records exist.

## Vercel

Use the default Vercel static site settings:

- Framework Preset: Other
- Root Directory: `.`
- Build Command: leave empty
- Output Directory: leave empty

## Assets

Marketing photos and QR assets are in `assets/`.
