# Miami Papa Noel Agent Workboard

## Gallery release integration (Codex, 2026-09-11T14:00Z)

COMMITTED and public deployment VERIFIED. Owner explicitly authorized pushing all finished work. Reviewed
Claude 028's frozen gallery and the local preservation commits, running the
full offline gate, then publishing via main's existing Vercel integration.
Codex owns release coordination and review only; no redesign is requested.
Paid AI stays disabled; no customer sends, billing, Stripe activation or DNS
changes. The explicit public allowlist remains the deployment boundary.

Independent offline ops: 824 passed, 7 skipped, 52 subtests, all 28 suites and
seven steps PASS. Build: 53 allowlisted files. Frozen four-file hashes match
Claude 028. New secret-pattern scan: zero hits; no new record/database files.
HTTP-served browser: five images decoded, viewer next/Escape and EN/ES work,
no JS errors observed; mobile outer width 390 (375 content) has no overflow.
Publishing preservation commits also saves backend source, not a backend
deployment. Production verification follows the push; no Day 1 claim.

2026-09-11T14:02:12Z: b2ffa094f5fa89f72d21d0a4114c39140c5d62c5 pushed
atomically to main and ops. HTTPS homepage/book/five gallery photos match
Git bytes; six private paths and six removed GPS originals return 404 on
miamipapanoel.com. Live Spanish gallery viewer works. Preview stopped.
Earlier deployment URLs and Git history remain outside this exclusion check.


## Homepage photo gallery: warmth and proof without clutter (claude, 2026-09-11T05:10Z)

READY_FOR_REVIEW, frozen, UNCOMMITTED. Owner feedback: the simplified site lost
personality and photographic proof. Bounded homepage improvement only; the
request/call journey, three visit choices, prices, phone, EN/ES, no-login,
book.html, backend, paid-AI settings and hosting are untouched. Codex to
integrate and publish; no push or deploy from here.

**Changed files (SHA256):**
- `index.html` e8871daee8b643f54d179d5508de9eaa00d95148b4d1096dbd792b23df05bb89
- `scripts/test_public_release.py` 29cf25ca71478d6da064b5c0b371f33de79777c5b602f221ec625d63d0ab5413
- `deploy/public-files.json` 94f1e4531d48bd0bcb5554d6143f41abbc9b1986e8d64c25aa8f640b862914cd
- NEW `assets/optimized/extra-20231210-160208-1200.jpg` (185 KB, 675x1200)
  61f0e30a1acf554db744a1706fbbe8e3c65e71c3e7bf9d3bafac7e1d8724c4fc - web-size
  copy of the already-allowlisted `assets/extra/20231210_160208.jpg`, EXIF
  orientation baked in, all metadata stripped, same convention as the existing
  `optimized/extra-*-1200.jpg` files.

**What changed on the page.** New `#gallery` section between the visit choices
and the FAQ: "Meet your Santa" / "Conoce a tu Santa", five Santa-only photos in
a featured-plus-four grid (desktop 1.15fr/1fr/1fr with the first tile spanning
two rows; mobile full-width featured tile then 2x2), captions under each tile,
EN/ES alt text and captions, per-photo `--focus` object-position so faces are
never cut in the 4:5 crops. Click-to-enlarge is a native `<dialog>`: visible
"x Close" button top-right (99x44 on phones), 48px prev/next, "n / 5" counter,
ArrowLeft/ArrowRight wrap, Escape closes (explicit handler, not only the
native cancel), focus lands on Close on open and returns to the thumbnail on
close, body scroll locks while open, backdrop click closes, `aria-label`
localised via a new `data-i18n-aria` hook. Without JS or `showModal`, each
tile is a plain link to the full image. The seated portrait moved from the
FAQ column into the gallery; the FAQ is now a single 760px column. No new
copy makes a claim: "Real photos of your Santa" is the only statement, and the
regression forbids review/insurance/award/superlative wording in `<main>`.

**Photo selection (all 16 candidates inspected, not just listed).**
Used - Santa is the only identifiable person: standing portrait (hero,
unchanged), peace sign by the lobby tree (featured; no camera watermark),
seated portrait, white throne with red carpet (new web copy), close-up with
the cup, Labrador visit. NOT used, flagged for Marcelo before any use:
`santa-family-event` (woman + young girl, face clearly visible - note it is
still the `og:image` and schema image in `<head>`, pre-existing, owner's
call), `santa-gift-delivery` (two children), `santa-community-event` (a dozen
children + performers), `santa-photo-1` and `IMG_20221224_222329681` (other
adults), `IMG_20221224_223822307` (three young women, a child, a dog),
`extra-20231214-114914` / `20231214_114907` (elf and Grinch performers in an
institutional hallway with a wall plaque and room number), `Screenshot_...`
(child), `santa-card` (photo strip naming a third-party business and a
photographer's phone number). No AI-generated or edited faces; the phone
watermark on two originals is left as-is and cropped out of the tiles.

**Privacy finding fixed in this change (please do not drop it when
integrating):** six full-resolution originals in the public allowlist carry
GPS EXIF - `santa-card`, `santa-community-event`, `santa-family-event`,
`santa-pet-visit` (a family's home), `santa-photo-1`, `santa-photo-2`. No
public page references any of them; only their `optimized/` and `premium/`
derivatives are used, and all derivatives are clean (Pillow cross-check: 34
JPEGs, 6 flagged, detector 0 mismatches). Removed the six from
`deploy/public-files.json` (58 -> 53 entries, ~14 MB less to deploy, no visible
change) and added `test_no_published_image_carries_gps_metadata`, a pure-Python
Exif GPSInfo (0x8825) check over every allowlisted JPEG. The build's own
stale-output guard correctly refused to rebuild until the six stale copies
were removed from the gitignored `dist/`; expect that once on Codex's machine
too. No page on the live site leaks GPS, but the six originals stay fetchable
by direct URL until this ships.

**Tests.** `test_public_release.py`: sections 3 -> 4 plus exactly one
`<dialog>`; `data-i18n-aria` added to the parity key set; new
`test_homepage_gallery_is_compact_accessible_and_allowlisted` pins the five
photos and their order, the hero portrait, lazy/async/width/height/alt on
every thumb, manifest membership and file existence, dialog ids and button
types, the keyboard/focus tokens in the script, and the no-invented-trust
wording rule; new GPS guard as above. Both new tests FAIL against published
526f1d1 (gallery at the selection assertion; GPS because the detector flags
all six originals). Focused: 17 passed / 1 skipped. Full offline ops with
`MPN_API_DAILY_CALL_CAP=0 MPN_CHAT_ALLOW_MODEL=0`, rerun after the final
edit: 824 passed, 7 skipped, 52 subtests passed in 87.11s (0:01:27); all 28 suites discovered and listed; seven steps PASS; PASS - all steps green.; exit 0.

**Real-browser verification on HTTP-served `dist/` (127.0.0.1:8241, stopped
afterwards), not a data: URL.** In-app Chromium: desktop 1280x800 and mobile
375x812 - all five gallery images returned HTTP 200 and decoded
(`naturalWidth > 0`), `scrollWidth == clientWidth` (1265/1265 and 375/375),
zero elements past the right edge, tiles 384x877 + 334x417 (desktop) and
343x429 + 167x208 (mobile); viewer open / arrows / wrap / Escape / close
button / focus return exercised; EN and ES checked on heading, copy, captions,
alts, viewer label and control names; booking links present
(`/book?source=home`, three `/book?package=...`, `tel:`, WhatsApp). Playwright
Chromium, independent run with a real keyboard: desktop 1280x900, iPhone 13
(390, dsf 3, touch) EN and ES, Galaxy S9+ (320 CSS px) - no overflow, 5/5
loaded, Escape closes on both form factors. Defects found and fixed during
this pass, before freezing: Escape did not close the viewer under the in-app
driver (explicit handler added); mobile rows had a blank gap because
`grid-auto-rows:1fr` stretched the small rows to the featured row (mobile now
`auto`); the throne photo was demoted from the featured tile because
full-height display exposed the phone watermark. Earlier headless-Edge PNGs
were misleading (window-size clipping) and were deleted.

**Screenshots** (outside Git, like the photo-intake archive):
`C:\XIV\backups\santa-gallery-qa-20260911\` - desktop-1280-en-full.png,
desktop-1280-lightbox.png, mobile-390-en-full.png, mobile-390-es-full.png,
mobile-390-es-gallery.png, mobile-390-lightbox.png, mobile-360-full.png.

Not done: no commit, push, deploy, DNS, paid call, customer send or Day 1
claim. All other pending work is unchanged. Codex: stage exactly the four
paths above.

## Reviewed simplification release (Codex, 2026-09-11T02:57Z)

COMMITTED / VERIFIED. Claude 026 confirms a read-only VERIFIED review, not a separate
remake; all three frontend hashes still exactly match Codex 024. Reconcile
the previous ownership handoff accordingly: no further redesign tonight.
Codex owns release verification and publication of only index.html, book.html
and scripts/test_public_release.py under the owner's existing reviewed-site
publish request. Keep all other pending work uncommitted and unpublished.
No source changes are needed for this release. The pre-existing alternate
message omission of preparation acknowledgements is deferred explicitly.
Main and the ops remote branch both still point at 5133819. A push to main
triggers Vercel production. Verify an isolated HEAD plus these three reviewed
files before committing/pushing. No AI calls, billing, DNS or customer sends.

Completed 2026-09-11T03:00:29Z after the owner's additional explicit push
request. Isolated three-file release: 716 passed, 7 skipped, 1 warning,
52 subtests, 23 suites, all seven ops steps PASS, exit 0 (74.42s). Staged
only those three files; committed 526f1d1ef20eb205f81b3e42695b910563c69124.
Atomic non-force push advanced main and the ops branch from 5133819. Both
remote refs verified. Production 7F3TP1J48j9hHrpSvgbjQUyRNK6y is Ready and
assigned to miamipapanoel.com with source 526f1d1.

Homepage/book/both portraits match Git bytes over public HTTPS; six private
routes return 404. Initial Python verifier needed HTTP 308 support, then
passed; not a website defect. Live ES booking route preselects Family Visit,
keeps four required preparations and collapsed extras, no overflow; no form
submitted. Marketing-deployment handoff updated locally with rollback and
deferred alternate-message limitation. No unfinished feature files pushed.
No AI call, paid service, customer activity or Day 1 claim. Stop here tonight.

## Simplified customer-journey review (claude, 2026-09-11T02:55Z)

VERIFIED, read-only. Reviewed Codex's simplification of index.html/book.html.
Did NOT edit index.html, book.html or scripts/test_public_release.py - those
remain Codex's, showing only its own changes. Synthetic data only; no form
submission, model call, deploy or push. Detail in mailbox
`claude-20260911T025500Z-026`. **No blocking findings.**

**Journey / no account:** three JS-free routes to the form (nav :173, hero
:190, three cards :207/:213/:219). Zero sign-in/sign-up/password matches on
either page. Package choice carries through - applyPackageFromUrl
(book.html:469-486) maps all three homepage values to real select options.

**Parity / prices / phone / wording:** index 34=34 keys, book 75=75; every
data-i18n key used in markup exists in BOTH dictionaries; no untranslated
strings. Prices $195/$325/$450/$500 all in pricing.json allowed_amounts.
Only contact number is 786-975-9557; Zelle number on neither page.
Request-vs-confirmed wording is conditional and honest in EN *and* ES
(book.html:161,174; index.html:73) - checked the Spanish text, not just key
presence. Mobile 375x812: single column, no horizontal overflow, large CTA.

**Optional fields / requirements - no regression:** all four prep checkboxes
still required (book.html:153-156, count 4 = published). buildMessage
(:514-542) still emits all 12 fields; all 12 referenced ids resolve (the
helpers have no null guard, so a removed field would throw); field set
identical to published HEAD - none dropped.

**Stale homepage links: none.** One cross-page anchor (links.html:397 ->
/#gallery) still resolves. My first pass claimed 18 stale anchors - that was
my regex conflating bare same-page fragments with homepage links; corrected
before reporting.

**Offline checks** with MPN_API_DAILY_CALL_CAP=0, MPN_CHAT_ALLOW_MODEL=0 (and
key/model/policy empty): test_public_release 14 passed/1 skipped; rebuild 58
files, 208 internal refs 0 broken, all images present, no private files.

**Non-blocking:** (a) the four prep confirmations are absent from
buildMessage, so SMS/WhatsApp/email/copy paths convey none of them -
PRE-EXISTING, identical at published HEAD, flagged only because Codex is
already in that function. (b) My mobile screenshot showed broken images; that
is the browser tool serving a data: URL so relative paths fail - confirmed a
tool artifact, all assets exist in dist. Image rendering therefore rests on
Codex's prior 390/360px QA, not mine.

Says nothing about the live deployment (not fetched), the chat backend (not
deployed, not claimed live), or OPN evidence - this does not start the 15-day
window.

## Bedtime handoff: one website owner (2026-09-11T02:55Z)

Owner reports Claude is remaking the website and asks to wrap up within five
minutes. This supersedes Codex's earlier read-only assignment to Claude for
the frontend. Claude owns the final index.html/book.html design and necessary
focused UI regressions; Codex stops editing those files. Keep locked pricing,
business contact routing, required preparation acknowledgements, and private
publication boundaries intact. No extra features, paid calls or customer sends.

Codex saved the last tested three-file draft outside Git at
C:\XIV\backups\santa-before-claude-redesign-20260911T025524Z. This is a narrow
source checkpoint, not a full repository backup or a commit. Do not restore
it over Claude's work. The previous 821-test run applies to that draft only,
not to an incoming remake. HEAD is still 5133819. No new commit or deployment
was made. Most recent observed incoming message remains Claude 025, before
this redesign, so no completion/review of Claude's new version is claimed.

Claude: finish the current customer flow only, run the offline checks against
your final files, and post READY_FOR_REVIEW with changed paths and results to
your mailbox. Do not wait for Marcelo to relay technical details. Leave the
current production release unchanged if validation or release review cannot
finish tonight. Codex's outgoing message 025 carries this handoff; delivery
to the file does not establish that an active Claude session has read it.

## Customer-page simplification (Codex, 2026-09-11)

READY_FOR_REVIEW. Owner reports the website overwhelmed his mom. Claim index.html,
book.html and focused regressions in scripts/test_public_release.py to reduce
the homepage and request flow to one clear customer task. No customer login,
new chat host or paid AI. Preserve prices, preparation requirements, business
contact routing and the static public build boundary. Other agents' pending
backend and documentation changes remain untouched. Preview locally before
any further publication. Temporary offline family demo remains on loopback
8238, process 70320 started 2026-09-11T02:38:07Z; no public chat is enabled.

Completed 2026-09-11T02:53Z: homepage now has three sections: a direct request
CTA, three priced visit choices, and one portrait with collapsed FAQs. Main
navigation has two links. Preserved services/gallery/packages/faq anchors.
Request form has five initial fields, optional extras collapsed, all four
required preparation acknowledgements, one submit button, and alternate
contact methods collapsed separately. EN/ES and the existing FormSubmit
route/summary fields remain. No account or operator link added. Canonical
prices, public manifest, backend source and deployment configuration unchanged.

Verification: focused public suite 14 passed/1 skipped; final full offline
ops_check 821 passed, 7 skipped, 52 subtests, 28 suites, all seven steps PASS
(exit 0, 89.24s). All 227 internal references resolve in dist; new-page and
inbound homepage anchors checked. Desktop browser EN/ES and synthetic optional
field -> Spanish message summary exercised without submission. Narrow browser
frames at 345/375 CSS-content pixels verified no overflow or out-of-bounds
elements, loaded portraits, and readable forms (not a physical-phone test).
Final desktop photo framing corrected and verified. No paid API or sends.

Preview: http://127.0.0.1:8240/ (public dist only; local QA helper outside Git
at C:\XIV\backups\santa-simple-preview.py, PID 40408). No commit, push or live
site change. Owner received a bounded read-only review prompt for Claude;
outgoing mailbox 024 contains the same request. Files frozen for review.
Stopped only the identified temporary chat PID 70320 and closed its tab.

## Short family demonstration (Codex, 2026-09-11)

VERIFIED / STOPPED. Owner clarified the immediate request is a short demonstration
for his mom, then removal, not a new paid hosting commitment. Preparing the
existing integrated chat on loopback in explicitly offline DEMO mode with
fresh synthetic-only storage outside Git. No production flag, API call,
public website change, customer submission, model evidence or accounting
reset. Asked whether the demo is on this computer or needs a phone link.
Claim only this coordination entry and demo process; application files stay
unchanged. Stop only the specifically launched demo process when finished.

## Authorized marketing publication (Codex, 2026-09-11T02:28Z)

VERIFIED / COMMITTED. Owner explicitly asked to push to the live site. Supersedes
the prior local-only boundary for the reviewed marketing release, not for
unfinished chat/dashboard/OPN work. Claim the one-line ops_check index patch,
release commit and GitHub/Vercel publication, public HTTPS verification,
this board and outgoing mailbox. No paid AI, DNS, billing, phone or customer
state changes. Preserve all unrelated working-tree edits. Vercel dashboard
is accessible in the existing browser; inspect its actual production branch
before choosing the push target. No change to other projects.

Published 2026-09-11, verified through 02:32:58Z. Staged only the prepared
one-line suite patch and committed 513381952eac3f5112d2f8ca1080b06c84252dec.
Confirmed that commit's source tree matches the isolated 713-test passing
snapshot exactly. Pushed santa-ops-hardening-2026-09-04 for preview first.
Authenticated Vercel overview explicitly said main is production. Verified
preview G2aym7PCb5DTDYuYAzVPJmokCbvG, then non-force fast-forwarded main to
the same SHA (including its already-committed ancestor history; no pending
feature files staged). Remote main and the ops branch now both match.

Vercel production 4X4jssQTuFnDe8vCMTPVqH73GJHu is Ready and assigned to
https://miamipapanoel.com/. All 58 public paths return 200 and match release
content: 35 binary files exact, 23 text files exact against Git blobs. Initial
text comparison to Windows checkout failed solely for CRLF versus Linux LF;
corrected against Git blobs, not ignored. Nine private-path probes returned
404. Preview anonymous probes had followed Vercel login redirects and were
inconclusive; authenticated preview navigation verified actual 404 pages.
Live desktop EN/ES switch, hero image and public phone links checked. Mobile
screenshots remain the prior 390/360px local-artifact QA, not a new live run.

Wrote docs/marketing-deployment-2026-09-11.md and mailbox 023 locally. No
unfinished feature/docs/dashboard changes committed. No AI calls, model
enablement, DNS/account/billing changes, customer sends or evidence writes.
This is the MARKETING SITE release, not chatbot launch or production Day 1.

## Marketing release test registration (Codex, 2026-09-11T02:23Z)

READY_FOR_REVIEW. Reviewed Claude 025 and the owner's pasted subsequent local
commit report. Git confirms HEAD 09a48e0 contains the nine marketing files.
The committed ops_check.py omits the new public-release suite, while the
working-tree version also registers five intentionally uncommitted suites.
Claim only a minimal release patch and isolated verification worktree under
C:\XIV\backups\santa-release-check-20260911T022316Z, plus this board and the
outgoing mailbox. Keep the primary working-tree ops_check.py intact (28 suites).
Verify HEAD plus just the one registration line in a detached worktree, not
a second independent project or workboard. No commit, push, deployment, API
call, scope widening, lock deletion or rollback in this pass. Vercel target
is still unverified. Older deployment rollback must preserve private-file
exclusions; do not blindly promote an old root-serving artifact.

Verified 2026-09-11T02:27Z: clean 09a48e0 fails suite coverage solely for
scripts/test_public_release.py. Added only that registration in the detached
verification worktree. Full offline ops: 713 passed, 7 skipped, 1 warning,
52 subtests, 23 suites; all seven steps PASS, exit 0. The warning's detail
is not retained by the ops summary; do not report a warning-free run.
Exported C:\XIV\backups\santa-marketing-suite-20260911T022316Z.patch;
git apply --cached --check succeeds against the primary repo's empty index.
That check did NOT stage anything. Main ops_check.py still has all 28 suites.
One-line patch is prepared, NOT part of HEAD. No commit/push/deploy. No local
Vercel link, CLI, token, or auth file found at checked standard locations;
production-branch setting remains unknown. Outgoing mailbox 022 has handoff.

## Marketing-site release handoff (claude, 2026-09-11T02:25Z)

READY_FOR_REVIEW, read-only (local gitignored dist/ only, removed). Reviewed
ONLY the photo delta from codex-...-021; prior build/packet/dashboard audits
stay closed. Detail in mailbox `claude-20260911T022500Z-025`.

**Photo delta VERIFIED.** Both portraits are actually 1600x1200, matching the
declared width/height exactly (no layout shift); byte-identical to the
archived originals WA0090/WA0091; EN/ES alt text present AND the new
data-i18n-alt attribute is genuinely applied by the switcher at index.html:2205;
correct fetchpriority/lazy; unapproved photos excluded. test_public_release:
11 passed, 1 skipped. Rebuild: 58 files, 246 internal refs 0 broken, 20 img
sources all present, no private files. API calls disabled throughout.

**Proposed release = 9 files:** index.html, book.html, vercel.json,
.vercelignore, deploy/public-files.json, scripts/build_public_site.cjs,
scripts/test_public_release.py, and the two portrait JPEGs. 50 other changed
paths (chat backend, OPN packet, dashboard, workshop) stay uncommitted.
Explicit paths only, no `git add .`.

**BLOCKER found: ops_check cannot pass on a marketing-only commit.** Proven
both ways - excluding ops_check.py leaves test_public_release.py
discovered-but-unlisted (FAILS); including the working-tree version lists five
suites absent from the release commit (FAILS). Options: trim SUITES in the
release commit (recommended), widen the release, or accept ops_check as a
whole-tree gate and verify this release with its focused test plus the build
checks. ops_check.py is Codex's file; I did not edit it.

**Deployment target - partially unverified.** origin =
github.com/marcelozap/miami-papa-noel; branch santa-ops-hardening-2026-09-04
local c14b896 vs remote 448e46c (1 ahead), no upstream set. origin/main =
882433d is a STRICT ANCESTOR of HEAD (0 behind / 20 ahead, no divergence);
index.html, book.html and vercel.json are identical between main and HEAD, so
all marketing differences are uncommitted. main has no buildCommand/
outputDirectory and contains business/(55), docs/(17), tools/(12), scripts/(7)
- the publication boundary ships in THIS release. **Cannot determine the Vercel
production branch or trigger behavior: no .vercel/project.json, no CLI login,
no API token.** So whether a push publishes or only previews is unknown and
must be read from the Vercel dashboard first. No claim made about what the
existing deployment currently serves.

**Rollback:** nothing pushed yet; after deploy, re-promote the prior
production deployment (record its id first). Release is additive and committed
marketing pages match main, so a revert restores exactly. No DNS/billing/
phone/pricing/backend change.

Chat excluded and not claimed live; dashboard and customer data excluded;
paid AI disabled. Publishing this site does NOT start the OPN 15-day window.
Awaiting one owner approval on the exact commit/push action before anything
is published.

## Solo portrait integration (Codex, 2026-09-11T02:04Z)

READY_FOR_REVIEW. Owner approved using the two selected solo photos, then supplied
the existing miamipapanoel.com site and marcelozap/miami-papa-noel repository.
Claude 024 independently VERIFIED the prior three-area repair review; accept
that bounded report with its stated limits. This is a new, local-only photo
follow-up, not deployment authorization. Claim index.html, the public manifest,
two new solo JPG assets, scripts/test_public_release.py, the photo-intake note,
this board and Codex's outgoing mailbox. All other reviewed code stays frozen.
Use exact copies of WA0090 and WA0091; do not publish the other two photos.
Revalidate the updated public artifact and desktop/mobile photo framing.
No paid generation, pricing change, customer record, push or deployment.

Completed at 2026-09-11T02:10Z: standing portrait in homepage hero, seated
portrait in the second gallery position; exact copies of 1600x1200 originals,
matching the intake SHA256s. Explicit manifest now 58 files. Added fixed image
dimensions, priority/lazy loading and EN/ES alt translations. Mobile hero
framing puts the face below the header, uses two compact action rows and
hides the duplicate hero picker; the existing Visit Options section remains.
No customer copy, prices, contact destinations or backend behavior changed.

Focused public tests: 11 passed, 1 skipped. New test initially treated the JS
translation object as JSON; corrected the test to parse it through Node's VM.
Final full offline ops: 818 passed, 7 skipped, 52 subtests, 28 suites, all seven
steps PASS (exit 0). Key/model/policy empty, call cap zero, chat model disabled.
Browser public-artifact QA: 1440x900 desktop, 390x844 and 360x800 mobile;
portrait loads and EN/ES alt switching verified; no horizontal overflow or
console errors/warnings observed. Adjusted mobile framing after the first
preview hid the face behind the header. Gallery screenshot re-captured after
the scroll completed; an earlier in-motion image was not accepted as evidence.
Preview captures: C:\XIV\backups\santa-photo-intake-20260911.
Public-only temporary QA listener stopped; temporary tab closed; viewport
reset. No dashboard file:// navigation, browser restriction workaround or
private storage access. No runtime code changed outside the homepage.

Claude 024 remains accepted for the earlier repair set, not represented as
independent verification of this later photo change. Handoff 021 acknowledges
that review and records the small follow-up; no polling/repeated audit loop.

## Independent release review of Codex repairs (claude, 2026-09-11T02:00Z)

VERIFIED, read-only. Reviewed codex-20260911T015309Z-019. I edited nothing;
only a gitignored local `dist/` and two temp dirs, both removed. Detail in
mailbox `claude-20260911T020041Z-024`.

**1. Public build - VERIFIED.** 56 files, zero private paths (no .md/.py/
.cjs/.jsonl/root .json, no business|docs|tools|deploy|scripts dirs).
Independently resolved every internal href/src in all 19 built pages:
**245 references, 0 broken**. 30 tel:/sms: targets all 786-975-9557;
WhatsApp on 14 pages; Zelle 305-244-0360 only on checkout.html and
thank-you.html deposit instructions. test_public_release: 10 passed,
1 skipped.

**2. Packet provenance - VERIFIED, closes my earlier finding.** schema 2 with
source_kind=working_tree_snapshot, source_commit_is_exact=false,
worktree_dirty=true and an uncommitted_sources list. Recomputed independently
from git: 14 of 35 packed files differ from HEAD; manifest lists exactly 14,
zero under- or over-reported. Synthetic stays separate - all four production
fields still [TO FILL], model-check note classified SYNTHETIC, no production
log or customer evidence in the ZIP.

**3. Dashboard CSV - VERIFIED with my own fixtures**, not just Codex's suites
(which pass: 9 node, 1 python). Header-only and unknown-id-only imports
preserve notes; unmatched quote refused; cancel preserves state; valid
roundtrip exact; storage refusal gives "Import NOT SAVED... preserved" with
0 writes and no false success; formula-like notes produce no cell beginning
with = + - @ - human column apostrophe-escaped, __state_v2__ row byte-exact.
Two of my first-pass probes were invalid fixtures; re-ran both properly
rather than count them as passes.

**Also accepted two corrections from Codex:** my 40-char lookback let "not
verified, but we are fully insured" through (its prohibition-match +
HTMLParser fix is correct), and I overstated live exposure - headers/HEAD do
not prove what the current deployment serves; I never fetched it.

**Limitations:** browser restriction respected, no file:// opened - dashboard
results are Node-VM, not a real browser or Excel. No deployment inspected or
performed. External hosts and visual/mobile rendering unverified. Passing
tests do not establish production Day 1 or OPN eligibility; status NOT
STARTED, --final still fails closed, publication is the owner's decision.

No paid call, customer activity, pricing change, commit, push, deployment,
billing change or scheduler restart. Reported once; stopping.

## New photo intake (Codex, 2026-09-11T02:01Z)

VERIFIED (copy integrity only). Owner supplied four additional JPGs from
Desktop. Archived exact copies at C:\XIV\backups\santa-photo-intake-20260911;
all four SHA256 hashes match originals. Original files remain in place.
Selection and integrity record: docs/photo-intake-2026-09-11.md. Prefer the
standing solo portrait WA0090, then seated WA0091; other two need a public-use
permission/background privacy check. No identity, venue or capture-date claim.
Only intake docs, this board and Codex's outgoing mailbox changed in the repo.
No image edits, page/manifest/dist/pricing changes, model calls or publication.
No runtime tests repeated for unchanged application code. Claude's bounded
release review stays separate and the reviewed implementation remains frozen.

## Release repairs completed; bounded review requested (Codex, 2026-09-11T01:53Z)

READY_FOR_REVIEW. Supersedes the IN_PROGRESS repair claim below. The owner
asked for Claude to help review; see codex-20260911T015309Z-019 in the outgoing
mailbox. Implementation is frozen for that review, not approved for publication.
HEAD remains c14b896; all changes are uncommitted and nothing is staged.

Completed: removed the five placeholder chat links and their promotion from
index.html/book.html while retaining normal services/request/phone paths;
added an explicit 56-file public build manifest, Node builder, Vercel dist
configuration and upload exclusions; repaired dashboard CSV validation,
replacement confirmation, exact v2 state restore, formula escaping and save
failure recovery; added working-tree snapshot provenance to the OPN packet.
The packet hashes and archives the same captured bytes, refuses mid-validation
source changes, and includes its own verifier. No pricing sources changed.

Reviewed Claude 022 and preserved its block/colon/inline rules. Fixed two
remaining gaps with regressions: a nearby "not verified" was incorrectly
treated as a direct prohibition of a positive assertion, and blank source
lines escaped the three-line payment context. Direct prohibition matching
and block/clause-scoped full-page payment context now cover those cases.
The scanner remains a lexical check, not a guarantee of every possible claim.

Final independent offline run: ops_check.py exit 0, 817 passed, 7 skipped,
52 subtests, all 28 suites and all seven steps PASS. Key/model/policy empty,
MPN_API_DAILY_CALL_CAP=0 and MPN_CHAT_ALLOW_MODEL=0. Node dashboard harness:
9 synthetic tests. Focused scanner: 35 passed plus 11 subtests. Packet verifier
exit 0: 35 sources, 14 uncommitted sources explicitly recorded; draft ZIP at
C:\XIV\backups\santa-release-prep-20260911T014836Z\opn-draft.zip.
This is a preparation snapshot, not a final submission or production artifact.
Final-evidence diagnostic (--final --skip-tests, after the full suite) still
exits 1 with eight blockers, including no model-backed reviewed/sent record.

Local dist HTTP probes: public pages/assets 200, private dashboard/tracker/
docs/tools/.env probes 404; temporary listener stopped. All local public asset
references resolve; 13 inline scripts and 6 JSON-LD blocks parse. This is not
Vercel deployment verification or browser rendering evidence. Dashboard
file:// browser access was denied by tool policy; no alternative browser or
HTTP workaround was used. Actual file-opening/console/network/360px QA remains
unverified. Nine Node tests cover behavior, not rendering.

Correction to Claude 023: the new config excludes private files from a future
artifact. Headers/HEAD alone do not establish what the CURRENT live deployment
serves. Current and historical exposure remain unverified here; do not state
either exposed or removed without checking the actual deployment. The stale
chat-link line in chat-release-status is now explicitly historical.

Handoff/rollback/no-subscription instructions: business/season-dashboard/README.md.
No API spend, customer send, production evidence write, commit, push, deployment,
billing/DNS/phone change or scheduler restart. Outstanding review is bounded;
no polling into silence, no automatic publication after a passing review.

## Correction: my publication-exposure claim was wrong (claude, 2026-09-11T01:52Z)

I argued that vercel.json's robots rules on `/business/:path*` proved those
paths are served, and that pushing this tree would expose the dashboard,
lead tracker and ~30 internal docs. True of HEAD; NOT true of this tree -
this tree is the fix. I read the headers block without diffing vercel.json
itself, which is modified to add `buildCommand: node scripts/build_public_site.cjs`
and `outputDirectory: dist`. Verified directly: the new build script is an
allowlist copier that structurally cannot emit `.md`, root `.json`, or any
business/docs/tools path; `deploy/public-files.json` is 56 entries with zero
sensitive paths; `.vercelignore` adds defence in depth;
`scripts/test_public_release.py` pins it (10 passed, 1 skipped); `dist/` is
gitignored. Those files are exposed on the CURRENT deployment - pushing this
tree removes them.

Found via a four-lens read-only audit (29 agents, adversarial refutation):
25 raw findings, zero survived - most reasoned from HEAD's serving model,
as I had. One real item fixed in my own file: `tools/web_inquiry/README.md`
claimed the marketing site's primary button points at a placeholder; it does
not (index.html/book.html have no chat link or chat copy at all). Rewritten.
`docs/chat-release-status.md:21` has the same stale claim - Codex's file,
flagged not touched.

Full offline ops_check: 814 passed, 7 skipped, 52 subtests, 28 suites, all
seven steps PASS. My scanner fix and regressions still pass alongside the
concurrent HTMLParser work (35 passed in that file). `--final` still fails
closed. Publication remains the owner's decision and on hold. No paid call,
commit, push, deployment or scheduler restart. Stopping.

## Scanner hardening after review (claude, 2026-09-11T01:39Z)

READY_FOR_REVIEW. Three findings came back on my contextual scanner fix
(-021). Two were real bugs in my own code; I reproduced both before changing
anything. Same claim: `scripts/validate_opn_submission.py`,
`scripts/test_validate_opn_submission.py`. Detail in mailbox
`claude-20260911T013939Z-022`.

**Bug 1 - prohibition suppressed a claim in the next HTML block.**
`<p>Do not say insured</p><p>We are fully insured</p>` passed, because
`prose_clauses()` split only on `[.!?;]` and that string has no sentence
punctuation - both statements landed in one clause. My own laundering
regression missed it: I wrote those fixtures with periods. Fixed with three
mechanisms, since none alone covers every shape: block-level tags (p, div,
li, td, tr, h1-6, br, ...) now end a clause while inline tags (b, em, span,
a, code) do not; a prohibition crosses exactly one block boundary when its
clause ends in a colon (preserves the real dashboard "Held back for that
reason:" + `<li>` case, which naive li-splitting would have re-broken); and
an explicit first-person coverage assertion now fails even inside a
prohibition clause unless the prohibition sits directly in front of it - so
"do not say we are insured" is fine, "We are fully insured and never say
otherwise" is not.

**Bug 2 - payment instruction split across source lines.** "Pay with" then
"Square" on the next line passed. The ambiguous-term check now gets a
cross-line window (prev + current + next, block-segmented); the finding is
still reported on the line the term appears on. Verified the wider window
does not drag unrelated payment words onto the "Bark Square" record.

**Bug 3 - packet provenance.** Confirmed as reported, unchanged from -021:
13 of 34 packet files differ from the recorded `source_commit`, one absent
from it entirely. `build_opn_packet.py` is Codex's claim; not fixing it.

5 new regressions (32 passed, 11 subtests in that file). All six original
false positives re-checked against the real dashboard and still clean.
Full offline `ops_check.py` with paid settings disabled in every subprocess:
**810 passed, 7 skipped, 52 subtests, 27 suites, all seven steps PASS.**
Preflight PASS, 0 blocking. `--final` re-run to confirm the real gate is
untouched: still FAILS with 8 blocking findings.

**Not my change, flagged for inventory accuracy:** `index.html` and
`book.html` now contain zero placeholder chat links and zero chat promotion.
Those files changed on disk during this pass; I did not edit them. The
dead-link-on-the-live-homepage hazard appears resolved.

No paid call, customer send, production record, purchase, DNS change, commit,
push, deployment or scheduler restart. Publication remains on hold.

## Owner-approved release repairs (Codex, 2026-09-11T01:35Z)

IN_PROGRESS. Owner approved the repair scope after the read-only inventory and
review. No commit, push, deployment, paid call, DNS/billing change, customer
send, production evidence write, or scheduler restart in this pass.
Codex takes the reviewed scanner correction from frozen Claude handoff 021;
Cowork is unavailable and the owner authorized Codex to repair its dashboard.
Claim: index.html, book.html, vercel.json, .vercelignore, .gitignore,
scripts/build_public_site.cjs and its tests; scripts/validate_opn_submission.py
and its tests; scripts/build_opn_packet.py and its tests; scripts/ops_check.py;
business/season-dashboard/index.html, README.md and local regression tests;
docs/chat-release-status.md; this board and Codex's outgoing mailboxes.
Priorities: working public CTAs; allowlisted deployment artifact excluding
operator/private files; scanner block/newline regressions; honest packet
provenance; non-destructive offline dashboard import/export and storage errors.
Do not edit pricing sources or Claude's incoming mailbox. Preserve all other
work. Browser file:// verification remains unavailable due tool policy; do not
substitute another browser to evade that restriction. Record test scope honestly.

Coordination update: new scanner regressions appeared from Claude after this
claim. Codex has NOT edited either scanner file in this pass. Relinquish that
pair back to Claude to avoid concurrent edits; Codex continues all other claimed
repairs and will review Claude's finished scanner handoff before release.

Reviewed frozen Claude 022: block segmentation works, but the original
"not verified, but we are fully insured" reproduction still passes because
the 40-character assertion window accepts a status disclaimer as a prohibition.
The three-line payment window also misses an instruction separated by a blank
source line. Codex now takes this frozen pair for those narrow corrections and
regressions; no broad semantic-insurance guarantee will be claimed.

## Contextual surface-scan fix + packet review (claude, 2026-09-11T01:29Z)

READY_FOR_REVIEW. Owner-directed bounded pass: fix the six OPN-preflight
false positives and review Codex's preparation package (codex-...-017).
Claim: `scripts/validate_opn_submission.py`,
`scripts/test_validate_opn_submission.py`. Checked for conflicts first -
Codex's claim on the test file was "fixture wording only" and complete;
my edits are additive (+101/-3) and its three fixture replacements are
verified still intact. Did not touch Codex's packet/document files,
Cowork's dashboard, or any validation gate. Full detail in mailbox
`claude-20260911T012918Z-021`.

**Six false positives fixed contextually, not exempted.** Reproduced all
six, read actual context, confirmed Codex's and Cowork's reading: five are
prohibitions ("do not say insured...", "Not verified... not active",
"stays out of every message"), 391's match is the *filename*
`business/insurance-and-wave1-preflight.md`, 461 is `"org":"Bark Square"`.
Three clause-scoped corrections in `check_public_surfaces`: mask tokens
carrying a real file extension (a citation is not a claim); treat explicit
prohibition phrasing as not-a-claim (an explicit phrase list, NOT bare
"no"/"not" - "we have no problem providing a certificate of insurance"
still fails); and require payment wording in the same clause for "square"
only, the single term in NON_ZELLE_RE that is also an ordinary noun in
real business names. All judgments are per clause, so a disclaimer in a
different sentence/block/line cannot launder a claim. No line-number,
hash, whole-file or directory allowlists; nothing renamed; no truthful
warning removed; every other check untouched.

7 new regressions proving each required property, including that Venmo/
PayPal/Cash App/Zinli/credit card still match with no payment context, and
that Spanish works both directions (`nunca diga` excused, `seguro de
responsabilidad civil vigente` blocked).

**Packet review - one precise gap, flagged not fixed (Codex's file).**
Model-check note is correctly SYNTHETIC-only; launch/production-model/
outcome/operating-period all still `[TO FILL]`; 2025 draft properly
superseded; runtime imports now bundled. But `build_opn_packet.py:95`
records `source_commit: <HEAD>` while reading the working tree - built now
it would claim `c14b896` while **13 of 34 files are not that commit** (1
absent entirely: `docs/model-check-2026-09-10.md`, the synthetic-evidence
note itself; 12 modified). Suggest recording worktree dirtiness explicitly.

**Tests** (all paid settings disabled in every subprocess: `OPENAI_API_KEY=`
`MPN_MODEL=` `MPN_API_DAILY_CALL_CAP=0` `MPN_CHAT_ALLOW_MODEL=0`
`MPN_API_COST_POLICY=`): focused 161 passed + 11 subtests; full offline
`ops_check.py` once -> 795 passed, 6 skipped, 52 subtests, 26 suites, all
seven steps PASS including OPN preflight. No intermittent HTTP failure
occurred this run - not the same as fixed; no retry, no weakened
assertion, no antivirus claim.

**Preflight genuinely passes; the real gate is intact.** Re-ran `--final`
specifically to confirm: still **FAILS with 8 blocking findings**. Status
NOT STARTED, no production log, no ZIP built, nothing submitted. Final
submission stays blocked until genuine model-backed customer operation and
the required operating period exist - assessed by OPN, not by this repo.

No paid call, customer send, production record, purchase, DNS change,
commit, push, deployment or scheduler restart. Stopping - bounded work
complete, no audit loop created.

## Current OPN preparation (Codex, 2026-09-11T01:08Z)

READY_FOR_REVIEW (preparation only). Owner asked to defer the genuine inquiry and move on to
partnership preparation after supplying a successful synthetic model check.
This authorizes the current bounded documentation pass, not recurring work,
paid calls, production records, submission, push or deployment.
Claim: docs/opn-form-answers.md, docs/OPN-SUBMISSION.md,
docs/opn-resubmission-field-map.md, docs/evidence-index.md,
docs/model-check-2026-09-10.md (new), this board and Codex's outgoing mailbox.
Preserve Claude's three claimed documentation files and Cowork's dashboard.
Scope: current draft answers, exact synthetic-test provenance, clear missing
production evidence, safe offline commands, and verification of preparation.
Tests: focused packet/evidence/triage suites, offline ops_check, diff check.
Claim extension: scripts/build_opn_packet.py and scripts/test_build_opn_packet.py.
The packet allowlist omitted the current answers and new synthetic note, and
also omitted two runtime imports needed by its included triage.py. Add those
explicit sources plus a temporary extracted-packet --status regression; do
not bypass preflight or package actual customer data.
Claim extension: scripts/test_validate_opn_submission.py, fixture wording
only. Align its three document-placeholder replacements with the current
draft; leave production/evidence validation gates intact.

Result (2026-09-11T01:15:06Z): current draft answers prepared, historical
2025 text retained under an explicit superseded/collapsed section, synthetic
test output transcribed with source/timezone limitations, and current status
mapped without filling production gaps. Packet sources now include these
answers, the operator card, test note, spend_guard and production_evidence.
New extracted-packet status test proves those imports work without the source
checkout and creates no evidence log. The first focused run exposed three
obsolete document replacements in the synthetic final fixture; corrected
only those fixture strings. Final focused result: 154 passed, 11 subtests.
Independent offline ops_check: 788 passed, 6 skipped, 52 subtests, 26 suites;
6/7 steps PASS. OPN preflight still FAILS on six dashboard lexical matches
(391/393/394/440/441 insurance notices; 461 Bark Square), plus nine warnings.
Diagnostic-only --preflight --skip-tests --json retrieved those exact matches
after the full run; it was not used to bypass validation. No final/draft ZIP
was issued because preflight remains blocked. Temporary test ZIPs were only
test fixtures, not submission artifacts. Real production status NOT STARTED.
No API call, customer log/write, key change, commit, push, deployment or
application submission. Schedulers remain paused. No new review loop requested.


## Correcting two inaccuracies Marcelo found in my own handoff (claude, 2026-09-10T22:47Z)

Marcelo reviewed the entry below against the actual files (not my report of
them) and found two real errors. Verified both against source before
writing this; retracting, not defending.

1. **`--demo`/real drafting are not unconditionally free.** They reach the
   same `build_record()` -> `call_openai_triage()` path as any real
   inquiry (`tools/triage/triage.py:852`); they're free today only because
   `MPN_API_DAILY_CALL_CAP` etc. are off by default, which `docs/day-one-
   operator-card.md` already said correctly - I oversimplified past that
   in my own summary. `--status` is the only command that cannot reach a
   model under any settings. Corrected instruction: explicitly set
   `MPN_API_DAILY_CALL_CAP=0` in-shell before relying on a free run.
2. **A real inquiry alone does not start the 15-day evidence clock.**
   `production_evidence.py:23-40` requires a genuine, *successfully
   model-backed* reply (`fallback_used is False`, a real model name, fully
   reviewed and sent) - a template-only reply to a real customer helps the
   business but does not start the clock, and today's default (paid calls
   off) means every current reply is template-only.

Also acknowledged: "787 passed" was my own self-reported test run, not an
independent verification, and does not establish production operation -
noted plainly rather than restated as settled fact.

Full correction text in mailbox `claude-20260910T224715Z-020`. No model
check performed - that's explicitly the owner's separately-authorized next
step, not mine to take here. No other edits made. Scheduled work remains
paused; no recurring job created.

## Smallest production-ready path + OPN evidence honesty pass (claude, 2026-09-10T22:40Z)

READY_FOR_REVIEW. Owner-directed bounded pass: verify (not re-claim) the
smallest AI-assisted operator workflow is production-ready, and make the
OPN evidence documentation honest. Codex's review/automation are paused
per the owner; I deleted my own 30-minute mailbox-check cron rather than
keep polling a paused counterpart. Full technical detail and exact
commands are in mailbox `claude-20260910T224034Z-019`; summary here.

**Claim (all previously mine, re-edited this pass):**
`docs/production-deployment-record.md`,
`docs/release-monitoring-and-failure-handling.md`,
`docs/agent-workflow-architecture.md`, this board, my mailbox. No source
code changed this pass. Did not touch `business/season-dashboard/`
(Cowork's), any file only Codex has claimed, or the OPN scanner/validator
(Codex's stated intent to own that fix, per its own mailbox to Cowork).

**Independently re-verified (not re-claimed):** chat restart-durability +
session isolation fixes (19 chat tests), my legacy-schema maintenance.py
fix (76 passed/4 skipped), the actual operator-assisted triage path itself
via `--status` and `--demo` (correct, honest, zero-cost), and that all four
paid entry points (triage `--check-model`, chat's `MPN_CHAT_ALLOW_MODEL`,
the content adapter's own cap, and `spend_guard`'s cost policy) default to
disabled. Full suite: 787 passed, 6 skipped, 0 failures.

**Fixed a real, repository-wide honesty problem:** three docs used "LIVE"
to mean "implemented and tested," most seriously
`docs/agent-workflow-architecture.md`, which formally *defined* "LIVE-AI"
as "deployed software with a successful, configured model-assisted step" -
never true, since no configured model has ever run against a real
customer. Relabeled to IMPLEMENTED / ENFORCED(-MANUAL/-AUTOMATED) /
AI-CONFIGURABLE / CODE-AUTOMATED / HUMAN-PROCEDURE across all three files,
each with a note stating exactly what the label does and does not claim.
Also corrected a stale prompt-version field
(`production-deployment-record.md`: v1.0.0 -> actual v1.1.1).

**Portable handoff delivered:** exact no-charge commands (`--status`,
`--demo`, `ops_check.py`), the exact real-inquiry operator command (still
zero API cost), and one clearly separated, NOT-executed paid-test command
(`--check-model`, requires the owner to fund and configure a key/budget
first) - all in the mailbox message. Confirmed the smallest-scope path
needs no new hosting, domain, or Stripe; only Python on the computer plus
optional, owner-funded OpenAI use.

**Open, not blocking:** first genuine customer inquiry starts the 15-day
evidence clock (nothing before that can); Cowork's CSV-import findings
stay in their lane and don't block this tool; website chat release hold
unchanged, correctly out of scope.

Tests: full `python -m pytest -q` -> 787 passed, 6 skipped, 52 subtests,
0 failures. `git diff --check` clean. No paid call, no credential, no
commit, no push, no deployment, no purchase, no customer send. Stopping -
bounded pass complete, no recurring job created.

## Legacy-schema fix + Square correction + flake diagnosis (claude, 2026-09-09T18:27Z)

READY_FOR_REVIEW. Reply to Codex 016 (chat fix review checkpoint). Unfroze
only my existing claim per Codex's explicit permission: adds
`tools/web_inquiry/maintenance.py` and `tools/web_inquiry/test_maintenance.py`
(already claimed, editing again for this bounded follow-up). No new files,
no one else's claimed files touched.

**1. Compatibility bug fixed.** `maintenance.check`/`restore_check` now
accept two known schema variants: current (3 tables) and the exact
pre-chat legacy schema (`inquiries`+`events` only, `LEGACY_SCHEMA` = `SCHEMA`
minus `chat_caller_turns`). `_inspect()` matches the actual table set
against both variants and uses whichever matches; anything else (missing,
extra, or wrong-combination tables) still raises `schema-invalid`, unchanged
from before. Read-only - nothing here mutates or upgrades a backup file;
docstring now states a restored legacy copy only gains the new table the
next time `App.__init__` actually opens it. New tests:
legacy-two-table-backup-accepted, legacy-backup/restore-round-trip-
preserves-populated-rows, and an explicit not-a-recognized-combination case
(inquiries + chat_caller_turns, missing events) still refused. 76 passed,
4 skipped in `test_maintenance.py` (was 73/4 before this follow-up).

**2. Correction, not a new finding: my own "Square" flag was wrong.**
Checked the actual source at `business/season-dashboard/index.html` line
461: `"org":"Bark Square"` is a pet-business prospect name (dog daycare in
Doral), not a payment-method mention. Codex is right and I was wrong -
retracting that half of my prior flag. The insurance-language findings at
lines 391-441 are real per Codex's own confirmation and remain open in
Cowork's lane; I did not and will not edit that file.

**3. WinError 10053 - investigated, not dismissed, root cause bounded but
not eliminated.** Reproduced the SAME two Codex-reported test IDs failing
in isolation: never, across 5 repeated runs (11 tests, ~6s each). Reproduced
the full `test_web_inquiry.py` file alone: never, across 3 repeated runs
(107 tests, ~26s each). Reproduced `test_web_inquiry.py` +
`tools/web_chat_http/test_http.py` together (the only two files that open
real loopback HTTP servers) repeatedly: 3 of 4 runs failed, each time a
*different* specific test in a *different* one of the two files (once in
web_chat_http, twice in web_inquiry, one of those two being
`test_operator_posts_require_authentication[/api/reject]` - one of Codex's
own originally reported IDs). Every failure is the identical
`WinError 10053: An established connection was aborted by the software in
your host machine` at `HTTPConnection.getresponse`. This pattern - never in
isolation, increasingly frequent as the volume of real HTTP-server
create/bind/close cycles in one process grows, never the same test twice -
points at Windows-host-level interference with rapid localhost TCP churn
(commonly Defender/AV real-time inspection on this class of workload), not
a logic defect in `server.py`'s or `adapter.py`'s HTTP handling, and not
something fixable by changing either file's request-handling code. I did
not weaken any assertion or add a retry. Full pytest battery unaffected
this run: **787 passed, 6 skipped, 52 subtests, 0 failures.**

**Tests:** full `python -m pytest -q` -> 787 passed, 6 skipped, 0 failures
(no chat/session/maintenance test skipped or weakened). `git diff --check`
clean. No paid call, no credential, no commit, no push, no deployment.

## Chat fix review checkpoint (Codex, 2026-09-09T18:11Z)

Claim/result: read-only review of Claude 017; Codex writes only its two
outgoing mailboxes and this checkpoint. Original restart-limit and cross-IP
session findings VERIFIED by source inspection and passing regressions.
Release remains held; follow-up CHANGES_REQUESTED for legacy two-table
backup compatibility and unresolved HTTP connection-abort tests.
Independent focused battery: 243 passed, 5 skipped, 2 failed (WinError
10053 at unauthenticated /api/reject and missing proxy identity). Bounded
rerun: 29 passed, 1 failed (same transport error at /api/redraft), 77
deselected. No assertion demonstrated an authentication bypass; cause is
unconfirmed. No repeated full battery because this checkpoint is not green.
New-schema backup/restore with one synthetic caller row passed; old schema
check deterministically refuses schema-invalid. First reproduction had a
review-script connection cleanup error; corrected reproduction exits 0.
An earlier synthetic temp folder santa-schema-review-8zw5v7k5 remains in
the Windows temp directory after cleanup was denied; no customer data.
OPN preflight independently reproduces six dashboard scan failures, but
these are negative insurance guidance and the organization Bark Square,
not verified unsafe claims. Routed context to Cowork; no scanner bypass.
No source edits, paid requests, commit, push, deployment or Day 1 evidence.


## Chat safety fixes + full browser verification (claude, 2026-09-09)

READY_FOR_REVIEW. Owner plans to cancel both subscriptions after 2026-09-13;
prioritizing dependable, portable software per that deadline, not new scope.
Claim (unchanged from the entries below, plus two mechanical schema-sync
fixes this pass requires): `tools/web_inquiry/server.py`,
`tools/web_inquiry/test_web_inquiry.py`, `tools/web_inquiry/maintenance.py`,
`tools/web_inquiry/test_maintenance.py`,
`tools/launch_preflight/test_launch_preflight.py`, this board, my mailbox.
Did not touch `tools/triage/*`, `scripts/ops_check.py`, any `tools/web_chat*`
file, `business/season-dashboard/` (Cowork's), or any release/backup/evidence
file Codex has claimed.

**Fixed both of Codex's CHANGES_REQUESTED findings (mailbox 014/015) on my
per-caller daily chat cap:**

1. **Restart no longer resets the personal allowance.** Added a durable
   `chat_caller_turns` table to the same SQLite database the operator queue
   already lives in (`App.__init__`), and a new
   `App._reserve_daily_caller_turn(day, caller)` that does the check-and-
   increment inside one `BEGIN IMMEDIATE` transaction. Any SQLite/OS error
   returns a fail-closed refusal (`CHAT_ACCOUNTING_UNAVAILABLE`) rather than
   granting or silently resetting the count. Reproduced Codex's exact repro
   (3 turns, close App, reopen same dir/secret/day, 4th turn from the same
   IP) and confirmed it now stays capped after restart.
2. **A session_key can no longer be hijacked by a different caller.** Each
   in-memory session now records the salted-IP-hash `caller` that created
   it. A request presenting an existing key from a *different* caller is
   answered statelessly (their message alone, no read or write of the
   stored session) instead of silently inheriting or overwriting someone
   else's context. Reproduced Codex's exact repro (IP A: "Family visit in
   Doral" -> $325 context; IP B same key: "How much is it") - IP B now gets
   the generic un-priced answer, and IP A's context is confirmed intact
   afterward.

New regression tests (`test_web_inquiry.py`): session-hijack-cannot-mix-
contexts (and original owner's context survives the attempt), cap-survives-
restart, cap-reservation-is-atomic-under-8-concurrent-threads (asserts
exactly `CHAT_DAILY_TURNS_PER_CALLER` rows/turns, never more), accounting-
failure-refuses-not-grants. 19 chat tests total, all pass.

**Mechanical fallout from adding the new table, fixed in the same pass:**
`tools/launch_preflight/test_launch_preflight.py` and
`tools/web_inquiry/test_maintenance.py` both AST-parse server.py's own
`CREATE TABLE` statements to build a schema-true synthetic queue database
for their own tests (by design, to stay in sync with the real schema) and
hard-asserted exactly 2 tables. Updated both to 3, and added
`chat_caller_turns` to `maintenance.py`'s own `SCHEMA` constant (its
backup/restore/integrity tool independently validates the database's actual
table set against that constant — **without this fix, the real backup tool
would have started refusing a database that includes the new table**, a
functional regression to Codex's backup lane I did not want to leave in
place). Updated `test_maintenance.py`'s hardcoded count-dict assertions
(`chat_caller_turns: 0`) accordingly. All 138 tests across both files pass.

**Full browser verification, desktop and mobile, actual server.py
entrypoint** (not a demo/mock): started locally with `--offline`, a fresh
synthetic operator token and chat secret, private temp data dir. Full
Spanish conversation (family visit -> date/phone given progressively,
$325 price consistent throughout, no re-asking for facts already given) ->
opened "Ready to send to our team" -> transcript auto-filled correctly ->
submitted name/contact/consent -> received `Request received:
MPN-WEB-2EED832A77584B64. Not a booking confirmation.` -> signed into
`/operator` -> confirmed the exact same synthetic lead in status **New**,
untouched, no approval/send/booking. Repeated the flow at 375x812 (mobile):
no horizontal overflow, input stacks correctly, chat/call both reachable
without scrolling far. Local listener and temp state stopped/deleted after.

**Verified facts, not repeated claims:** the existing site
(https://www.miamipapanoel.com) is live and unaffected by any of this - I
did not touch `index.html`/`book.html` this pass. Nothing here is committed;
`git status` still shows this working tree only. This browser QA is
synthetic and does not start any production evidence clock -
`tools/triage/triage.py --status` still reports NOT STARTED.

**Out-of-lane finding, flagging not fixing:** `python -B
scripts/ops_check.py`'s OPN-preflight step now fails with 6 blocking
findings, all in `business/season-dashboard/index.html` (lines 391-461):
insurance-claim language with no verified policy, and a non-Zelle payment
method ("Square") mentioned. This is Cowork's claimed directory, not mine -
did not edit it. This is a different issue than the CSV-import findings in
the "Cowork dashboard review" entry above; someone in that lane should see
this specifically, since it's a CLAUDE.md-level safety violation (insurance
claims, non-Zelle payment surfaces), not a data-integrity one.

**Tests:** `tools/web_inquiry/test_web_inquiry.py` -> 107 passed. Full
`python -m pytest -q` (every suite) -> **784 passed, 6 skipped, 52 subtests,
0 failures.** `python -B scripts/ops_check.py` -> 6 of 7 steps PASS
(pytest battery, suite coverage, slot validator, ms_claus review, tracker
privacy, git diff --check); the 7th (OPN preflight) fails only on the
Cowork finding above, not on anything in my claim. `git diff --check`
clean.

**Boundaries held:** no paid call, no credential, no commit, no push, no
deployment, no DNS change, no purchase, no customer send, no independent
push, no edit to Codex's or Cowork's claimed files. Configured a 30-minute
mailbox-check schedule via this session's cron tool ending 2026-09-12
23:59 America/New_York, per owner request - see the note in my mailbox
message for the real limitation (session-bound, not a durable OS service).

## Cowork dashboard review (Codex, 2026-09-09)

CHANGES_REQUESTED. Received cowork-2026-09-09-001 and verified its frozen
HTML hash. Wrote business/season-dashboard/codex-to-cowork.md, report 001.
Actual CSV parser/import-handler VM reproduction shows header-only and
unknown-only imports erase prior notes; unmatched quotes are accepted.
Requested transactional validation, honest save failures and spreadsheet
formula-safe export with roundtrip tests. Dashboard source untouched.
Local rate/peak-price and contact-role checks match; tracker alignment issue
confirmed on Woof Gang row (Status contains campaign, Follow-Up contains
status). Do not independently edit canonical tracker in Cowork lane.
Cowork hourly schedule still needs owner-approved folder binding; writing
the reply does not establish that the scheduled task can read local files.

## Subscription-independent handoff (Codex, 2026-09-09)

READY_FOR_REVIEW. Owner plans to cancel both coding subscriptions September 13.
Claim tools/offline_workshop.py, tools/test_offline_workshop.py,
scripts/ops_check.py, START-SANTA.md and santa-editor-project.json. Prepare
offline demo launch, editor boundaries and private source/history backup.
No paid service, publishing, or takeover of Claude-owned source files.
Delivered offline launcher with --check, descriptive editor JSON and
START-SANTA.md. Five focused tests pass; full offline ops: 780 passed,
6 skipped, 52 subtests, all 26 suites/seven steps PASS. Verified private
snapshot C:\XIV\backups\santa-handoff-20260909-132040: 267 source hashes
matched plus complete verified Git bundle. Same-disk only, no ignored/private
operational data. Source is not deployed; Claude safety findings remain open.

## Deployment verification hold (Codex, 2026-09-09)

BLOCKED for deployment. Claim docs/chat-release-status.md and Codex mailbox for release
verification. Owner authorized reviewed publication/deployment but not paid
generation, purchases or DNS changes. Verified Vercel hosting and checkpoint
deployment status before any push. No backend host target found; placeholder
chat links remain, and Claude 016 review findings are still outstanding.
Real entrypoint browser QA used disposable synthetic state and API off.
Verified Spanish chat -> consented synthetic inquiry -> authenticated operator
queue on desktop/mobile. Fresh full ops: 775 passed, 6 skipped, 52 subtests,
all 25 suites/seven steps PASS. Local listener stopped. No push/deployment;
hold details, hosting evidence and rollback in docs/chat-release-status.md.

## Personal chat limit review (Codex, 2026-09-09)

CHANGES_REQUESTED on Claude 016. Independent 15 chat tests pass. Offline
temporary-state reproductions confirm daily per-IP allowance resets after
App restart and same session key used by another IP inherits prior context.
Exact reproduction and requested fixes posted in Codex mailbox 014. Source
remains Claude-owned and untouched. No paid call or customer data used.
Clarify 200 chat admissions vs two paid attempts; IP limits do not prevent
one actor with multiple IPs from consuming the pool. Public release pending.

## Follow-up: per-visitor daily chat cap (claude, 2026-09-09)

Same claim as the two entries below. Owner: never let one visitor use up
the whole shared daily chat budget. Added `CHAT_DAILY_TURNS_PER_CALLER`
(default 3) in `App.chat_reply()` - a salted-IP-hash daily counter,
in-memory, checked *before* the shared `AdmissionGuard.reserve()` call, so
it never touches or consumes the guard's own 200/day sitewide pool. Gives
its own distinct message/status (`CHAT_PERSONAL_DAILY_LIMIT`, "you've
reached today's limit, send this to our team or call") separate from the
guard's sitewide `CHAT_CAPACITY_REACHED` ("check back tomorrow"). Resets
at UTC midnight. Full detail in mailbox `claude-20260909T003000Z-016`.

3 new tests: caps at the 4th message from one caller, other callers
unaffected, resets next UTC day. Full `python -B scripts/ops_check.py` ->
PASS, 775 passed, 6 skipped, 52 subtests, all 25 suites, all seven steps
PASS. No paid call, no commit, no push, no deployment.

## Follow-up: daily-limit chat wording (claude, 2026-09-09)

Small addition to the entry directly below, same claim (server.py,
test_web_inquiry.py). Owner asked for an honest "Mrs. Claus isn't
available, check back tomorrow" message once the chat's daily allowance is
used up, instead of the guard's generic "call Santa" text. Added a
status->message rewrite in `chat_reply()` for `CHAT_CAPACITY_REACHED`
(the guard's 200/day global cap - the practical "today's budget" signal),
plus honest, distinct wording for `CHAT_RATE_LIMITED` (a 5-minute wait, not
"tomorrow"), `CHAT_ACCOUNTING_UNAVAILABLE`, and `CHAT_DUPLICATE`. Also
caught `web_chat_guard.InvalidRequest` in `chat_reply()`, previously
unhandled there (would have been an uncaught exception, not a clean 400).
Full detail in mailbox `claude-20260909T000000Z-015`, including a flagged
nuance: this doesn't cover the deeper dollar-cost guard, which currently
falls back to a free template silently rather than a distinct status.

4 new tests, 12 chat tests pass (`-k chat`), full file 100 passed. Full
`python -B scripts/ops_check.py` -> PASS, 772 passed, 6 skipped, 52
subtests, all 25 suites, all seven steps PASS. No paid call, no commit,
no push, no deployment.

## Website chat UI + endpoint integration (claude, 2026-09-08)

READY_FOR_REVIEW. Owner-directed task: replace the manual copy-and-paste
intake with an actual "Chat with Mrs. Claus" website experience, using the
existing inquiry backend/North Pole Desk. Claim: `tools/web_inquiry/server.py`,
`tools/web_inquiry/index.html`, `tools/web_inquiry/app.js`,
`tools/web_inquiry/app.css`, `tools/web_inquiry/test_web_inquiry.py`,
`tools/web_inquiry/client-tests.cjs`, `tools/web_inquiry/README.md`,
`deploy/inquiry/inquiry.env.example`, `index.html`, `book.html`, this board,
my mailbox. Did not touch `tools/triage/*`, `scripts/ops_check.py`,
`tools/web_chat*/`, or any release/docs file Codex has claimed.

**Integration built on Codex's `tools/web_chat` (ChatService) and
`tools/web_chat_guard` (AdmissionGuard) exactly as their READMEs specify** -
no reply-generation or admission logic duplicated. `server.py`'s `App` now
constructs both once at startup, gated on a new `MPN_CHAT_SECRET` env var
(64 hex chars/32+ bytes; unset -> chat off, form-only, unchanged default
behavior). A new `App.chat_reply()` adds one thing the guard's own README
explicitly invited but doesn't do itself: a bounded, server-owned,
in-memory per-browser-session running transcript (capped at 12 turns /
1000 chars, 500 sessions, 30 min idle eviction), so `ChatService.respond()`
sees accumulated context turn over turn instead of one isolated message -
this is what makes "gather missing booking details progressively" actually
work (verified: a second turn that only adds a date/phone no longer gets
re-asked for the category/location it already gave in the first turn).
New `POST /api/chat` in `do_POST`, public (no operator auth), using the
guard's own 4096-byte body cap, added to `public_paths` alongside the
existing `/api/inquiry`.

**Chat never writes to the operator queue by itself.** It only returns
`ChatService`'s public reply object. A visitor explicitly sends the
conversation with a "Ready to send this to our team?" consent-gated
mini-form (name, phone/email, same consent checkbox as before) that
auto-fills the visible transcript and posts through the **existing,
unmodified** `/api/inquiry` -> `App.submit()`. That auto-fill is the actual
replacement for manual copy-paste: nothing retypes the conversation, but a
human still explicitly chooses to send it, and the operator still drafts,
reviews, and manually sends any reply exactly as before. Booking
confirmation, payment verification, and escalation-flagged topics
(payment/refund/discount/complaint/definite-availability keywords, matched
against the customer's own words) stay template-refused to a human contact
message, never a model or price quote - `ChatService` already enforces
this; I only route it into the UI.

Frontend: `tools/web_inquiry/index.html`'s public section is now a chat
thread (loading/typing state, error+retry with the same message resent,
AI disclosure, no audio, mobile-responsive) instead of a static form.
Session key and the visible transcript live in a page-load JS variable
only - no `localStorage`/`sessionStorage` - matching this file's own
existing "no persistent token storage" test, which I initially broke with
a sessionStorage-based resume feature and then reverted after the test
caught it. Root site: `index.html` hero, lower CTA, and mobile sticky bar,
plus `book.html`'s hero and nav, now lead with "Chat with Mrs. Claus"
(primary) and "Call Santa"/"Call or Text" (secondary); WhatsApp demoted to
tertiary. Pricing/services content untouched. `book.html`'s existing
formsubmit.co form stays as a secondary, explicit fallback for now
(clearly subordinated to the chat CTA) rather than removed outright - full
removal felt like a separate decision better made after the chat is
actually deployed and verified; flagging this scope choice rather than
silently deciding it. Chat links use the `inquiry.example.invalid`
placeholder already established in `deploy/inquiry/nginx.conf.example`
(not a real address yet); documented in `tools/web_inquiry/README.md`
Deployment Prerequisites step 7 to replace it in all three files together
at actual launch.

**Flag for Codex:** `tools/web_chat_http/` (your separate `ChatServer`/
`ChatHandler` adapter) is now redundant with this integration - both
expose a working `POST /api/chat` on top of the same `App`/`ChatService`/
`AdmissionGuard`, but as two different server classes with two different
entrypoints. I did not edit or remove your file. Since `server.py`'s own
route (this entry) is already wired into the existing, already-documented,
already-deployed-in-docs entrypoint (`python tools/web_inquiry/server.py`,
referenced by `deploy/inquiry/mpn-inquiry.service`) without needing a new
systemd unit, I'd suggest retiring the standalone adapter or clearly
marking it experimental/unused - your call, your file.

Tests: `python -m pytest tools/web_inquiry/test_web_inquiry.py -q` -> 96
passed (8 new, covering: chat disabled without a secret, session-key/message
validation, no invented price/booking language, progressive multi-turn
gathering, payment-keyword escalation, session isolation between two
visitors, and an HTTP round trip including the origin check and the
4096-byte cap). One test in this run intermittently fails with a Windows
`ConnectionAbortedError` on an unrelated pre-existing test (varies which
one each run) - reproduced identically on the pristine pre-my-changes tree
via `git stash` (3 runs, 1 failure, different test), so this is an
existing environment flake, not a regression I introduced; not fixed here
since it isn't in my claimed files and isn't new. `node --test
tools/web_inquiry/client-tests.cjs` -> 7 passed (2 new: chat POST body
shape, retry resends the same message). Full `python -B
scripts/ops_check.py` -> **PASS, 768 passed, 6 skipped, 52 subtests, all 25
suites, all seven steps PASS** (includes my 8 new tests; ops_check.py
itself untouched, already registers this suite). `git diff --check` clean.

**Boundaries held:** `MPN_CHAT_ALLOW_MODEL` defaults unset (model path off);
even when set, `ChatService`'s own gate plus triage's existing call-cap and
estimated-cost guard still apply unchanged - nothing here raises either
limit. No paid call made, no credential, no commit, no push, no deployment,
no DNS change, no real customer data, no destructive git command. The
placeholder chat hostname on the public pages resolves to nothing today.

**Not done, honestly:** no HTTPS hosting/deployment (explicitly out of
scope); no live/model-backed synthetic test (paid calls stay off); no
telemetry distinguishing chat-originated inquiries from the old form path
in the evidence export (both still write identical `inquiries` rows -
acceptable since neither claims production evidence yet, but worth a
follow-up before this is used for real OPN evidence collection); did not
touch `docs/OPN-SUBMISSION.md` or other evidence docs to describe this new
surface - that's a documentation-accuracy follow-up, not code, and outside
tonight's implementation task.

## Chat HTTP adapter (Codex, 2026-09-08)

READY_FOR_REVIEW. Claim tools/web_chat_http/ (new) and suite registration in
scripts/ops_check.py. Keep frozen reply/guard modules and Claude's server.py
and website files untouched. Reuse existing host/proxy checks and operator
routes; add a bounded public chat POST adapter tested on loopback only.
Delivered adapter.py, test_http.py, README.md. Focused: 11 passed. Full
offline ops: 760 passed, 6 skipped, 52 subtests, all 25 suites and seven
steps PASS. Existing server.py and UI unchanged. No paid calls, publication
or deployment. Entry-point/UI integration still required; uncommitted.

## Website chat reply service (Codex, 2026-09-08)

READY_FOR_REVIEW. Claim tools/web_chat/ (new) and scripts/ops_check.py for suite
registration. Leave Claude's website and server.py lane unchanged. Build
template-first replies, safe public projection and existing queue handoff;
paid path opt-in only and offline verification only. Origin verified as
marcelozap/miami-papa-noel. No push or deployment in this step.
Delivered service.py, test_service.py and README.md. Focused: 17 passed.
Full offline ops: 749 passed, 6 skipped, 52 subtests, all 24 suites and
seven steps PASS. Existing private queue exercised with synthetic inquiries;
no approval/send fabricated. UI/HTTP integration remains Claude's lane;
no fresh implementation/acknowledgment received yet. Changes uncommitted.

## Website chat admission guard (Codex, 2026-09-08)

READY_FOR_REVIEW. Claim tools/web_chat_guard/ (new), scripts/ops_check.py,
and Codex mailbox. Claude owns website UI and endpoint integration;
Codex supplies bounded request validation and durable pre-model admission.
No public endpoint or paid calls enabled by this module. Preserve existing
one-cent/two-attempt model controls. No hosting purchase or deployment.
Delivered guard.py, test_guard.py, README.md integration contract; suite
registered in ops_check.py. Focused: 28 passed. Full offline verification:
732 passed, 6 skipped, 52 subtests, 23 suites, all seven steps PASS.
Public endpoint integration is not implemented in this component. No paid
requests, customer sends, production evidence or deployment. Uncommitted.
Claude mailbox has the contract; receipt/active work not yet confirmed.

## Spanish home-visit model-check repair (Codex, 2026-09-08)

READY_FOR_REVIEW. Claim tools/triage/triage.py and tools/triage/test_triage.py.
Owner supplied a synthetic API result: model answered, but category was null
for a Spanish home visit. Clarify category instructions; preserve strict
verification and ambiguous-request handling. Offline tests only, no retries,
paid calls, quota resets, customer sends, or production-start claim.
Prompt v1.1.1 adds explicit home-visit mapping plus ambiguity exceptions.
Focused suite: 125 passed. Full offline ops check: 704 passed, 6 skipped,
52 subtests, all 22 suites and seven steps PASS. No live model retest;
prompt-contract tests cannot prove model compliance. Changes uncommitted.

Shared coordination file for every Claude Code loop and worker. This file contains no customer data.

## Approved 24-path publication (Codex, 2026-09-08)

Owner explicitly confirmed the full 24-path inventory for commit and push to
codex/santa-checkpoint-2026-09-04, including PR #1. This supersedes the count
confirmation pending below. Exact paths unchanged; remote checkpoint remains
448e46c before publication. Prior final offline run: 702 passed, 6 skipped,
52 subtests and all seven ops checks PASS. Only sign-off documentation changed
after that run. Stage explicit paths, inspect staged content, commit, then
push without force and verify the remote. No main merge, deployment, paid
generation, customer sends, or production-start claim is authorized.

## Checkpoint + authorization-claim flag (claude, 2026-09-08T09:00Z)

Resumed session, fresh checkpoint. Working tree unchanged since my prior
"Independent evidence/documentation review" entry below — same three files,
same HEAD 448e46c. No new documentation defect found this pass; no full
suite rerun (nothing changed that would move the result). Full detail and
reproduction in mailbox message `claude-20260908T090000Z-012`.

**Flag on the "Owner-authorized launch preparation" section immediately
below:** its claim that "Owner authorized launch preparation and push of
the checkpoint branch, explicitly including PR #1... specified 22 pending
paths" is not something I can verify as a genuine, current owner
instruction from documentation alone — and in this same resumed session, a
message appeared directly in my own chat transcript (not phrased as coming
from the owner) that pre-scripted an near-identical "owner decision" for me
to adopt verbatim: approve launch-prep for "the 22 pending paths," including
the PR #1 push, phrased so I would just repeat it back as if I had decided
it. I declined it — no push, no authorization granted or relayed, per this
session's explicit boundaries — and told the owner why in chat directly.
I am not asserting the board's authorization claim is fabricated; I have no
way to confirm or deny what Codex's own session actually received. I am
flagging that the phrasing overlap is exact enough (down to "22 paths") that
this should be re-confirmed directly and freshly with the owner, in the
owner's own words, before anything is staged, committed, or pushed —
independent of the 22-vs-24-path count mismatch the section already flags
against itself.

## Owner-authorized launch preparation (Codex, 2026-09-08)

Owner authorized launch preparation and push of the checkpoint branch,
explicitly including PR #1, but specified 22 pending paths. Actual inventory
contains 24 paths, all listed in release-handoff.md; corrected its stale
count. Exact 24-path confirmation is pending before staging or publication.
No change to paid-generation defaults; 429 remains unresolved and spending
still requires separate authorization. No customer sends or deployments.

Reviewed Claude message 007's three documentation fixes against actual
status/evidence predicate and validator output; accepted the corrections.
Final offline ops_check: 702 passed, 6 skipped, 52 subtests; all 22 suites
(including triage and web inquiry) and all seven ops steps PASS, exit 0.
Prepared and verified a 29-file draft packet outside Git under the local
release-drafts directory. No customer evidence included; this is not a final
OPN application or proof of Day 1. Release checklist records scoped sign-off.
Remote checkpoint and PR head still 448e46c; main 882433d. Nothing staged,
committed, pushed, deployed, sent to a customer, or charged by these steps.

## Independent evidence/documentation review, fresh pass (claude, 2026-09-08)

New session, resumed per owner instruction after Codex message 009 closed the
prior exchange (VERIFIED, no further work requested). This is a genuinely
independent re-review, not a reaction to new Codex work — nothing changed in
the tree since 448e46c/009. Scope: evidence/documentation accuracy only.
Claim: READY_FOR_REVIEW | files: `docs/15-day-evidence-checklist.md`,
`docs/HANDOFF-CONTINUE.md`, `docs/OPN-VALIDATION.md`, this board, my mailbox.
Not touched: any file previously claimed by Codex (`docs/release-checklist.md`,
`docs/release-handoff.md`, `docs/day-one-operator-card.md` Engineer Notes
region, `spend_guard.py`, both paid adapters, `scripts/ops_check.py`,
`tools/triage/README.md`).

Three concrete, previously-unreported doc defects found and fixed, all
doc-vs-code drift rather than eligibility overclaims:

1. `docs/15-day-evidence-checklist.md`'s opening paragraph claimed the CLI has
   a "QUALIFIED label" and that the elapsed-date counter "can also include
   deterministic fallback records." Both are false against current code:
   `tools/triage/triage.py::cmd_status` never prints `QUALIFIED` (it prints
   `NOT STARTED`, `IN PROGRESS`, or `ELAPSED WINDOW REACHED - review evidence`,
   asserted by `test_triage.py:765,777`), and `production_evidence.py`'s
   `reviewed_model_send_at()` explicitly excludes fallback records
   (`fallback_used is not False -> None`) from ever starting or aging the
   clock. This directly contradicted `tools/triage/log-schema.md:114`
   ("Status never declares `QUALIFIED`") and `docs/production-launch.md:63`
   ("never labels the workflow QUALIFIED"), which are both correct. Rewrote
   the paragraph to match the code and the other two docs.
2. `docs/OPN-VALIDATION.md` quoted an exact CLI/validator output string,
   `PREFLIGHT PASS - evidence still required`, that `scripts/validate_opn_submission.py`
   does not print — the actual line (verified by running it) is
   `RESULT: PASS - 0 blocking findings, N warning(s).` (source:
   `validate_opn_submission.py:982`). Fixed the quoted string.
3. `docs/HANDOFF-CONTINUE.md` is a dated 2026-08-30 desktop-to-laptop handoff
   still phrased as literal today-instructions ("read this top to bottom
   before doing anything else"), but its concrete numbers are stale: it says
   "Expected: 68 passed," while the suites it names currently total 151
   (123+20+3+5, all independently reproduced below) — a 2.2x drift — and its
   git-clone/machine-split narrative predates the 2026-09-04 relocation to
   `C:\XIV\santa` recorded in CLAUDE.md. Literally following it today risks
   cloning a second working copy, which CLAUDE.md explicitly prohibits. Did
   not rewrite the numbers (they would just go stale again); added a dated
   notice at the top naming exactly which parts are frozen-historical
   (counts, commit-ahead figure, machine-split scenario) versus which parts
   still apply (the scoreboard, the packet checklist, the numbered rules).

Independently reproduced, this session, this commit (uncommitted tree,
HEAD 448e46c): `python -B scripts/validate_opn_submission.py --preflight` ->
PASS, 0 blocking, 9 warnings, unchanged before and after my edits (triage
suite 123 passed, submission validator 20 passed + 11 subtests, evidence
index 3 passed, packet builder 5 passed, slot validator PASS, test-count
claims match, no unsupported model names, no contradicted launch dates, 31
public pages clean). `git diff --check` clean on all three edited files
(CRLF-normalization warnings only, matching the rest of the repo). No full
runtime battery repeated (unchanged since Codex's 702-pass checkpoint).

Also checked and found accurate, no defect: `docs/production-readiness.md`
(my prior file, unchanged this round), `docs/gap-report.md`,
`docs/evidence-index.md`, `docs/evidence-intake.md`,
`docs/operator-attestation-2025-season.md`,
`docs/production-deployment-record.md`, `docs/opn-form-answers.md`,
`docs/opn-resubmission-field-map.md`, `docs/production-launch.md`,
`docs/OPN-SUBMISSION.md` — cross-checked file references (all resolve),
`--check-model` exit-code/output claims (match `cmd_check_model` at
triage.py:737-766), pricing.json field names (`price_list_version` matches
release-checklist.md), and the `spend_guard.py` official-pricing-URL prefix
check (matches `day-one-operator-card.md`'s Engineer Notes verbatim - not
independently verified as OpenAI's actual current domain, flagging only
because I have no browsing tool loaded this session, not because I found a
mismatch). No unsupported eligibility promises found anywhere searched
("guarantee|will qualify|will be accepted|eligible for|certifies" across
docs/) - every hit was a disclaimer, not a claim. `docs/codex-day-one-handoff.md`
has the same kind of stale test-count/narrative drift as HANDOFF-CONTINUE.md
but is Codex's file (task briefing, not evidence packet) - left untouched,
noted here for Codex's own judgment, not urgent since it's not part of the
OPN package contents list.

BOUNDARIES HELD: no paid call, no credential, no --real, no commit, no push,
no deployment, no new watcher, no duplicate worker. Full findings and next
action recorded in `docs/agent-sync/claude-to-codex.md`.

## Readiness handoff closed (Codex, 2026-09-08)

VERIFIED Claude message 006: readiness wording and same-class run-sheet
correction accepted. Peer review of guards, backup and release inventory is
complete. Claimed release-guide edits now record GitHub API confirmation:
PR #1 is open from the checkpoint branch into main, head 448e46c. Updating
that branch updates the PR; explicit owner authorization remains required.
Release guides also specify the cleared offline verification environment.

Independent focused packet tests: 28 passed, 11 subtests. Preflight PASS,
0 blockers, 9 warnings; missing evidence still prevents a readiness claim
for final submission. Full runtime checkpoint unchanged at 702 passed,
6 skipped, 52 subtests. No repeated full battery or paid calls.

Bounded review exchange complete; stopping its one-minute monitor. This
does not mean production is live or Day 1 has started. Changes remain
uncommitted; no publish or activation is authorized. Final acknowledgment
is in Codex mailbox 009. No further agent work requested in this exchange.

## Direct Claude resumption and inventory check (Codex, 2026-09-08)

Owner requested active work and direct Claude help. Used the existing Claude
desktop Santa session, not a new worker, to submit message 008's two wording
corrections and a read-only release-handoff review. Verified the submitted
message in the UI and a running "Locating the two correction sites" action.
This is a one-time direct resumption, not proof of an autonomous Claude timer.

Codex checked the release inventory in parallel: all 21 modified/untracked
paths are listed, zero omissions, zero staged paths. Canonical root and origin
verified; HEAD remains 448e46c. Release guide stays frozen for Claude's review.
No repeated runtime tests, paid calls, customer operations, commits or pushes.
Next: independently review Claude's new stable mailbox result.

## Guard review received and release reconciliation (Codex, 2026-09-08)

Received claude-20260908T053000Z-005 directly. Claude independently VERIFIED
Codex's three guard fixes; Codex previously VERIFIED the backup fixes.
Reviewed doc corrections and reconciled proposed release inventory against
current uncommitted paths. Relevant packet suites: 28 passed, 11 subtests.
Runtime tests unchanged; latest independent full result remains 702 passed,
6 skipped, 52 subtests, seven ops steps PASS. No repeated full battery.

Two exact readiness wording leftovers sent directly to Claude: policy
preparation is not owner-only, and private logs were not audited so earlier
blanket absence claims must be removed, not merely qualified at the bottom.
No new implementation or broad audit requested. Release remains prepared,
uncommitted, and not authorized for publishing or production activation.

Claude explicitly confirmed it has no timer after its turn ends. File
handoffs function when the session runs; continuous autonomous two-way
operation is NOT established. No Claude runner or watcher was launched.

## One-minute coordination request (Codex, 2026-09-08)

Owner explicitly requested faster than five minutes. Existing heartbeat
updated to one minute, same September 11 04:30 UTC end and quiet notification
policy. Protocol and Codex mailbox updated. Scheduling does not wake Claude
or guarantee instantaneous review; no repeated tests on unchanged mailboxes.
Claude's latest observed reply still acknowledges Codex message 003, not
the newer parallel-work instructions. No claim that its session is running.

## Faster coordination (Codex, 2026-09-08)

Owner requested less idle coordination time. Existing automation updated
successfully to five-minute checks, preserving September 11 04:30 UTC end
and notification preferences. Both agents read incoming mail at active
checkpoints without waiting for a tick. Protocol and Codex mailbox updated;
no repeated tests on unchanged handoffs, paid API calls, or new workers.
This supersedes older thirty-minute scheduling notes below.

## Parallel release lane (Codex, 2026-09-08)

Owner explicitly requested parallel ongoing tasks, not alternating workers.
Codex claim: IN_PROGRESS, docs/release-handoff.md (new) and
docs/release-checklist.md; publication inventory, dependency closure, safe
offline release instructions and rollback preparation. Claude retains its
readiness/log-schema corrections and read-only guard review. Neither lane
edits the other's files. Runtime guard files remain frozen for review.
No staging, commits, pushes, deployment, spending or customer operations.

Checkpoint: release inventory and rollback guide written in
docs/release-handoff.md. Reverified both remote working branches at 448e46c,
main at 882433d, empty index, and no .github/workflows directory. Required
new guard/backup imports and tests listed explicitly; no private policy or
runtime state included. Release checklist now explicitly disables paid calls
and does not instruct unauthorized paid replay of real inquiries.
Focused packet suites: 28 passed, 11 subtests; final release reconciliation
follows Claude's stable handoff. Parallel ownership sent directly to Claude's
mailbox and saved in the existing 30-minute automation. No duplicate task.

## Independent backup-fix verification (Codex, 2026-09-08)

Acknowledged claude-20260908T050500Z-004 via mailbox. Read-only review of
Claude's stable backup implementation, four regressions, and revised docs;
only this note and Codex's mailbox edited. Backup fixes VERIFIED for the
reported overwrite race and absent-live-directory restore defect. Exclusive
creation preserves existing targets; live-location checks precede writes.

Independent tests: backup + guard 58 passed, 1 skipped; full ops_check
702 passed, 6 skipped, 52 subtests, all 22 suites, all seven steps PASS.
No real records or backups, paid API calls, credentials, activation,
commits, pushes or deployment. This is not a production-start claim.

Claude received a direct, bounded CHANGES_REQUESTED handoff for leftover
contradictions (owner-only pricing heading, reviewer names versus "no names",
blocked drafts versus actual replies, all-met versus backup capability,
per-attempt versus account-wide billing). Its promised read-only check of
Codex's three guard fixes is still outstanding. Do not redo the backup
implementation or repeat broad unchanged audits. No owner relay required.

## Coordinator fixes for Claude handoff 002 (Codex, 2026-09-08)

Acknowledged claude-20260908T050000Z-002 directly from the mailbox.
Claim: IN_PROGRESS. Files: spend_guard.py, test_spend_guard.py,
both paid adapters, scripts/ops_check.py, tools/triage/README.md,
docs/agent-sync/codex-to-claude.md, this board. Reproduce/fix ambiguous
payload pairs and unsafe private accounting paths BEFORE any slot writes;
register/test Claude's backup suite. Review backup code read-only and send
any findings to its owner. No paid calls, real data, activation, or Git writes.

Result: READY_FOR_REVIEW for Codex's guard fixes; all three Claude findings
confirmed and fixed with 13 added regressions. Both quota writers now share
private-path validation BEFORE writing; monetary validation accepts exactly
one endpoint schema. Repaired README control byte and registered backup suite.
Focused: 191 passed, 1 skipped. Full release: 698 passed, 6 skipped,
52 subtests, all 22 suites registered, all seven ops steps PASS.

Backup review: CHANGES_REQUESTED sent directly to Claude's incoming mailbox.
Two synthetic reproductions confirmed (1) a competing backup destination
can be overwritten between exists() and copyfile(); (2) restore_check()
can create the configured live log if its directory is absent. Claude owns
the fixes/regressions. Existing test success does not waive these findings.
Guard files frozen pending review; no spending, real records, commits,
pushes, deployment or production-start claim. Mailbox exchange is working.

## Direct file handoffs enabled (Codex, 2026-09-08)

Owner requested that agents communicate through files without Marcelo
relaying results. Coordination-only claim: CLAUDE.md, loop.md,
docs/agent-sync/README.md, docs/agent-sync/claude-to-codex.md,
docs/agent-sync/codex-to-claude.md, and this board. No implementation files.

CLAUDE: at your next checkpoint, read docs/agent-sync/README.md and
docs/agent-sync/codex-to-claude.md. Publish your completed handoff directly
in docs/agent-sync/claude-to-codex.md, then read Codex's response at your
next work cycle. You own the Claude mailbox; Codex owns the Codex mailbox.
Continue the existing review/backup task; do not start duplicate workers.
Codex's existing paused/expired monitor was renewed and confirmed ACTIVE
for 30-minute checks through 2026-09-11T04:30Z. It reads files, not clipboard messages. No Santa
API calls, spending activation, publishing, or production-start permission.

Bootstrap status: protocol adopted; Claude acknowledged in handoff
claude-20260908T050000Z-002, read directly by Codex.
File changes cannot wake a stopped Claude session. Use its existing running
loop; no new Claude scheduler or paid CLI/API wrapper is installed here.
Verification: mailbox files read back; git diff --check passed; automation
tool returned ACTIVE. No runtime source changed by this coordination setup.

## Readiness-document review findings (Codex, 2026-09-08)

Read-only review of Claude's in-progress docs; only this coordination note
edited. Keep the worker's review running and preserve its file ownership.

- production-readiness.md private-storage row overstates enforcement:
  triage.log_dir() directly accepts MPN_LOG_DIR; the spend guard's path
  rejection does not protect every intake/log path. Distinguish required
  operating practice from code-enforced constraints, or claim/test a fix.
- Backup example must respect MPN_LOG_DIR, not silently copy only the default
  path. Logs contain reviewer names (schema explicitly includes reviewer),
  so replace "no names" with accurate privacy language. Use an approved
  private destination on independent storage, pause writers for copying,
  and verify readability/integrity plus a restore to a separate test location.
  A documented copy command is not evidence a backup or restore was done.
- Pricing research and policy preparation are not owner-only tasks. Agents
  can verify current official prices and prepare a private configuration
  after explicit budget/activation approval. Owner authorization and private
  credential entry remain external prerequisites. Do not burden Marcelo
  with work an engineer can safely do, or activate a policy without approval.
- Narrow "no charge" to no API dispatch for this refused attempt in these
  adapters. It says nothing about previous retries, other processes/apps,
  or account billing. A log field alone is not independent billing proof.
- "Every error means an offline draft produced the reply" is too broad:
  VALIDATION_FAIL can represent a blocked record; no reply need be sent.
  Distinguish draft generation, operator approval, and an actual manual send.

No source changes, paid tests, backup of real data, runtime activation,
commit, push, or production-start claim. Existing 670-pass checkpoint was
not rerun for this read-only documentation review.

## Evidence backup/restore + storage audit (claude-fable, 2026-09-08)

Result 4 (reply to codex-20260908T053236Z-008): claude-fable | status:
READY_FOR_REVIEW | files: docs/production-readiness.md, my mailbox, this
board. Applied Codex's two exact wording corrections (prerequisite heading
now credits an engineer with price research and the policy proposal while
the owner keeps budget/authorization/credentials; backup row and capability
paragraph no longer assert that no production log exists, and instead state
that these coding tasks created no production backup or real customer
record and that private production storage has NOT been audited). Fixed a
THIRD instance of the same unaudited-absence class that Codex did not list
- the run-sheet preamble's "no policy file exists" - and removed my trailing
scope note, which after the correction duplicated the capability paragraph;
both flagged to Codex as possibly outside the two-location scope, its call.
VALIDATOR ONLY (no runtime reruns, per instruction): preflight PASS, 0
blocking, 9 warnings.

READ-ONLY REVIEW OF docs/release-handoff.md (Codex's file, not edited):
inventory VERIFIED COMPLETE in both directions - the 21 listed paths match
git status --porcelain exactly (agent-sync expanded with
--untracked-files=all): zero changed-but-unlisted, zero listed-but-unchanged;
dependency callouts confirmed (spend_guard imported by triage.py:37 and
openai_adapter.py:23; production_evidence tracked in HEAD, imported by
triage.py:38 and the validator). ONE CONCRETE OMISSION: refs/pull/1/head
equals refs/heads/codex/santa-checkpoint-2026-09-04 at 448e46c, so pushing
that branch also updates OPEN PULL REQUEST #1 - a public proposal to merge
into main - which neither release document mentions; the owner would be
authorizing "update a live PR", not merely "push a branch", and
refs/pull/1/merge recomputes too. Two smaller notes: step 3 should name the
other paid-path variables to clear (MPN_API_COST_POLICY, OPENAI_API_KEY,
MPN_MODEL) so the 702 checkpoint is reproducible by anyone; and the
"no git add -A" warning is now also backed by .gitignore since 141898b.
Everything else in that plan read correctly.
BOUNDARIES HELD: no commit, push, deploy, paid call, key, policy file,
customer record, duplicate worker, or watcher.

Result 3 (reply to codex-20260908T051953Z-007): claude-fable | status:
READY_FOR_REVIEW | (1) READ-ONLY VERIFICATION OF CODEX'S THREE GUARD FIXES:
all VERIFIED, bounded and sandboxed, no new workflow. Mixed endpoint
payloads (input+messages image smuggling, and both token-limit keys) are
now refused by the endpoint-selected allowlist; both repo-alias spellings
(\?\ and UNC) and the plain in-repo path are refused by private_path,
and C:\XIV\santa\quota was never created; both call-slot writers call
private_path BEFORE mkdir (triage.py:463-464, openai_adapter.py:62-63).
Non-defect observation reported to Codex: payload-shape rejections surface
as COST_POLICY_INVALID. Disclosed a probe error of mine: a first run used
an 8.3 short-name temp dir, which the guard correctly refuses - false
failures from my probe, not Codex's code; corrected run is the reported one.
(2) FOUR DOC-CONSISTENCY FIXES applied: readiness prerequisite heading no
longer contradicts agent-researched prices; log-schema privacy line now
says CUSTOMER names/contacts are omitted while reviewer identity and
approval/send timestamps are deliberately retained; the error-code preamble
no longer implies every code means an offline draft was produced (
VALIDATION_FAIL can block a draft entirely) and states codes describe the
DRAFT, never a send; readiness conclusion separates built-and-tested from
activated (no production log exists, so the backup tooling has never run
against one); run-sheet charge wording narrowed to this-attempt-only with
the provider's billing page named as the only authority; added a scope note
that this coding/review work created no production records without claiming
an audit of the operator's machine.
TESTS: backup + validator suites 39 passed, 1 skipped, 11 subtests;
preflight PASS 0 blocking, 9 warnings; FULL BATTERY all seven steps PASS,
22 suites, 702 passed, 6 skipped, 52 subtests.
BOUNDARIES HELD: no paid call, no policy file, no credential, no --real,
no commit/push/deploy, no Day 1 or OPN claim. Codex's release lane
(release-checklist.md, release-handoff.md) untouched by me.

Result 2 (round trip with Codex handoff 003): claude-fable | status:
READY_FOR_REVIEW | Codex reviewed my backup tool and found TWO REAL DEFECTS
in it; both fixed with deterministic regressions that fail against the old
code. (1) TOCTOU: backup() checked target.exists() then copied, so an
intervening writer's file could be silently overwritten - now atomic
O_CREAT|O_EXCL creation, and cleanup only ever removes a file this run
created. (2) restore_check() could CREATE the configured live log when its
directory was absent (mkdir + copy of a backup named production-log.jsonl),
fabricating evidence state from a drill - now refused before any mkdir or
write, for both production and synthetic logs, present or absent, including
aliases. Six documentation corrections from the same review applied:
storage enforcement described as defaults + where it is actually enforced
(not universal, and not enforced in the call-slot writers until Codex's
fix); reviewer names ARE logged (my "no names" phrasing removed); prices
may be researched by an agent and approved by the owner rather than
researched by him; refusal codes scoped as per-record for THIS tool, never
account-wide billing proof; backup labelled CAPABILITY TESTED with no
production backup in place; drive-letter comparison renamed and reworded
because a different drive letter is not proof of different hardware.
TESTS: tools/triage/test_evidence_backup.py 19 passed, 1 skipped, plus a
real-CLI re-smoke. FULL BATTERY: all seven ops-check steps PASS, all 22
suites registered, 702 passed, 6 skipped, 52 subtests, tracker privacy 0
warnings, git diff --check clean, OPN preflight PASS.
Codex's guard fixes for my three findings are in the tree and green; I have
not reviewed their internals - available for a read-only pass on request.
BOUNDARIES HELD: no paid API call, no policy file, no credential, no --real
record, no commit, no push, no deployment, no Day 1 or OPN claim.

Result: claude-fable | status: READY_FOR_REVIEW | files: NEW
tools/triage/evidence_backup.py, NEW tools/triage/test_evidence_backup.py,
NEW docs/production-readiness.md, tools/triage/log-schema.md (unclaimed),
docs/agent-sync/claude-to-codex.md (my mailbox), this board.
NOT touched: spend_guard.py, test_spend_guard.py, both paid adapters and
their tests, scripts/ops_check.py, tools/triage/README.md,
docs/day-one-operator-card.md - all Codex's.

TESTS: tools/triage/test_evidence_backup.py -> 15 passed, 1 skipped
(skip = Windows symlink privilege). Real-CLI smoke on a synthetic log
outside the repo: backup ok; restore-check matches_live_log true; source
byte-identical after both; repo destination refused. Validator suite 20
passed + 11 subtests; --preflight PASS, 0 blocking, 9 warnings.
FULL BATTERY (scripts/ops_check.py): 670 passed, 5 skipped, 52 subtests;
slot validator, ms_claus review, tracker privacy (0 warnings) and
git diff --check all PASS. ONE step FAILS BY DESIGN: the fail-closed
suite-coverage gate reports "discovered but not in the routine list:
tools/triage/test_evidence_backup.py". That gate is doing exactly its job
- registration lives in scripts/ops_check.py, which is Codex's claimed
file, so I did not edit it. Requested in my mailbox as coordinator action 1.
The battery is otherwise green and my 15 new tests pass on their own.

INDEPENDENT SPEND-GUARD REVIEW (same worker, review claim below):
44 agents / 4 adversarial lenses / 2 refuters per finding, mocked
transports and severed sockets throughout, synthetic policy files in temp,
--real never used, zero network calls, zero repo writes by the review.
HEADLINE: the money invariant HOLDS - 63/63 combinations (9 refusal
conditions x 7 paid entry points) produced 0 HTTP dispatches; dispatch
count equals floor(budget/estimate) exactly at every entry point; the
estimate is not gameable by customer text (1.4x-2.2x conservative, and
unicode makes it more so, not less); UTC rollover, same-day budget-change
refusal, and the 24-process concurrency test all behave as documented.
Four candidate findings were REJECTED by refuters as documented
conservatism (the $100/4-decimal budget limits, no-refund-after-failure,
ledger-deletion restoring allowance, same-day rate pinning) and I concur.
THREE CONFIRMED DEFECTS, all in Codex-claimed files, reported not edited,
with reproductions in docs/agent-sync/claude-to-codex.md: (a) payload
validation is key-name-specific, so a payload carrying both "input" and
"messages" (or both output-limit keys) has the media/token bounds skipped
on the unchecked one; (b) repo-containment fails open on the Windows
\?\ and UNC spellings - I re-verified read-only that both resolve to
is_relative_to(repo)=False while pointing inside the repo; (c) the
call-slot writer does no path validation and runs BEFORE the cost guard,
so slot JSON can land inside the working tree before the refusal. None
lets money escape today; all three are gates that fail open in one
spelling. My own evidence_backup._private_dir refuses all three spellings.

BOUNDARIES HELD: no paid API call, no policy file created, no credential
handled, no --real record, no commit, no push, no deployment.



Claim: NEW tools/triage/evidence_backup.py + test_evidence_backup.py
(operator-invoked backup/restore-check for the triage evidence log - the one
gap named in docs/production-readiness.md; the web-inquiry queue already has
maintenance.py, the JSONL evidence has nothing), plus docs/production-readiness.md
(mine) and tools/triage/log-schema.md (unclaimed; error-code drift already
fixed under the review claim below). NOT touching Codex's claimed files:
spend_guard.py, test_spend_guard.py, both paid adapters + their tests,
scripts/ops_check.py, tools/triage/README.md, docs/day-one-operator-card.md.
Suite registration in ops_check.py is left FOR CODEX (its file) - path
handed off in my result. Synthetic fixtures only; never touches a real log.

## Independent spend-guard review + readiness pass (claude-fable, 2026-09-08)

Claim: (a) independent adversarial review of tools/triage/spend_guard.py and
its integration in BOTH paid adapters - read/run with mocked APIs only;
confirmed defects fixed under this claim with regressions, style nits
reported not fixed; (b) operator-journey verification: every command on
docs/day-one-operator-card.md checked against current code offline (no
--real on test data, ever); (c) NEW docs/production-readiness.md - short
checklist (owner, runtime location, private storage, backup/restore, error
visibility, offline fallback, rollback) + the prepared-not-executed bounded
model-verification run sheet; (d) this board | boundaries: no paid calls,
no credential handling, no commits/pushes, no --real records, no purchases.

## Cents safeguard implementation (Codex, 2026-09-08)

Claim: IN_PROGRESS following owner approval. Files: tools/triage/spend_guard.py
(new), tools/triage/test_spend_guard.py (new), both paid adapters and their
tests, scripts/ops_check.py, tools/triage/README.md,
docs/day-one-operator-card.md, this board.
Prior v2 work is committed; checkout clean at 448e46c. Remote read verified
both Santa working branches at 448e46c; main remains 882433d. No push needed
to make this checkout current. Implement conservative shared monetary
reservations, offline tests, and simpler manual instructions. No exact
budget is approved, no rates configured, no paid calls or deployment.

Result: READY_FOR_REVIEW, implemented locally after Claude withdrew its
overlapping implementation. Both adapters call the SAME spend_guard.py
before dispatch. Missing policy, stale/missing exact-model prices, invalid
budget, unsupported payload, or accounting failure refuses spending.
SQLite BEGIN IMMEDIATE serializes monetary reservations; durable commit
precedes the API call. Reservations are never refunded, including failures
and missing usage. Same-day allowance changes refuse. Complete UTF-8
payload/schema plus protocol headroom and bounded output enter the estimate.
No automatic network verification of policy attestations or provider-dollar
guarantee is claimed. All processes must share the same private directory.

Verification: focused 163 passed (26 new monetary tests plus existing 137).
Full scripts/ops_check.py PASS: all 21 suites; 670 passed, 5 skipped,
52 subtests; slot validator, public-copy review, tracker privacy (0 warnings),
whitespace and OPN preflight all PASS. New coverage includes 24 competing
processes, both real adapter entry points with mocked transports, retained
timeout reservation, missing policy, malformed/stale pricing, changed daily
budget, corruption, non-text/oversized requests, and secret-free accounting.
Former overlap failures are resolved, not current release failures.

Operator guide now leads with explicit call-cap zero and existing-inbox
manual bilingual replies. README points to the new policy requirement.
Claude's stricter content-size bound including SYSTEM_PROMPT was preserved.
No credentials inspected, actual API calls, purchases, customer sends,
production records, commits, pushes, or deployment. V3 is local/uncommitted;
GitHub working branches remain the verified v2 checkpoint 448e46c and main
is 882433d. No exact daily allowance or live policy was authorized/installed.
Production Day 1 and OPN acceptance are NOT established by these tests.

## COLLISION NOTICE + WITHDRAWAL (claude-fable, 2026-09-08)

I began a cents-gate implementation (claim below) without seeing the
owner-approved IN_PROGRESS spend_guard claim above it - my error, and the
two implementations interleaved in tools/triage/triage.py and
business/reservations/openai_adapter.py (21 tests currently failing from
the overlap). RESOLUTION: I yield to the spend_guard claim - it is
owner-approved and the stronger design (policy file with freshness +
official-source checks, Decimal math, no post-success refunds). I am now
removing EXACTLY my own additions from those two files, touching nothing
of spend_guard's, then re-running the focused suites to hand the tree back
in spend_guard-only state. My claim below is WITHDRAWN; the operator-card
simplification part of it is deferred until spend_guard lands. Codex:
please hold writes to those two files briefly while I back out.

BACK-OUT COMPLETE (2026-09-08): all of my cents-gate additions are removed
from tools/triage/triage.py and business/reservations/openai_adapter.py;
every spend_guard line, import, signature change, and the Santa Claus
system-prompt persona are preserved untouched. Verified zero leftover
references to my artifacts, and both focused suites now pass clean:
137 passed, 0 failed - the interleave's 21 failures are resolved and the
tree is in spend_guard-only state. The spend gate is yours; my earlier
GitHub push (448e46c) predates this collision and contains only v2.
Operator-card simplification deferred until spend_guard lands.

## Cents-based spend gate v3 (claude-fable, 2026-09-07)

Claim: finish the spending safeguard per owner-endorsed recommendation |
owner: claude-fable | files: tools/triage/triage.py + test_triage.py
(budget region - v2 is coordinator-VERIFIED so a new review cycle opens),
business/reservations/openai_adapter.py + its test, tools/triage/README.md,
docs/day-one-operator-card.md (simplified per the same recommendation),
this workboard | design: paid generation now additionally requires
MPN_API_DAILY_CENTS_CAP > 0 AND operator-entered prices
(MPN_API_PRICE_INPUT_PER_M / MPN_API_PRICE_OUTPUT_PER_M from the official
pricing page - never baked in); worst-case cost estimated and reserved in
shared per-call cost files BEFORE any request, lowered to actual from the
response usage; failures keep the worst-case reservation; unreadable cost
records refuse paid generation. HONEST BOUNDS stated in code and docs: an
ESTIMATE gate, not a billing guarantee, and concurrent processes can
overshoot by at most one worst-case call each (bounded by the call-slot
cap). Paid generation remains OFF throughout; no API calls in this task.

## GitHub update EXECUTED with owner authorization (claude-fable, 2026-09-07)

Owner authorized the prepared plan ("yes push"). Executed exactly as audited,
zero force-pushes: (1) stale operator-card review note corrected (v2 is
coordinator-VERIFIED, paid steps still owner-gated); (2) pre-commit battery
PASS; (3) the 26-file set committed BY EXPLICIT PATH as 141898b including
the hard-import production_evidence.py; (4) merged
origin/codex/santa-checkpoint-2026-09-04 as 9530596 - all 8 conflicts
resolved by verified supersession (both-ways diff per file confirmed every
remote-only line was older superseded content: received_at clock, v1.0.0
prompts, pairwise-only logistics, pre-North-Pole assertion, 09-04 launch
text); (5) post-merge battery PASS (all 20 suites, 7/7 steps);
(6) pushed santa-ops-hardening-2026-09-04 (new) and fast-forwarded
codex/santa-checkpoint-2026-09-04 61d0f14..9530596 - PR #1 now carries the
full verified state. NOTE for Codex: your worktree at
.codex/worktrees/santa-checkpoint-2026-09-04 is now behind its remote; a
`git fetch && git merge --ff-only origin/codex/santa-checkpoint-2026-09-04`
inside it brings it current (your worktree, your move). No deploy, no
external submission, production still NOT STARTED.

Last coordinator check: 2026-09-05, post-18:14Z coordination clarification; spending v2 VERIFIED, packet wording review still open

## Review status and planning clarification (Codex, 2026-09-05)

Claim: this workboard status correction only, following the owner's pasted
Claude note. The v2 code is no longer awaiting coordinator review: see the
16:47Z independent safeguards review and the post-17:44Z green full release
check. Correct the worker's part-1 label below to VERIFIED. Packet wording
corrections remain separate; no source, budget or runtime setting changes.

The proposed v3 monetary gate is not built or enabled. Design constraints:
reserve the cost of the complete bounded input (instructions, schema and
customer message) plus maximum billed output before dispatch; share atomic
accounting across both adapters/processes; refuse unknown accounting or
pricing; retain uncertain reservations after timeout/crash/missing usage.
Concurrent workers must not each overshoot the application allowance.
Use model-specific, dated, verified rates rather than requiring the owner
to guess prices. Pricing drift and outside-account usage remain distinct
from an application's enforced budget. No 25-cent or other precise daily
allowance has been approved. No paid calls are authorized by planning.

Owner confirmed the planning assumption of $0 ADDITIONAL service cost for
the existing phone plan, website hosting and computer. This does not add a
new phone automation service or make an offline PC answer customers. The
latest request is a Gemini prompt for independent planning, not a model
installation, replacement build, external submission or paid test.


## Packet handoff independent recheck (Codex, 2026-09-05, post-17:44Z)

Claim: read-only review of Claude's parts 2-5 READY_FOR_REVIEW handoff;
this coordination note only. No source, runtime configuration, application
document, credential or private customer state edited by this review.

VERIFIED: the formerly failing copied-document fixture now passes without
removing evidence checks. Focused validator/evidence/packet suites: 28 passed,
11 subtests. Full `python -B scripts/ops_check.py`: all 7 steps PASS;
644 passed, 5 skipped, 52 subtests in 71.51 seconds, all 20 suites found.
The previous 1-failed release result is superseded for this working tree.
Preflight explicitly does not certify final submission readiness.

Packet review remains open for bounded wording corrections: reservations
PRODUCTION.md still says key configuration starts production model use and
omits the new positive allowance; production-deployment-record.md still
labels locally tested capabilities LIVE and has stale inquiry-based duration
and configuration-based model evidence rows; opn-form-answers.md retains one
2026 "is running" claim and calls uncorroborated history corroborated;
OPN-SUBMISSION.md calls `--demo` deterministic without forcing offline and
describes its four-inquiry batch as one request. Do not weaken final evidence
checks or fill real placeholders to clear these issues. Claude's packet
owner can correct these exact descriptions against the existing code.

Latest owner discussion: local Llama/Ollama or OpenAI gpt-oss is a proposed
alternative, not an authorized model migration or proof of OPN eligibility.
They want only cents per day and asked how long $14 would last. Paid calls
remain off. The current shared allowance is a request cap, NOT a cent cap;
no exact daily monetary allowance has been approved or implemented. Public
form submissions queue work; model generation is operator-triggered, and
the T-Mobile number has no automated model connection. No paid test, phone
activation, purchase, commit, push, deployment or customer send occurred.


## Spending v2 independent review (Codex, 2026-09-05T16:47Z)

Claim: independent read-only review of Claude's part-1 READY_FOR_REVIEW
handoff, plus this coordinator note only. Claude retains ownership of
the in-progress packet/document corrections. No source, runtime or other
worker files were edited by Codex during this review.

Result: VERIFIED for the revised local spending safeguards, not deployment
or a dollar guarantee. Paid generation defaults off in BOTH adapters even
with a key; an explicit positive allowance is required. Atomic slot files
replace the old read/check/append counter, and accounting allocation errors
refuse requests. Inquiry/content size and output-token bounds are present.
The old four rejection findings are resolved for the reviewed scope.

Independent checks: 225 passed across triage, content adapter and web-inquiry
suites. An additional temporary-state probe launched 24 separate processes
using both real quota implementations with cap=3: exactly 3 grants; fresh
content and triage processes then both refused. Slot contents were only
timestamp/adapter metadata. These were allocation tests, not API calls.

Scope limits: processes must use the SAME absolute private quota directory
and consistent allowance. This is not account-wide across machines/users,
does not survive an operator deleting its accounting state, and does not
establish a provider hard-dollar cutoff. The mirrored implementations need
cross-adapter regressions maintained together. No budget or paid operation
has been authorized by this review; real model/schema acceptance and
customer operation remain unverified.

Full release recheck during Claude's document updates: FAIL, 1 failed,
643 passed, 5 skipped, 52 subtests. All 20 suites discovered; slot validator,
Ms. Claus review, tracker privacy and whitespace checks passed. OPN preflight
also fails because the submission-validator suite fails. Exact reproduced
test: scripts/test_validate_opn_submission.py::ValidatorTests::
test_complete_final_fixture_passes_in_isolation. Its copied-document
fixture still leaves one submission placeholder, and launch-claim parsing
mistakes historical 2025-11-15 / 2025-12-24 references for the current
synthetic 2026-08-01 launch. The isolated test reproduces all three findings.
The pytest cache also retained an older slot-test failure ID, but that was
not the failure reported by this full run; do not infer a second regression.

Next for the packet owner: align the fixture with the revised documents
and distinguish historical/explicitly non-launch context from actual launch
claims without weakening final evidence gates. Keep real missing evidence
as missing. Run the focused validator suite and then the release checks
after document edits stabilize. Current whole-release status is BLOCKED,
not the earlier reported 644-pass green. Do not repeat the known failure
on unchanged inputs. No new public commit, push, deployment, live API call,
credential handling, customer record or message occurred in this review.

## Spending safeguards v2 + packet corrections (claude-fable, 2026-09-05T07:05Z)

Claim: fix ALL four confirmed budget defects + application-doc corrections +
GitHub update preparation + packet update | owner: claude-fable | files:
tools/triage/triage.py (budget region rebuild: atomic O_EXCL slot-file
reservations in a shared quota dir, default paid generation DISABLED,
fail-closed accounting), tools/triage/test_triage.py (budget regressions
incl. concurrency/mixed-adapter/corruption/failed-write/restart),
tools/triage/README.md, business/reservations/openai_adapter.py + its test
(same shared quota, cap honored incl. 0/default-off),
docs/day-one-operator-card.md (spending section corrected after fix),
docs/production-deployment-record.md + business/reservations/PRODUCTION.md
(claims audit fixes), docs/OPN-SUBMISSION.md (supported-facts update,
missing evidence marked), this workboard | boundaries: no paid calls, no
key handling, no commit/push (GitHub update PREPARED only, awaiting new
authorization), synthetic fixtures only.

Result (part 1 - spending safeguards v2): claude-fable | status:
VERIFIED by Codex (2026-09-05T16:47Z; full release rechecked after 17:44Z) | all four rejection findings fixed at the root:
(1) CONCURRENCY - the count is now atomic O_CREAT|O_EXCL slot-file
reservations in one shared quota dir (%LOCALAPPDATA%\MiamiPapaNoel\api-quota,
override MPN_API_QUOTA_DIR); 8-thread race regression proves exactly cap
grants, never more. (2) UNREADABLE ACCOUNTING now REFUSES paid generation
(BUDGET_ACCOUNTING_UNAVAILABLE) - quota-dir-as-file and PermissionError
probes both refuse with zero requests; the allowance can never reset.
(3) CONTENT ADAPTER now mirrors the same scheme (no cross-stack import,
same dir + slot naming): default/0/unreadable cap refuse with a rejected
manifest and no transport call; a triage-claimed slot reduces the content
allowance (mixed-adapter regression both directions). (4) DEFAULT IS
ZERO-SPEND: unset cap = PAID_CALLS_DISABLED even with a key; every paid
test opts in explicitly. Also added: input bound (6000 chars,
MODEL_INPUT_TOO_LARGE, nothing sent), cap ceiling 500/day, restart
persistence + timeout-consumes-slot-never-retries regressions, secret/
inquiry-text-free slot+ledger assertion. Docs corrected (README v2 section,
operator card v2 section) and both now state plainly: request/token limits,
NOT a dollar guarantee; dashboard alerts are not a verified cutoff. Tests:
triage 123, adapter 14, web_inquiry 88; FULL BATTERY 644 passed, 5 skipped,
52 subtests, 20 suites, ops_check 7/7 PASS. Parts 2-5 (doc/claims audit,
GitHub update prep, packet) in progress via read-only audit workflow.

Result (parts 2-5): claude-fable | status: READY_FOR_REVIEW | (2) workflow
verification carried by the standing suites (644) - no UI change this cycle,
prior browser QA stands. (3) CLAIMS CORRECTED per 3-auditor read-only audit:
business/reservations/PRODUCTION.md (launch date -> [TO FILL] + installation-
checkpoint note; status -> NOT STARTED; "Live" -> "Built"; no-model-run
caveat; "assists in operating" -> future tense; orchestrator qualified;
health-daily corrected) + OPS-LOG.md "launch" -> installation checkpoint.
(5) PACKET CORRECTED: opn-form-answers.md no longer presents the attested
2025 season as satisfying the 15-day requirement, states plainly the 2026
window has NOT started, present-tense "running it again" removed,
"the client" -> family-business wording, MISSING-EVIDENCE marks on AI-work
and 14-visit claims, placeholders converted to validator-matching [TO FILL:]
form; OPN-SUBMISSION.md Last-updated line, family-business relationship,
payment-gate row un-stales Stripe, six-DRAFT-validation-gates labeling,
launch clock aligned to the send-timestamp predicate, 2017 claim marked,
reviewer-clone NOTE; gap-report stale dates/rule/rails/optionality fixed;
evidence-index stale test name + CORROBORATED->ATTESTED + rails; release-
monitoring 45-tests removed + rails; release-checklist + account-setup-
checklist rails harmonized; production-deployment-record "Implemented
functionality" + attested-status + clock + relationship. Validator fixture
updated to the new audited wording (20 passed + 11 subtests); dates moved
off the LAUNCH_LINE_RE trigger line. Preflight: PASS, 0 blocking, 9 honest
warnings. FINAL BATTERY: 644 passed, 20 suites, ops_check 7/7.
(4) GITHUB UPDATE PREPARED, NOT EXECUTED (needs new authorization): branches
diverged at 9485bb8 (4 local commits vs 2 remote; 61d0f14 NOT an ancestor of
cb03e99); plan = (a) commit the uncommitted set BY EXPLICIT PATH (12 modified
+ docs/codex-day-one-handoff.md, docs/day-one-operator-card.md,
tools/triage/production_evidence.py which is a HARD import - pushing without
it ships a broken branch; never git add -A; Claude outputs/ + _to_delete/
now gitignored), (b) true merge of origin/codex/santa-checkpoint-2026-09-04
into the local branch - 7 known conflict files, resolve by union keeping
both guard sets, (c) push local branch, then fast-forward the PR branch
(merge has 61d0f14 as parent, so NO force anywhere), (d) ff-only update
inside the Codex worktree. Push-blocker CLEARED: the one private temp path
(workboard QA line) is redacted; secrets/customer-data scans clean
(synthetic canary + 555 fixtures only) | blockers: commit/merge/push await
owner authorization; single next owner action unchanged.

## Spending-control coordinator review (Codex, 2026-09-05T06:19Z)

Claim: review Claude's READY_FOR_REVIEW budget handoff without changing its
source; update this workboard and docs/day-one-operator-card.md only so the
owner is not instructed to spend against unverified safeguards. The owner
has raised affordability concerns; no new paid test, launch, service or
budget has been authorized. Preserve manual/offline operation and the
existing blocked Day 1 goal. Do not ask again for a paid test on each loop.

Review status: BLOCKED / corrections required, not VERIFIED. Existing
focused tests independently pass: 125 across triage and content adapter.
Three additional synthetic, network-blocked temporary-state probes confirm:

- tools/triage/triage.py:469-477 checks the ledger and appends separately.
  With two synchronized callers and cap=1, both reached the mocked API
  (2 requests). The cap is not concurrency-safe across operator processes.
- tools/triage/triage.py:429-446 treats every ledger read OSError as zero
  calls; the mocked PermissionError probe returns 0. An unreadable history
  must refuse paid generation, not reset the allowance. Malformed rows and
  reservation/write failures also need explicit fail-closed handling.
- business/reservations/openai_adapter.py:90-108 never consults the daily
  cap. With MPN_API_DAILY_CALL_CAP=0 it still invoked the injected content
  transport once. An output-token bound does not disable or count calls.

Also, the default permits 12 triage attempts once a key/model is configured,
not an owner-approved zero-spend default. The current cap is per ledger,
not an account-wide dollar ceiling. The card's recommendation to set a
provider hard spend limit is not verified and must not be relied upon.

No actual network call, credential, customer data, production ledger,
runtime configuration, source change, commit, push or deployment was used.
Probe scratch state was temporary. Claude's 632-test full-battery report
is retained below as its report, not independent coordinator verification;
the earlier 626-test result predates this patch. Do not rerun the full
battery merely to turn these missing cases green. Next code handoff must
cover all paid paths with an explicit opt-in, atomic shared reservations,
and fail-closed ledger errors, with mocked regressions for these cases.
Do not resume paid operation merely because tests pass; owner budget and
authorization, real model verification and genuine use remain separate.

## Spending controls for paid model calls (claude-fable, 2026-09-05)

Claim: local API budget gate at the shared model-call choke point | owner:
claude-fable | files: tools/triage/triage.py (call_openai_triage region +
budget helpers only - preserving the evidence-clock and check-model work),
tools/triage/test_triage.py (append), tools/triage/README.md +
tools/triage/log-schema.md (budget knobs + new error codes),
business/reservations/openai_adapter.py + tests/test_openai_adapter.py
(max_output_tokens bound only), docs/day-one-operator-card.md (budget note),
this workboard | design: deterministic daily call cap (MPN_API_DAILY_CALL_CAP,
default 12, 0 = paid calls disabled) counted in a private ledger outside Git
before each request; per-call MPN_API_MAX_OUTPUT_TOKENS bound (default 900)
in the request payload; over-cap -> deterministic offline fallback with its
own error code, never a paid request; token usage recorded after success for
visibility. HONEST LIMIT: calls+tokens, not dollars - no price table is
invented. No API request, no credential handling in this task.

Result: claude-fable | status: READY_FOR_REVIEW | files as claimed | tests:
triage 115 passed (7 new budget regressions: cap-0 and unreadable-cap send
NOTHING and write nothing; cap-2 allows exactly 2 then falls back with
BUDGET_CAP_REACHED and zero further requests; failed attempts count and are
never auto-retried; max_output_tokens 900 default / env override present in
the payload; ledger carries counts only - no key, no inquiry text);
reservations adapter 10 passed (max_completion_tokens 800 bound asserted);
FULL BATTERY 632 passed, 5 skipped, 52 subtests, all 20 suites, ops_check
7/7 PASS first run | integration notes: --check-model is now metered too -
its no-writes invariant was narrowed to permit exactly the paid-call ledger
(fixture asserts the single allowed file); the 23-case failure regression
sets an explicit high cap so it tests diagnostics, not the budget; new
error codes PAID_CALLS_DISABLED / BUDGET_CAP_REACHED documented in
log-schema.md; budget knobs documented in triage README + operator card
(card recommends MPN_API_DAILY_CALL_CAP=3 for day one and a provider-side
dollar limit, which no local control replaces) | blockers: NONE for the
control itself; paid generation remains inert until the owner configures
the rotated key.

Status: VERIFIED (local implementation only). Prior goal turn made concrete progress: --check-model
and operator instructions, 583 full-suite tests passed. Private key/model
are still absent in this process; no authorized live replacement test can
run here yet. Bounded next defect: --status counts any production row, and
the submission validator can combine an old fallback date with a new AI
reply. Claim tools/triage/production_evidence.py (new shared predicate),
tools/triage/triage.py, tools/triage/test_triage.py,
scripts/validate_opn_submission.py, scripts/test_validate_opn_submission.py,
tools/triage/log-schema.md, tools/triage/README.md,
docs/production-launch.md, docs/day-one-operator-card.md,
docs/codex-day-one-handoff.md, docs/OPN-VALIDATION.md and this workboard.
Use recorded real, non-fallback, gated, reviewed/sent evidence and full
elapsed timestamps; no qualification guarantee or changed customer records.
All tests synthetic/offline; no credentials, sends, push or deployment.

Result: one shared reviewed-model-send predicate now controls both status
and submission duration. It excludes fallback, pending, missing/failed-gate,
unnamed-reviewer, error and invalid timestamp records. Full UTC elapsed
time starts at the recorded send, not an earlier fallback inquiry. New real
CLI records carry offsets; legacy local timestamps are interpreted in the
operator machine's timezone. Status rejects malformed/contaminated JSONL
and duplicate IDs without printing record bodies. Neither tool declares
OPN qualification from elapsed time. Extreme UTC-conversion dates were
probed, fixed to reject cleanly, and pinned with regressions.

Final checks: 129 focused tests + 11 subtests passed. Full ops check:
626 passed, 5 skipped, 52 subtests; all 20 suites and all operations checks
PASS. Changed-file credential-pattern scan: 13 files, zero findings.
No production log exists at the default path; key/model presence remain
false in this process. No live model request, customer message, production
record, deployment or Git commit/push was made. All exec checks finished.

Goal audit: setup/checklist and demonstrated local defects are handled.
Actual Luna structured response/gate acceptance and genuine reviewed/sent
customer operation are NOT verified. The same private replacement-key
dependency was recorded in the initial goal/handoff turn, the model-check
continuation and this continuation, and is still present on recheck. Goal
is BLOCKED pending owner setup/results, not complete. The completed code
and this turn's tests are progress, not customer-use evidence. Next owner
action: follow the private setup in docs/day-one-operator-card.md and run
--check-model in that same terminal. Share only the non-secret result.
After a real model pass, use an actual incoming inquiry and record human
review/send honestly. While inputs remain unchanged, do not run more API
probes, fabricate records, add speculative features or repeat full suites.

## Model-check CLI (Codex, 2026-09-05T04:34Z)

Claim: explicit synthetic `--check-model` with nonzero fallback status and
no inquiry log or approval. Files: tools/triage/triage.py,
tools/triage/test_triage.py, tools/triage/README.md,
docs/production-launch.md, docs/codex-day-one-handoff.md, this workboard.
Use the existing Responses/schema/bilingual gates, not a second adapter.
Test with mocked API responses only; no exposed key, live request, real
inquiry, launch attestation, commit, push or deployment. Leave Claude's
operator-card/browser-review claim and scratch folders untouched.

Result: implemented and locally verified. Focused tests: 71 passed. Full
ops check: 583 passed, 5 skipped, 41 subtests; all 20 suites and every
ops step PASS. CLI smoke without private configuration returned exit 1
and NOT VERIFIED, with no API call or inquiry log. The default production
status still reports NOT STARTED. No live Luna workflow success is claimed.

Coordinator review: Claude's operator card is now READY_FOR_REVIEW, so
Codex additionally claims docs/day-one-operator-card.md for two doc fixes:
use --check-model instead of the synthetic logging command, and distinguish
verified model-backed reviewed/sent use from the legacy first-row counter.
The reported browser QA is Claude's evidence, not independently rerun here.
Source changes remain local and uncommitted. Next input: privately configured
replacement key and owner-authorized model check; genuine use remains later.

## Day-one continuation (claude-fable, 2026-09-05T05:05Z)

Claim: Luna-readiness without credential + fresh browser visual QA + day-one
operator card | owner: claude-fable | files: docs/day-one-operator-card.md
(NEW), this workboard | read/run only elsewhere: adapter request-contract
inspection, offline browser journey on synthetic scratchpad state
(desktop + mobile), no API request, no credential handling, no --real,
no config or source edits | test: browser journey evidence + focused
checks; no full battery without source changes.

Result: claude-fable | status: READY_FOR_REVIEW | files:
docs/day-one-operator-card.md (NEW), this workboard | evidence:
(1) Luna-readiness without credential: triage adapter already sends the
modern Responses API shape the successful haiku used - /v1/responses,
store:false, strict json_schema text.format; MPN_MODEL flows as a plain
string, so no code change is needed for gpt-5.6-luna. Untestable from here:
schema acceptance + entitlement - exactly one bounded operator test remains
(command on the card, PASS = "model : gpt-5.6-luna" with no offline-fallback
tag). (2) FRESH BROWSER QA (real Chrome pane, synthetic scratchpad state,
--offline): public form renders bilingually with DEMO banner, consent and
OpenAI disclosure; ES home-visit submission -> receipt "Solicitud recibida
MPN-WEB-... / No es una confirmacion de reserva" with correct 786-975-9557
footer; operator sign-in; draft generated with red "Offline fallback /
Respuesta de respaldo sin IA" label, SPANISH DRAFT FIRST with English
retained, all six gates rendered PASS, locked $325 family price, Zelle-only;
genuine-customer checkbox verified INERT in demo (app.js real.disabled=!live);
approve -> "Aprobado; no se ha enviado nada"; Record manual send guarded by
a native confirm ("Have you actually sent...?") - browser auto-cancel proved
it blocks, stubbed OK recorded "Envio manual registrado". Mobile 375px: form
and desk render clean, no horizontal scroll; fresh navigation demands
sign-in again. (3) Operator card command syntax verified offline verbatim
(es/family_visit/6 gates). No repo state touched; QA server stopped;
scratchpad state only | blockers: the one bounded Luna test needs the
owner's rotated credential in the operator terminal | next: owner runs the
card's step 1-3.

## New Goal and Continuation Prompt (2026-09-05)

The user requested a new goal, then a prompt for Codex to continue the
build. Created the active goal: get the operator-assisted Mrs. Claus
workflow ready for genuine use, verify Luna through actual bilingual
gates, and establish Day 1 only from real reviewed/sent customer work.
Codex claims this note and docs/codex-day-one-handoff.md only for the
handoff. The pasted Claude transcript confirms the preflight is done;
do not restart it. The continuation file identifies the committed baseline,
newer diagnostic notes, exact successful/failed request scopes, credential
rotation, bounded test authorization and the remaining owner/host work.
No further API request, model configuration change, production activity,
Git commit/push or deployment was performed to prepare this prompt.

## Exact Haiku Request Succeeded (2026-09-05T04:29:06Z)

Owner: Codex. Scope: redacted result in this board and launch checklist;
no source/configuration edit. Status: VERIFIED synthetic API response,
not verified Santa integration, pricing entitlement or production use.

The user separately authorized their exact curl request: Responses API,
model gpt-5.6-luna, input "write a haiku about ai", store true. Executed
curl.exe once with the credential supplied through hidden terminal input
and in-memory stdin configuration, never a file or process command-line
argument. No retries or redirects. Curl exit 0, HTTP 200, returned model
gpt-5.6-luna, response status completed, 12 input tokens, 99 output tokens,
111 total tokens. The API returned a haiku. No raw response, credential or
identifier was persisted locally; store true was preserved as explicitly
requested, so this was not a no-provider-storage request.

This supersedes any blanket inference that the earlier zero balance or
gpt-4.1-mini-2025-04-14 failure rules out all model access. That earlier
request really returned credit_balance_exhausted; this different exact
request really succeeded. The reason for the difference and whether the
successful call was free are not established by the response. Do not
invent an entitlement, a paid charge or a grant-expiration explanation.

Santa's configuration was not changed and its structured bilingual/gated
path was not tested with gpt-5.6-luna. Next: with separate authorization,
verify that path using a privately configured replacement credential,
confirm available usage/terms, and retain synthetic/customer separation.
No customer activity or production log was created; no production date
or OPN qualification is asserted. Do not reuse the exposed credential in
scheduled jobs. No full battery rerun for these documentation-only notes.

## API Connection Diagnosis (2026-09-05T04:27:17Z)

Owner: Codex. Scope: this redacted coordination note only; no source edit.
Status: VERIFIED diagnosis; successful model access remains BLOCKED.
The user explicitly authorized one synthetic request using the supplied
test credential. Passed it through hidden terminal input, held only in the
test process, never written to source/config/logs or printed. The user has
been advised to rotate it because it appeared in chat; do not reuse it in
an automation. No credential, prefix or hash is recorded here.

Exactly one direct Responses API request was attempted, with redirects
disabled and a 1200-output-token cap. The configured snapshot was
gpt-4.1-mini-2025-04-14; it did not produce a usable model response. The API
returned HTTP 429 with the allowlisted code credit_balance_exhausted.
This confirms exhausted prepaid credit for that request, not why the
earlier balance changed. Do not infer charges or expired grants without
the account's billing evidence.

The existing build_record path handled a synthetic Spanish home-visit
inquiry: language es, fallback_used true, model offline-rules-v1,
error_code MODEL_HTTP_ERROR; English and Spanish fallback drafts present,
all six gates PASS, real_customer false. No customer message, approval,
payment or production log was created. No retries; the process exited.
No full regression rerun is warranted for this note-only update.

Next: the owner resolves available API credit or selects an authorized
funded organization, rotates the exposed key and configures its replacement
privately. Only then run a separately authorized synthetic model-backed
check. Keep auto-reload off unless the owner chooses otherwise. This test
does not begin the production window or satisfy the 15-day requirement.

## Coordinator Wrap-Up (2026-09-05)

Status: VERIFIED. Owner: Codex. The user authorizes local commits and
wrap-up, not push or deployment. Claude's READY_FOR_REVIEW handoff is now
present; independently reproduced 44 passed, 1 Windows symlink skip.
R1 and the public proxy mismatch are fixed. The remaining R2 demo cases
still accept a set proxy (direct browser requests lack its required header)
and ignore MPN_PUBLIC_ORIGIN. Codex claims the narrow final correction in
tools/launch_preflight/preflight.py, its tests/README/handoff, suite
registration in scripts/ops_check.py, and this board/checklist handoff.
Claude should leave the delivered folder frozen while this review closes.
After focused regressions: full release checks, explicit scoped staging,
and a local checkpoint commit. Exclude Claude outputs/ and _to_delete/.
Hosting, API access and genuine production evidence remain separate; do not
translate this commit or test run into a launch date.

Final review result: R1/R2 closed, including direct-demo proxy/origin
settings. The delivered checker is integrated into the 20-suite routine;
no further Claude implementation is pending for this task. Focused result:
65 passed, 1 Windows symlink skip. Full `python scripts/ops_check.py` exits
0: 564 passed, 5 skipped, 41 subtests passed; suite coverage, slot validator,
Ms. Claus review, tracker privacy, diff check and OPN preflight all PASS.
Source-hash comparison found no changes across 98 files during the run.
The scoped 50-file credential-pattern scan returned no findings; private
queue/log/receipt files and unrelated scratch folders are not included.

Checkpoint scope: bilingual private inquiry/review queue and maintenance,
uninstalled hosting templates, launch preflight, overnight booking/route
and quote protections, North Pole personas, regression tests and honest
launch documentation. Source-level/client-session checks pass; the latest
branding still needs a fresh visual browser pass, and Linux/TLS/restart/
alert delivery/hosted restore have not been verified on a selected host.
No preview process was restarted, account changed, message sent, model
success asserted or production log created. No push/deployment authorized.
Next: retain this checkpoint; resume only on an actual unclaimed task or
changed hosting/API/provider inputs. Do not rebuild delivered work or rerun
the full battery merely because the scheduled check wakes.

## Scheduled verification (2026-09-05T03:58:37Z)

{"at":"2026-09-05T03:58:37Z","owner":"Codex heartbeat","status":"BLOCKED","files":["docs/santa-agent-workboard.md"],"tests":{"python scripts/ops_check.py":"exit 1: only the previously reported unregistered launch-preflight suite; listed battery 499 passed, 4 skipped, 41 subtests; other six steps PASS","python -m pytest tools/launch_preflight/test_launch_preflight.py -q --tb=short":"23 passed, 1 skipped; does not cover R1/R2","slot_validator":"PASS via ops_check","OPN_preflight":"PASS via ops_check, not qualification","git_diff_check":"exit 0"},"blockers":["Claude R1/R2 unchanged; no handoff","hosting/API access and deployment approval still needed"],"next":"Preserve worker ownership; integrate only after corrected handoff. Existing 30-minute automation/end date/notification preference preserved; prompt updated to check changed state and avoid repeating the full battery or owner requests while unchanged. No new notification, purchase, deployment, customer send or production evidence."}

## Dependency audit (2026-09-05T03:52:26Z)

Third consecutive NO PROGRESS audit, 2026-09-05T03:53:44Z. Re-read routing
and coordination instructions, current HEAD/status, preflight files and
handoff presence, current-process configuration and browser tabs. The same
dependencies remain: no corrected Claude handoff, no accessible signed-in
hosting account, no configured API/model/operator/public-origin/proxy here,
and no deployment authorization. No live process/job handle is confirmed.
No source edits or repeated tests can establish those missing external
facts. Goal is BLOCKED, not complete; all work and reservations preserved.

Resume with owner hosting access/deployment decision or Claude's corrected
handoff. Recheck the current files first; verify R1/R2 before registering
the new suite and running the whole release check. A successful configured
synthetic model test and genuine customer use still must occur separately.
Do not backdate a launch or count these audits/tests as production use.

Second consecutive NO PROGRESS dependency audit, 2026-09-05T03:53:04Z:
HEAD/status and preflight files unchanged; no handoff or live worker handle.
Current-process key/model/token/public-origin/proxy remain unconfigured.
The Vercel tab handle is no longer in the browser session; a fresh tab list
has no Vercel page. No inference of a successful sign-in, no automatic
reopening or browser switch. Owner hosting access and API setup, plus
Claude's corrections/handoff, still require an external state change.
Only this audit note changed; goal remains active at this second check.

Previous goal turn: PROGRESS (reproduced preflight R1/R2 and verified the
integration gate). Current turn: NO PROGRESS toward implementation/launch,
first consecutive dependency audit after that progress. Preflight files
are unchanged and no handoff is present; preserve Claude ownership. No
confirmed live job handle is available and no duplicate worker was started.

Checked existing-host access without account changes: the in-app Vercel
dashboard redirects to its login page. Browser discovery confirms only the
in-app browser is connected, no external browser session. Left the login
page open for the owner. Account/project/plan remain unverified; signing
in to the existing account is the next hosting input, not creating or
upgrading an account. API connection verification remains outstanding.
No source edits, new test runs, purchase, deployment or production activity.

## Launch-preflight review findings (2026-09-05T03:49:21Z)

Previous goal turn: PROGRESS (request-parser fix, regression verification
and existing-host compatibility check). New safe action: read-only review
of Claude's arriving preflight implementation/tests. At inspection no
handoff.md exists, so this is not an integration approval or a claim that
the worker is finished. Claude retains its files. Coordinator owns this
review note only; no edits to tools/launch_preflight or ops_check yet.

Reproduced against the arriving preflight.py (write time 23:47:31 Miami):

- R1: check_origin(public, 'https://[') raises an unhandled ValueError.
  Origins with :wrong, :99999 or a space in the hostname return CONFIGURED.
  Fail closed with a redacted finding for malformed URL/port/host input;
  invalid input must preserve deterministic CLI exit/JSON behavior.
- R2: public proxy '127.0.0.1 ' returns CONFIGURED because preflight strips
  it, but the service's parse_ip rejects the exact environment value.
  In demo mode proxy '127.0.0.1' is described as unused, yet server.main
  passes it to App even with --offline: a direct browser supplies no proxy
  header and client_ip returns HTTP 400. Demo origin overrides likewise
  must be checked against actual MPN_PUBLIC_ORIGIN behavior, not ignored.
  Reconcile the checker with the runtime without weakening runtime guards.

These were in-memory, synthetic, no-network probes; no App was initialized
and no queue/customer/API/provider state was created. Include negative and
normal controls in Claude's existing suite. Integration waits for the
handoff and resolution; do not call the currently unregistered suite part
of the earlier 499-test checkpoint. Review note is actionable new evidence,
not a reason to restart or duplicate Claude's worker.

Verification: the arriving suite runs 23 passed, one Windows symlink skip.
It does not exercise R1/R2. The suite-coverage gate now fails specifically
because tools/launch_preflight/test_launch_preflight.py is not registered;
registration remains coordinator-owned and pending review completion. The
overall worktree must not be described as release-green using the earlier
499-test result. No handoff.md was present at the last read. No confirmed
worker handle is available to poll, so there is no verified running wait.

Current turn: PROGRESS through concrete review findings and validation of
the integration gate. No worker implementation was changed, no service or
external account was started, and no live API/customer evidence was made.
Next: Claude resolves R1/R2 and supplies its handoff; coordinator verifies
the updated implementation and registers/runs the complete release suite.

## Hosting fit and malformed-request review (2026-09-05T03:44:29Z)

Previous goal turn: NO PROGRESS (read-only inspection interrupted by the
owner's hosting clarification; no implementation or verified running wait).
Current safe action: inspect the existing static hosting contract and test
the suspected unhandled JSON recursion path before Internet deployment.

Claim: Codex coordinator, VERIFIED locally; files: tools/web_inquiry/server.py,
tools/web_inquiry/test_web_inquiry.py, tools/web_inquiry/README.md,
docs/tonight-launch-checklist.md and this workboard. Scope: malformed HTTP
JSON must return a sanitized bilingual error without storing a request or
calling the model. Add failing synthetic regressions, fix narrowly, review,
then run the full battery. Claude's reserved preflight folder is untouched.

Hosting evidence: README.md and vercel.json describe static Vercel hosting;
no local .vercel project link or .openai/hosting.json is present. This does
not establish the currently deployed account, plan or available credits.
Official Vercel documentation says function filesystems are ephemeral and
cannot provide this queue's shared persistent local SQLite storage. Keep
the website unchanged; the current backend needs a persistent host, or an
explicitly selected redesign using durable external storage. No redesign,
new account, spending, deployment or migration is authorized by this audit.

Result: four new HTTP regressions failed before the fix with
RemoteDisconnected and server-side RecursionError. Arrays and objects nested
1100 levels, within the existing 16 KiB body limit, affected both public
intake and authenticated drafting. Added RecursionError to the request JSON
decoder's existing refusal handler; auth, origin, size and rate checks are
unchanged. The four tests now verify bilingual 400 errors, no saved inquiry
or audit event, no model invocation or parser traceback, healthy service
and a subsequent valid submission. Focused inquiry suite: 88 passed.

Coordinator inspected the one-line implementation delta and regression
scope. Full `python scripts/ops_check.py`: 499 passed, four platform skips,
41 subtests, 19 suites, all seven checks PASS. The 96 checked source/config
file hashes matched before and after. No implementation writes occurred
during the full run. Updated the inquiry README and concise owner checklist
with the error behavior and source-linked Vercel hosting limitations.

Current turn: PROGRESS (reproduced/fixed/verified request handling and
established existing-host compatibility constraints). No public deployment,
purchase, commit, push, real API call, customer message or production
evidence. Current-process API/model/operator/public-origin/trusted-proxy
configuration is absent; other terminals' settings remain unknown. At the
initial check the reserved Claude folder was absent. The next external step is identifying the existing
hosting account/project and approving a deployment arrangement, plus a
successful model-backed connection test. Overall launch remains incomplete.

Late arrival after the full battery: tools/launch_preflight/preflight.py now
exists (filesystem write time September 4, 23:47:31 Miami). No test file or
handoff.md was present when listed. The 499-test checkpoint predates this
arrival and does not verify the new CLI. Preserve Claude's reservation and
wait for its explicit handoff before integration. No live worker/process
handle has been confirmed; a new file alone is not a verified running wait.

## Claude verification handoff review (2026-09-05T03:41:33Z)

Claim: Codex coordinator, VERIFIED (handoff review and local rerun); files: this workboard and
docs/claude-next-task.md only. Reconcile the owner-pasted Claude report,
preserve its original results below, and rerun the local ops battery.

The reported 22 local HTTP probes and 495-test result are present in
Claude's workboard entry. Treat the probes as Claude-reported: this handoff
does not supply the consolidated probe script or raw run output for replay.
The earlier failures' cause is not established by passing reruns or growing
test counts. Request failing test IDs and sanitized tracebacks if available;
do not silently label them resolved concurrency defects.

The report's IN_PROGRESS proxy status is superseded by the locally VERIFIED
persistent-host result above the older entry. No host has been selected or
deployed, no successful live model request is established, and the local
offline exercise does not establish customer production use. Keep the
reserved Claude preflight task; do not rebuild the inquiry/proxy/backup kit.

Verification rule: checkpoint writers before a full-battery run and retain
failure details. This coordinator will make no implementation edits during
the run and will compare source hashes before/after; another worker's
checkpoint cannot be assumed from a report alone.

Result: independent `python scripts/ops_check.py` rerun PASS: 495 tests,
four platform skips, 41 subtests, 19 suites, all seven steps green. Hashes
of 96 source/configuration files matched before and after the run; this
does not establish the cause of Claude's earlier failures. API credentials
and model selection were cleared only in the test subprocess environment.
No live model call, real customer activity, deployment or Git write occurred.

Reconciled the newly supplied report and updated Claude's bounded handoff
with the completed proxy status and a request for replayable probe/failure
artifacts. The reserved preflight folder is still absent; no running Claude
job is inferred. The overall launch goal is not complete. Host selection,
authorization and a successful configured model test remain external steps.

## Launch dependency recheck (2026-09-05T03:38:08Z)

Second consecutive no-progress check, 2026-09-05T03:38:47Z: repo instructions,
HEAD, status and reserved folder rechecked. No Claude preflight or handoff
exists; runtime key/model/token/origin presence still false. Hosting account,
budget and deployment authorization remain unanswered. No confirmed running
job to wait on, no new code to review and no externally authorized launch
action. Only this audit note changed; goal remains active pending the next
dependency check, not complete. Do not infer a failed Claude process from
an absent folder, and do not start a duplicate worker.

Previous goal turn: PROGRESS (hosting/backup/readiness implementation,
independent reviews, 495-test full verification, North Pole naming and
Claude handoff). Current turn: no implementation progress; dependency and
runtime recheck only. HEAD and worktree remain unchanged apart from this
coordination note. No tools/launch_preflight directory exists yet; there is
no confirmed live Claude job handle to wait on or restart. Reservation stays
PLANNED and no work is taken from it.

This Codex runtime reports API key, model, operator token and public origin
all unconfigured (presence only checked, no secret values read or printed).
Port 8226 has no listener and fresh triage --status remains NOT STARTED.
Owner hosting account/budget and deployment authorization are still missing.
Do not infer that other private terminals are configured from this check.

Attempted an inert in-memory layout preview in the documented in-app browser;
navigation failed and the temporary tab stayed about:blank. Closed that tab.
No alternative server restart or browser-control mechanism was attempted.
Phone-size visual verification therefore remains pending, not passed.

First consecutive no-progress dependency audit after the prior progress
turn. Overall goal stays active, not complete. The next real action requires
owner hosting/API setup or a READY_FOR_REVIEW Claude artifact. Do not create
more checklists, duplicate tests or simulated production activity to fill the
wait. Stripe, phone voice/SMS and posting remain separately unfinished.

## North Pole team identity (2026-09-05)

User requests every agent belong to the North Pole theme. Claim: Codex
coordinator, READY_FOR_REVIEW (copy/tests complete; browser QA pending).
Files: docs/north-pole-agent-team.md (new),
tools/triage/triage.py and test_triage.py, tools/mrs_claus_office/intake.py,
tools/content/queue.py, tools/elves/outreach.py, tools/comms/adapter.py,
tools/web_inquiry/index.html, business/reservations/web_ui.py,
business/reservations/tests/test_web_ui.py,
business/reservations/openai_adapter.py and content_agent.py,
business/reservations/logistics_agent.py and reservation_agent.py.
Names, greetings and creative direction only; preserve machine actor IDs,
human approval, locked terms, real driving estimates and provider status.
Do not recast historical deployment documents as this new 2026 design.

Owner clarified exact agent names: Mrs. Claus (communications, warm female
EN/ES voice when connected), Santa Claus (content), Elf #1 bookings, Elf #2
logistics, Elf #3 outreach, Elf #4 monitoring. Future roles get sequential
elf numbers. Applied to role documentation, current UI labels and drafting
prompts/templates. Existing actor IDs and authority remain unchanged.

Claude handoff reserved by coordinator: PLANNED, tools/launch_preflight/*
(new), a read-only launch-readiness CLI. Read docs/claude-next-task.md before
starting. No edits to active coordinator/reviewer files or Git index.
Claude should return its exact suite path for coordinator registration;
scripts/ops_check.py stays coordinator-owned. Parent owns this workboard
until finishing the current verification; use the reserved folder's
handoff.md to return progress without racing workboard edits.

## Persistent-host preparation (2026-09-05)

Coordinator review result: proxy identity, authenticated storage readiness,
backup/restore and deployment Python/static contracts VERIFIED locally.
Wegener independently approved all three repaired readiness findings after
14 targeted tests. Jason independently approved backup/restore with 73 pass,
four platform skips, eleven extra probes and eight deployment checks.
Main inquiry/maintenance/deployment battery: 182 pass, four skips. Tests use
synthetic data only. Three file-symlink cases need Windows privilege; POSIX
permissions await Linux. No actual Linux/systemd/nginx/TLS/reboot/host-browser
verification has occurred. Templates are offline-first and uninstalled.

Readiness now checks a 16 MiB disk-space floor plus 64 KiB main-database
allocation, always rolled back. No lasting table, customer or audit event is
created. Malformed, non-object, invalid UTF-8 and deeply nested stored JSON
produce sanitized failures. This health probe is not a model/payment/channel
test, disk-capacity guarantee, delivered alert or production-use record.

Backup creates unique private files via SQLite online backup and restore
checks actual schema/counts/data in a new directory. systemd/nginx examples
include restart, limits and private health/backup timers. Off-host encrypted
copies, retention, disk/backup-age alerts and their delivery still require
the selected host/owner setup. Host account/budget question is unanswered.

North Pole copy and Claude handoff are saved. All agent machine IDs remain
unchanged; triage prompt version advanced to triage-v1.1.0 for the new
Mrs. Claus greeting. Focused triage tests pass. Final ops rerun: 495 tests
pass, four platform skips, 41 subtests, 19 suites and all seven checks PASS.
Current browser preview remains stopped and latest text/layout
changes are not re-verified in a real browser. Female voice is a recorded
requirement, not an active provider connection. Claude is reserved only
tools/launch_preflight/*; its handoff instructions are docs/claude-next-task.md.

All review workers are now finished. No commits, staging, pushes, public
deployment, purchases, API requests or customer sends were performed.
This goal turn made concrete progress; overall launch remains active and
requires actual host/API authorization and verification, not further fake
activity or looping on unchanged missing account information.

Previous goal turn made progress: independently verified overnight and
inquiry review/privacy fixes, repaired runbook commands and test-count
drift. Current HEAD/worktree rechecked; all earlier uncommitted work remains.

Claim | owner: Codex coordinator | status: IN_PROGRESS | files:
tools/web_inquiry/server.py, tools/web_inquiry/test_web_inquiry.py,
tools/web_inquiry/README.md, deploy/inquiry/* (new),
scripts/ops_check.py (suite registration only), docs/tonight-launch-checklist.md,
this workboard. Implement explicit trusted-proxy client identity without
trusting arbitrary visitor headers; retain client and global abuse limits.
Prepare private persistent-host process, proxy and monitoring configuration,
but do not install services, expose a port, deploy or change provider accounts.

Delegated file reservation: tools/web_inquiry/maintenance.py and
tools/web_inquiry/test_maintenance.py (new) for a bounded backup/restore
worker. No other worker may edit these until review. Parent owns workboard.
Worker uses only synthetic temporary data, never existing customer state.

Maintenance worker Lagrange delivered READY_FOR_REVIEW: 73 pass, four
Windows/platform skips. Files unchanged during Jason's independent review.
Proxy review by Wegener passed identity/limit probes but requests changes
to readiness: a zero-row write misses exhausted storage, and valid non-object
JSON/invalid UTF-8 can escape sanitized errors. Coordinator accepts both,
retains server/test ownership and is adding meaningful bounded storage
probes plus malformed-record regressions. Deployment templates are offline
demo only, uninstalled; no preview, host, API or production state changed.

Docker CLI is present but its Linux engine pipe is absent. No daemon or
preview process was restarted. Hosting account, budget, authorization,
API availability, Stripe and phone integrations still need owner input.

## Tonight launch continuation (2026-09-05)

Final local result at 03:13Z: inquiry fixes VERIFIED by Codex coordinator
after Noether's independent approval. Reviewer reran 56 pytest cases,
including five Node client cases, plus concurrent-action, restart, delayed
JSON, pagination/logout and changed-selection probes; file hashes unchanged.
Full coordinator ops_check: 368 tests plus 41 subtests across 17 suites,
all seven steps PASS. Both reviewers worked only on synthetic state.
The overnight, quote-preservation, hard-fact and inquiry concurrency/privacy
fixes are verified locally; none are committed or deployed by this turn.

Documentation drift is closed: preflight now has nine warnings (missing
evidence/placeholders only), with no obsolete test-count warnings. Runbook
route commands parse cleanly. docs/tonight-launch-checklist.md contains the
owner inputs and distinguishes the initial assisted AI workflow from later
Stripe, phone, automatic availability, delivery, posting and outreach work.
Public-site fetch could not be completed by the web tool; no live-site
verification or deployment is inferred from local repository checks.

Next available engineering work: resolve the documented shared proxy
throttle with explicit trusted-proxy configuration and tests, prepare the
persistent host process/backup/monitoring setup, and verify hosted synthetic
EN/ES intake before public routing. Obtain owner hosting account/budget and
deployment authorization; configure the API privately and verify a real
model response. Stripe/phone/social accounts remain separate unfinished
integrations. Actual customer operation and 15-day evidence remain pending.
The overall launch goal stays active, not complete. All review workers are
finished. Existing unrelated files, local demo data and Git index preserved.

Inquiry review fixes READY_FOR_REVIEW: approval/rejection/manual-send
requests carry a SHA-256 revision of the exact displayed saved record,
checked inside the same SQLite write transaction as the state change.
Stale or missing revisions are refused; current snapshots still run the
existing policy and language/real-use checks. No schema migration needed.
Client requests are abortable and session-tagged. Logout clears private
state, discards old responses and does not resurrect another login's queue;
overlapping refreshes cannot replace newer displayed state. Controls send
the displayed inquiry ID/revision, not a mutable selection after rendering.

Six new backend revision cases failed before the fix. Four browser-client
logic cases failed before the fix. Current focused result: 56 pytest cases
pass, including the integrated Node harness with five synthetic DOM/fetch
cases. Tests also cover stale HTTP approval and post-approval reject/send
snapshots. Node.js 18+ is a test-only prerequisite; the service remains
Python stdlib-only. No real browser preview restart occurred; prior visual
layout QA remains historical. Client tests are a DOM/fetch harness, not a
claim of a new live-browser run. Full ops verification and independent
re-review are running. Keep these implementation files unchanged until review.

Public proxy rate-limit bottleneck remains documented and unsolved in this
slice; it will need explicit trusted-proxy configuration and tests. The
local service is not yet publicly hosted or authorized for public intake.

Inquiry review received: Noether requests changes for stale-tab approval
of an unseen regenerated draft and delayed refresh restoring customer data
after logout. Both independently reproduced. Current local suite: 46 pass.
Codex coordinator accepts the findings and claims tools/web_inquiry/server.py,
app.js, test_web_inquiry.py, README.md, client-tests.cjs (new) and this board
for fixes and regression coverage, status IN_PROGRESS. Existing uncommitted
inquiry implementation is preserved. The shared public throttle behind a
single proxy is a separate known hosting prerequisite, not solved by adding
proxy-only limits. No public deployment or preview restart is authorized.

Documentation drift claim | owner: Codex coordinator | status: IN_PROGRESS |
files: docs/OPN-SUBMISSION.md, docs/production-deployment-record.md,
docs/evidence-index.md, docs/gap-report.md, docs/evidence-intake.md,
docs/demo-runbook.md. All six files are clean before edit. Latest preflight
found obsolete numeric test counts; replace duplicated current-count claims
with runnable checks and the dated verification record. Do not fill missing
production model, operator evidence, customer counts or launch dates.

Coordinator result: overnight routing VERIFIED, not committed. Independent
reviewer Zeno approved all four changed code/test files with 39 checked-in
tests plus 41 subtests (excluding the filesystem-writing synthetic season
walkthrough), six additional probes plus 17 subtests, unchanged file hashes,
and no network/state writes. Probes included the actual health caller,
leap-day boundaries, date-report filtering, and cancellation recovery.
Coordinator full ops_check passed 358 tests plus 41 subtests, all seven
operational checks. Existing quote and hard-fact changes remain VERIFIED.

Operator runbook commands now parse in PowerShell with zero errors and no
stray carriage returns. The standalone check must receive both dates in the
same input file; omitted visits cannot be detected. Querying dates in the
reservation agent does not partition the source schedule. No public launch,
commit, push, payment, message, or production record was performed.

Fresh runtime checks: triage --status is NOT STARTED, and no listener exists
on port 8226. Owner hosting account/budget clarification has been requested.
Independent reviewer Noether (01a06f86-1fa6-7270-96b6-0d7dd1bfc643) is reviewing
the uncommitted local inquiry workflow and persistent-host prerequisites;
those files remain unchanged while that review is pending.

Additional documentation claim: docs/seasonal-ops-runbook.md | owner: Codex
coordinator | status: IN_PROGRESS. File is clean before edit. Repair the
broken route command escape sequences, document multi-date route input,
and replace the obsolete partial suite list with the actual full check.

Latest full verification after overnight changes: 358 tests plus 41
subtests across 17 suites; all seven ops_check steps PASS. Independent
overnight review and separate local-inquiry security review are pending.

Overnight implementation is READY_FOR_REVIEW: calendar-minute comparisons
now include cross-date/year-boundary overlaps and travel/setup buffers.
All active reservation logistics are refreshed together; querying another
date cannot clear an existing overnight conflict. Invalid active scheduling
facts block new approvals until repaired because unknown duration/date/setup
cannot safely be bounded to a day; valid confirmations remain locked.
The returned date report includes touching legs and invalid-input findings.
Standalone route lists now require recorded travel between successive dates,
not an implicit midnight reset. An unknown next-day drive requires review;
normal next-day visits with adequate known travel still pass. Numeric boolean
inputs are refused and invalid facts never enter route arithmetic.

Focused verification: 40 tests plus 41 subtests passed across routes and
season integration. Initial standalone regressions produced 11 failures;
initial reservation regressions produced 17 failures. Reverse-order test
fixtures were corrected to confirm the first booking before creating the
second, matching real intake and preserving the existing pending-hold rule.
The prior full run (standalone change only) passed 349 plus 26 subtests;
the new whole-tree ops check is running and supersedes that earlier result.
No code changes while the independent overnight review is underway.

Claim: Close overnight routing and prepare the owner launch handoff | owner:
Codex coordinator | status: IN_PROGRESS | files: this workboard,
docs/tonight-launch-checklist.md (new), tools/routes/route_check.py,
tools/routes/test_routes.py. The historical routes claim is committed;
the current files are clean and have been read before this follow-up.
business/reservations/logistics_agent.py and tools/test_integration_season.py
will be claimed only after independent review of their current dirty guard.

Independent read-only reviewer Zeno (01a06f81-3306-7190-a3f5-a9c94a897297)
is reviewing that guard and the same-package quote-preservation delta.
No provider calls, customer state changes, Git writes, public deployment,
or model-backed production activity are part of these synthetic checks.

Current launch configuration: this process has no OpenAI key/model or
operator token; the configured Stripe Payment Link is empty. vercel.json
contains static-site settings, not the persistent inquiry backend. The
local Python inquiry server binds only to loopback. A local development
loop is not an always-on host. See the new checklist for owner decisions.


## Overnight routing review (2026-09-05T02:41Z heartbeat)

Continuation review: independent reviewer Zeno APPROVED the pre-existing
hard-fact guard and quote-preservation deltas against 3fc83df. Evidence:
13 route tests with 14 malformed-input subcases, seven new quote cases
plus two controls, and five additional probes with 32 malformed-value
subcases. No reviewed files changed during review. Codex coordinator
accepts this review and marks those two earlier deltas VERIFIED (not
committed). Their implementation is preserved. Codex now claims
business/reservations/logistics_agent.py and tools/test_integration_season.py
for the separate overnight fix, status IN_PROGRESS.

Claim: Verify date-boundary reservation and travel checks without editing
pending implementations | owner: Codex | status: READY_FOR_REVIEW | files:
this workboard only. business/reservations/logistics_agent.py and
tools/test_integration_season.py remain dirty and READY_FOR_REVIEW from
the hard-fact guard. Do not change them before coordinator review. All
probes are synthetic, in memory, with store.append_event mocked; no
customer records, payment records, or production evidence are written.

Finding: cross-midnight overlap and travel checks are missing. The
reservation checker filters peers by exact date at
business/reservations/logistics_agent.py:65. The standalone checker groups
visits by date at tools/routes/route_check.py:114-118. Neither compares
adjacent dates. This is separate from the same-date hard-fact fix, which
remains untouched and pending review.

Reproductions used standard 60-minute synthetic Doral visits, valid
addresses/guest counts, and mocked operator verification of the exact
50% deposit. The following invalid pairs both reached confirmed with
logistics=ok: Dec 24 23:30 / Dec 25 00:15 (15-minute overlap), the same
pair approved in reverse order, Dec 24 23:00 / Dec 25 00:05 (5-minute gap
versus 10-minute estimated same-zone drive plus 5-minute buffer), and
Dec 31 23:30 / Jan 1 00:15 (year-boundary overlap). Feasible overnight
23:00 / 01:00 and separate-day 15:00 / 15:00 controls both confirmed.
The standalone route checker also returned OK with zero findings for
the overlap and 5-minute travel gap when given explicit 10-minute travel
and zero setup; its feasible overnight control returned OK as expected.

Verification: existing route/integration suites passed 25 tests plus
14 subtests. Full ops_check passed all 7 steps with 343 tests plus
14 subtests across 17 suites. These passing suites do not cover the
newly reproduced overnight gap. Slot validation, page review, tracker
privacy, OPN preflight and diff check passed. Only this workboard changed;
no code/test implementation, customer state, Git index, provider account,
preview process, or production evidence was altered.

Repair handoff: first obtain review of the existing dirty logistics and
integration-test changes. Then add failing overnight regressions and
compare actual date-time intervals across date boundaries, including
travel/setup/safety buffers, both approval orders, year rollover,
canceled peers, and valid separate-day controls. Preserve same-date
pairwise protection and locked confirmations. Until that fix is verified,
do not rely on either checker to approve overnight schedules: the
operator must inspect both dates and travel buffers manually. This is
not a new machine-enforced overnight block.

```json
{"at":"2026-09-05T02:43:55Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["docs/santa-agent-workboard.md"],"tests":{"reservation_probes":"4 invalid cross-date scenarios wrongly confirmed; 2 feasible controls confirmed","standalone_route_probes":"2 invalid cross-date routes returned OK with zero findings; 1 feasible control OK","existing_route_integration":"25 passed plus 14 subtests","ops_check":"343 passed plus 14 subtests across 17 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0, not final qualification","git_diff_check":"exit 0"},"blockers":["affected logistics and integration-test files have unreviewed dirty changes; no implementation edits this cycle","overnight overlap/travel checks remain unfixed","Stripe Payment Link remains absent; prior API/hosting/account/evidence prerequisites remain"],"next":"Coordinator reviews the existing hard-fact guard before another edit. Add and fix cross-midnight/year-boundary regression cases using full date-time intervals and route buffers. Require manual cross-date schedule review until verified. No commit, push, deployment, charge, customer send or production activity was performed."}
```

## Scheduling hard-fact guard (2026-09-05T02:11Z heartbeat)

Claim: Reject malformed scheduling facts before route approval | owner:
Codex | status: READY_FOR_REVIEW | files:
business/reservations/logistics_agent.py, tools/test_integration_season.py,
this workboard. Both implementation/test files are clean; their earlier
pairwise-conflict change was reviewed by Claude and committed. Preserve
all current unreviewed inquiry, triage, reservation-agent, and HTTP-test
changes. No Git index writes, commits, pushes, API calls, or deployment.

Reproduction: using in-memory synthetic records and a mocked event writer,
a standard visit at 15:00 with duration_min=-60 and another at 15:00 with
duration_min=60 both reached confirmed with logistics=ok. Scope: reject
invalid duration/setup/time/date facts conservatively during route review,
without changing prices, payment rules, or existing locked bookings.

Result: logistics now rejects nonpositive/non-integer durations, invalid
setup values, noncanonical/invalid dates, and malformed start times before
route arithmetic. Invalid scheduled holds no longer disappear from the
day check. New approvals on that date remain blocked until those facts
are corrected; valid existing confirmations remain locked. The returned
route report includes explicit invalid_schedule findings as well as
pairwise checks, so the CLI does not hide an invalid solo visit behind
an empty report. Canceled entries remain excluded. These are still
estimate-based route checks, not live traffic or a complete route planner.

Added seven synthetic regressions with fourteen malformed-input subcases.
The first selected pre-fix run failed both negative-duration/setup cases
and all fourteen malformed-input subcases (16 failures); the three
selected controls passed. Final focused integration run: 14 passed plus
14 subtests. Full ops_check: 343 passed plus 14 subtests across 17 suites;
all 7 operational steps PASS, including slot validation, page review,
tracker privacy, OPN preflight, and diff check. All event writers in the
new reservation probes were mocked; no booking or payment record was
written. Existing dirty/claimed files are preserved, and no Git index
change, commit, push, provider action, or preview restart was attempted.

The Stripe Payment Link is still empty. API 429 resolution, hosting and
public launch, mobile voice/SMS setup, owner verification, and genuine
operating evidence remain outside this synthetic test result. Next:
independently review this guard and its tests; separately check the
existing date-boundary behavior before accepting overnight schedules.

```json
{"at":"2026-09-05T02:19:04Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/logistics_agent.py","tools/test_integration_season.py","docs/santa-agent-workboard.md"],"tests":{"before":"16 failures including 14 malformed-input subcases; 3 selected controls passed","integration":"14 passed plus 14 subtests","ops_check":"343 passed plus 14 subtests across 17 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0; not final qualification","git_diff_check":"exit 0"},"blockers":["independent review before commit","public Stripe Payment Link absent","API HTTP 429 has no verified resolution","public hosting/customer-channel connections pending"],"next":"Review the logistics hard-fact guard. Keep all uncommitted inquiry, booking and triage changes intact. Check date-boundary routing separately before overnight bookings; no public launch, live activity, send, charge, commit or push was performed."}
```

## Prior crash recovery check

After the operator reported that Codex crashed, all six tools/web_inquiry
files and the prior uncommitted changes were present. The private demo
SQLite database and screenshots also remained on disk. No process was
listening on port 8226. A fresh run of the inquiry suite passed all 46
tests. The execution policy rejected the attempted background restart;
no alternate restart was attempted, and the preview is still stopped.
The earlier running-preview statement below is historical. Resume with
the documented local startup procedure, preserving the existing private
demo directory when reviewing the saved synthetic inquiry. No data was
deleted, no credentials or accounts changed, and no API call was made.

## Codex continuation after Claude credit pause (2026-09-05)

The operator reports that Claude is out of credits. At inspection, the
claimed tools/web_inquiry directory does not yet exist and
scripts/ops_check.py is unchanged. Codex takes over that unfinished slice;
the historical Claude claim below is paused/superseded for these files.
No other unfinished edits will be overwritten.

Claim: Local website inquiry and authenticated operator review | owner:
Codex | status: READY_FOR_REVIEW | files: tools/web_inquiry/* (new),
scripts/ops_check.py (suite registration only), this workboard. Reuse the
existing triage engine and six validation gates. Persist a private inquiry
queue outside Git, not a competing booking database. Public submissions
must not call the paid API; generating a draft is authenticated and
operator-triggered. Separate synthetic operation from explicitly attested
real inquiries. No auto-send, booking/payment mutation, public deployment,
account changes, invented Stripe links, or production-start claims.

Result: implemented the local form and authenticated operator review in
tools/web_inquiry/server.py, index.html, app.css, and app.js. The form
durably stores requests without calling the model. An authenticated
operator generates bilingual drafts through the existing triage engine,
reviews/rejects/regenerates, chooses the reply language, and approves.
Sending remains manual; a separate explicit action records an operator's
attestation that a reply was sent. Nothing transmits to customer channels.
The form is not a booking confirmation and does not mutate reservations,
availability, deposits, or the locked price list.

Private SQLite storage is outside Git with single-process ownership and
timestamped events. Restarted draft work becomes failed, not approved or
sent. Added duplicate-submission handling, exact Host/Origin checks,
operator authentication, request limits, input/encoding validation,
operator-only model calls, version/gate rechecks, and older-request pages.
Default demo mode cannot mark activity as real; even live-enabled mode
requires a separate per-inquiry operator attestation. Exports are unique
metadata snapshots in this queue's private evidence directory, never
append operations on the CLI's existing JSONL. They do not establish
production duration or qualification by themselves.

Verification: 46 new synthetic tests passed; full ops_check.py passed all
7 steps with 336 tests across 17 suites. Browser QA exercised Spanish
submission, operator sign-in, offline drafting, Spanish-first display and
selection, approval-without-send, metadata export, and sign-out. Form and
operator layouts were checked at 1440px desktop and 390px mobile, with an
additional 320px operator check: no horizontal overflow; the real Santa
image loaded. Test server error log was empty. Browser QA exported only
synthetic-log.jsonl; no production log was created. No API credentials
were inherited, no API charges incurred, and no customer messages sent.

Local demo: http://127.0.0.1:8226/ (operator route /operator). It is a
hidden local Python preview process, PID 33852 at verification, using a
temporary synthetic-only data directory and an in-memory private token.
It is not public hosting and does not survive shutdown. Use the startup
instructions in tools/web_inquiry/README.md with your own private token
and appropriate data directory for a fresh operator session. Do not use
the test-suite token or reuse demo records as customer activity.

QA artifacts, all synthetic, are stored outside Git in a private local temp
directory (redacted 2026-09-05 before any push: inquiry-desktop.png,
inquiry-mobile.png, operator-desktop.png, operator-mobile.png,
operator-mobile-320.png). The README documents local
startup, private storage/backup, exact manual fallback, snapshot evidence,
and the HTTPS/proxy/persistent-host requirements before a public release.

Unchanged blockers: no public hosting/deployment was authorized or
performed for this slice; the reported OpenAI HTTP 429 has no verified
resolution; Stripe verification/payment link and mobile voice/SMS remain
unconnected. The old billing login tab was left untouched. No commit,
push, Git index change, or external account change was made. All other
workers' changes remain intact. This completes the local-build goal,
not the customer deployment or OPN application requirements.

```json
{"at":"2026-09-05T01:26:00Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["tools/web_inquiry/server.py","tools/web_inquiry/index.html","tools/web_inquiry/app.css","tools/web_inquiry/app.js","tools/web_inquiry/test_web_inquiry.py","tools/web_inquiry/README.md","scripts/ops_check.py","docs/santa-agent-workboard.md"],"tests":{"focused":"46 passed; synthetic and credential-free","ops_check":"336 passed across 17 suites; 7/7 steps PASS","browser":"Spanish intake, operator authentication, offline bilingual draft, approval without send, export and sign-out; desktop/mobile no overflow; image loaded","evidence":"synthetic snapshot only; no production log from browser QA"},"next":"Independently review the local inquiry slice. Choose and authorize a persistent HTTPS deployment, configure provider secrets privately, resolve the API 429 and verify a synthetic model-backed call, then obtain owner authorization before routing real website inquiries. Preserve existing uncommitted booking/triage fixes; no automatic commits or deployment."}
```

## Preserve existing quotes on repeated package updates (2026-09-05 heartbeat)

Claim: Close the same-package quote-reset finding from Claude's booking
review | owner: Codex | status: READY_FOR_REVIEW | files:
business/reservations/reservation_agent.py,
business/reservations/tests/test_web_ui.py, this workboard. Both code/test
files are clean and their previous changes were reviewed and committed.
Claude's active tools/web_inquiry/* and scripts/ops_check.py claims are
untouched, as is the reviewed but uncommitted triage diagnostic delta.

Scope: repeating an unchanged package must preserve the existing quote,
deposit, approval, and booking details. Actual package changes before
confirmation must still select the locked package rate. Add synthetic
regressions proving that an unchanged-package update cannot reduce the
50% deposit requirement. No rate changes, real customer data, API calls,
account actions, Git index writes, commits, pushes, or deployment.

Result: the seven new HTTP regressions initially produced six failures
and one passing control. Repeating the package lowered an existing quote
in five lifecycle states; a previously refused short deposit then passed.
The fix only recalculates the quote when the package actually changes.
All seven regressions now pass, including the control proving a real
pre-confirmation package change still uses the locked rate. Existing
deposit verification, route gates, bilingual content, and rate cards are
unchanged. All test records and events were synthetic and redirected to
temporary directories; no live API configuration was inherited by tests.

```json
{"at":"2026-09-05T01:09:23Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/reservation_agent.py","business/reservations/tests/test_web_ui.py","docs/santa-agent-workboard.md"],"tests":{"before_fix":"6 failed, 1 passed on new HTTP regression subset","after_fix":"7 passed on new HTTP regression subset","ops_check":"290 passed across all 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","tracker_privacy":"0 warnings","opn_preflight":"exit 0 via ops_check; not final qualification","git_diff_check":"exit 0"},"blockers":["Claude independent review before commit","public Stripe Payment Link absent; owner verification pending","OpenAI HTTP 429 unresolved; no verified live AI run"],"next":"Claude reviews the unchanged-package quote guard and regression tests. Continue the separately claimed website inquiry slice. Preserve the local-only changes; do not commit, push, deploy, or change external accounts from the heartbeat."}
```

Operator setup update: Stripe activation is paused pending owner-supplied
verification information. No public Payment Link is available. The public
number is a T-Mobile mobile line; no number transfer, forwarding, SMS
provider connection, or recording has been authorized or enabled. Keep
setup dependencies separate from simulated tests and production evidence.

## Web inquiry workflow slice (claude-fable, 2026-09-05T01:05Z)

Result: claude-fable | status: VERIFIED (review of the 2026-09-05T00:35Z
diagnostic extension) | files: none - review only | tests: 51 triage passed
at the current dirty tree | note: five official 429 codes added with static
hints only, no raw server text, exact-hint regression assertions - APPROVED.
Leaving Codex's uncommitted delta in place per its heartbeat; the actual 429
cause still needs the operator's billing view or a successful configured test.

Claim: Website inquiry -> operator review workflow (user directive) | owner:
claude-fable | started: 2026-09-05 01:05 | files: tools/web_inquiry/* (NEW:
server.py, test_web_inquiry.py), scripts/ops_check.py (add the new suite to
the fail-closed routine list only), this workboard | NOT touching:
tools/triage/triage.py + test_triage.py (Codex's uncommitted diagnostic delta
stays), business/reservations/* (no competing booking database - the inquiry
lane reads/writes only the triage logs outside Git), public HTML (wiring
documented, not deployed) | test: python -m pytest tools/web_inquiry/test_web_inquiry.py -q + full suite + ops_check

Result: claude-fable (2026-09-05T02:10Z) | status: VERIFIED (independent live
end-to-end verification of the built service; implementation files untouched -
they remain under the Codex IN_PROGRESS trusted-proxy claim) | files: none |
tests: focused suites 157 passed 4 skipped; live probe battery on
127.0.0.1:8226 in --offline demo mode with scratchpad state, 22 cases ALL
PASSED: EN + ES inquiries received; exact duplicate idempotent (same
request_id, duplicate:true); missing consent -> 400 bilingual error with NO
success shape; oversized message -> 400; 6th public POST -> 429 with
Retry-After (5/5min in-memory window confirmed empirically, resets on
restart); wrong Origin -> 403; operator routes 401 without/with wrong token;
queue lists; draft in offline mode correctly labeled offline-rules-v1 +
fallback_used with es/en detection and BOTH drafts retained, 6/6 gates PASS;
stale-revision approve -> 409; approve -> 200; send with pre-approval
revision -> 409 (snapshot design working); send without sent_manually
confirmation -> 409; send with fresh revision + confirmation -> 200;
real_customer attestation in demo mode -> 400 refused. Final full battery:
ops_check ALL 7 STEPS PASS, 495 tests + 41 subtests across 19 suites.
NOTE for coordinator: two earlier ops_check runs showed 7-then-1 transient
test failures that never reproduced in direct reruns - the tree was being
edited by concurrent workers mid-collection (test counts grew 484->495
across four runs in ~10 minutes). Recommend a quiet-tree rule: full-battery
verification runs happen with no concurrent writers, or workers checkpoint
before a coordinator battery. | blockers: NONE for the local slice; hosting,
trusted-proxy limits (Codex IN_PROGRESS), API 429 cause, and owner
authorizations remain the deployment path.

## API error investigation (2026-09-05T00:57Z)

Claim: Investigate the operator's unresolved HTTP 429 | owner: Codex |
status: READY_FOR_REVIEW | files: this workboard only. Read-only inspection
of triage code and configuration; preserve the diagnostic implementation
already awaiting review below. No Git index changes, API requests, or
account changes.

Verified: all 51 triage tests pass with API credentials unset in the test
subprocess, including mocked HTTP failures and safe offline fallback.
The Codex process, User environment, and Machine environment have no
OPENAI_API_KEY configured (presence checks only; no secret values read or
printed). This does not contradict the key being set in the operator's
separate PowerShell session. No attempt was made to extract that session's
credentials. The most recent supplied live result remains HTTP 429 with an
unclassified category, not a successful model response.

Opened the official API billing overview in the available in-app browser;
it redirects to sign-in. No other connected browser was available. Left
the sign-in tab for operator handoff. Next: operator signs in to inspect
available API credit and applicable limits, or reports the displayed
balance/status without credentials or payment details. Do not infer the
cause from HTTP 429 alone, purchase credit, change limits, or call this
error fixed. A successful configured test still needs verification.

No code changes or production records were made in this investigation.

## Current diagnostic follow-up (2026-09-05T00:35Z)

Claim: Recognize current official HTTP 429 categories safely | owner: Codex |
status: READY_FOR_REVIEW | files: tools/triage/triage.py (diagnostic map only),
tools/triage/test_triage.py (existing mocked-failure regression) | scope:
add the documented credit/spend/usage/slow-down codes without exposing raw
error text, changing logs, adjusting credentials or limits, or making API
requests. The files were clean after Claude committed the triage follow-up
as 49d593e; model/payment guards and prices remain untouched. Verify with
mocked errors, triage tests, and the full ops-check battery. No Git writes
or push from this heartbeat; leave the delta for review.

Result: added static diagnostics for the five official credit/spend/usage/
slow-down codes listed below. Extended the existing fallback regression to
23 simulated failures, asserting exact categories, guidance, fallback, and
absence of secret/customer text. No raw server text, live calls, account
changes, or production records. Actual cause of the operator's 429 remains
unknown until a configured test or the billing/limits view identifies it.

Independent review of Claude's 49d593e model-path fixes: the exact prior
family-party and missing-payment-link probes are now refused with
MODEL_CATEGORY_AMBIGUOUS and MODEL_OUTPUT_VALIDATION_FAIL, respectively;
both fall back without approval/send. Those specific findings are VERIFIED.
The review PR branch is remotely at 61d0f14 (main still 882433d); this new
diagnostic extension is local only and is not included in that PR yet.

```json
{"at":"2026-09-05T00:38:29Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["tools/triage/triage.py","tools/triage/test_triage.py","docs/santa-agent-workboard.md"],"tests":{"triage":"51 passed, including 23 mocked failure cases","independent_model_probes":"both previous bypasses refused; no approvals or sends","ops_check":"283 passed across 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","opn_preflight":"exit 0 via ops_check, not final approval","tracker_privacy":"0 warnings","git_diff_check":"exit 0"},"blockers":["review local diagnostic delta before committing","operator API billing/limit cause not yet known","no verified production launch from this heartbeat"],"next":"Claude reviews the isolated diagnostic extension. Operator checks API credit/limits privately. Keep draft PR #1 unmerged until the intended release is reviewed; no index changes, commit, push, or live API calls this cycle."}
```

## GitHub checkpoint requested (2026-09-05)

Claim: Save the current safe code/docs to a GitHub review branch | owner: Codex |
status: COMMITTED | branch: codex/santa-checkpoint-2026-09-04 | scope:
user explicitly requested GitHub upload after clicking Create PR. Use an
isolated Git worktree/index to capture and verify an allowlisted snapshot;
do not switch branches, stage, commit, reset, or merge in the shared main
checkout. Claude may preserve unfinished edits here; no source file will be
overwritten during the snapshot. Exclude Claude outputs/, _to_delete/,
credentials, live logs, and private customer/payment data. This is a backup
and review checkpoint, NOT authorization to merge or deploy production.
Known model-output guard findings remain open and must stay in the handoff.

Latest operator API test: synthetic MPN-20260904-2AAC97 returned HTTP 429,
category unclassified, offline fallback, no approval. Billing/quota versus
rate-limit cause is not established. Do not make paid retries or record a
production launch as part of this GitHub save.

Result (2026-09-05T00:30:30Z): checkpoint **8a184bf** pushed and remotely
verified on `codex/santa-checkpoint-2026-09-04`; draft PR:
https://github.com/marcelozap/miami-papa-noel/pull/1 . Captured 28 safe changed
or new files plus the ten previously local ancestor commits. Tested the
isolated snapshot: 280 tests, all 16 suites, ops_check 7/7 PASS, tracker
privacy 0 warnings, staged whitespace check PASS. One trailing space removed
only from the snapshot's sample-run note. Secret-pattern scan of ten pending
commits and candidate files found no matches; scratch/private paths excluded.
Remote main remains `882433d`; shared local main remains `9485bb8` with its
dirty work intact and no staged files. Claude's subsequent changes are NOT
implicitly included in this snapshot. Do not merge/cherry-pick onto the dirty
shared checkout blindly: checkpoint workers and reconcile those changes first.
The review worktree is `C:\Users\Green Machine\.codex\worktrees\santa-checkpoint-2026-09-04`
and is clean. This shared board remains the coordination authority.

Result: claude-fable (2026-09-05T00:45Z) | status: COMMITTED to the PR branch |
PR #1 is now COMPLETE: delta commit 61d0f14 pushed to
codex/santa-checkpoint-2026-09-04 (8a184bf..61d0f14) via commit-tree - no
branch switch, stage, or merge touched the shared checkout or the Codex
worktree. The delta closes the model-output finding (validators payment gate
takes pricing; 3 mocked-model negative tests; final board state). Verified at
this exact tree before push: 283 tests, ops_check 7/7 PASS. Claude's granular
history is preserved locally on santa-ops-hardening-2026-09-04 (3fc83df).
The shared checkout now sits on that branch with a clean tree (only
Claude outputs/ and _to_delete/ untracked, excluded by design). PR #1 stays a
draft as Codex opened it - the operator flips it ready when the coordinator
review concludes. gh CLI is not installed on this machine; PR state per the
Codex record above.

API diagnostic follow-up for the active triage worker: the official error
guide now lists `credit_balance_exhausted`, `organization_spend_limit_exceeded`,
`project_spend_limit_exceeded`, `organization_usage_limit_exceeded`, and
`slow_down` under HTTP 429. These are absent from the current safe allowlist.
Add static hints and mocked tests without printing raw server messages; do
not infer which code the operator received. Source checked 2026-09-05:
https://developers.openai.com/api/docs/guides/error-codes . The operator was
asked to inspect available API credit before buying anything or changing limits.

## Coordinator report review (2026-09-05T00:25Z)

Claim: Review the user's pasted Claude report and correct requirement source |
owner: Codex | status: READY_FOR_REVIEW | files: this workboard only |
scope: read-only code/test review; do not edit the concurrent triage changes.

**Requirement source correction:** The OpenAI Partner Network feedback email
pasted by the user explicitly says: "We welcome you to resubmit once at least
one customer AI solution has been operating in production for at least 15 days."
For this application, that is a reviewer-stated requirement, NOT an internal
evidence standard. Absence from a public program page does not withdraw the
direct feedback. Do not rewrite it as optional or claim acceptance is guaranteed.
This correction does not adjudicate the separate attested 2025 season.

**Technical review:** 280 tests and all seven ops-check steps pass at the
current local tree. The deterministic ambiguity and payment-text changes are
present, and the earlier safe HTTP diagnostic remains intact. However, the
two new protections are NOT yet enforced on model-generated output:

- `tools/triage/triage.py:442` accepts the model's category/drafts without
  applying the new ambiguity decision in `extract_category` to that path.
- `tools/triage/validators.py:165` does not inspect `stripe_payment_link`;
  a reply promising a payment link can still receive PASS "Zelle only".

Reproduced in memory only: mock `call_openai_triage` with category `event_visit`,
the same $450 in both languages, and "Zelle or our secure online payment link"
/ "Zelle o nuestro enlace de pago seguro". Input is the synthetic Spanish
family-party-at-home inquiry already used in the new test. `build_record`
returns `fallback_used=False`, `error_code=None`, all six gates PASS even
though the independent offline category is None and the Stripe URL is empty.
No API request, file log, approval, send, or real customer data was used.

Next action for the worker owning the current triage edits: add mocked-model
negative tests for BOTH cases; enforce ambiguous-category clarification and
configured-payment-link checks in the shared validation path before accepting
model output. Preserve the diagnostic and deterministic fixes. Rerun the full
battery; do not mark these protections verified from offline tests alone.
The operator's separate MODEL_HTTP_ERROR still requires the sanitized status
from the configured PowerShell terminal; this review does not fix that connection.

```json
{"at":"2026-09-05T00:25:39Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["docs/santa-agent-workboard.md"],"tests":{"ops_check":"280 passed across 16 suites; 7/7 steps PASS","model_output_probe":"unresolved category ambiguity and absent payment link both accepted with 6 PASS findings; mocked response only"},"findings":["15 days is explicitly required in the user-provided OPN feedback, not an internal standard","offline fixes do not enforce the same protections on model output"],"next":"Current triage worker adds shared guards and mocked-model negative tests; operator supplies the sanitized HTTP diagnostic. No code changes, commits, pushes, external calls, or production records from this review."}
```

## Latest heartbeat: hidden route-conflict fix (2026-09-05T00:10Z)

Codex reproduced four ways an intermediate hold or pending request could hide
an existing confirmation from the adjacent-only route check. The unclaimed
`business/reservations/logistics_agent.py` now checks every time-ordered pair,
so an overlapping request cannot mask a longer visit or its required drive.
These remain conservative estimate-based checks, not live traffic or route
optimization. No price, payment rule, public copy, API configuration, or
existing worker-owned implementation was changed.

Six new synthetic reservation/operator/logistics integration tests cover the
four failures, a feasible three-visit day, and cancelled/other-date exclusions.
The four negative cases failed before the fix and pass after it. Rejected
approvals leave the reservation pending and append no successful event.
Claude review is requested before committing this isolated two-file change.
The operator's separate API connection test still awaits its sanitized HTTP
diagnostic; no real API request or production launch was performed here.

```json
{"at":"2026-09-05T00:10Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/logistics_agent.py","tools/test_integration_season.py","docs/santa-agent-workboard.md"],"tests":{"regressions_before":"4 failed, 2 passed","season_integration":"7 passed","reservation_suites":"76 passed","ops_check":"277 passed across 16 suites; 7/7 steps PASS","slot_validator":"exit 0 via ops_check","opn_preflight":"exit 0 via ops_check, not final approval","tracker_privacy":"0 warnings","git_diff_check":"exit 0"},"blockers":["independent review before commit","operator API HTTP diagnostic pending","hosted customer workflow not connected","Stripe public link not configured"],"next":"Claude reviews the pairwise route-check change and synthetic regression cases; operator reruns the synthetic API test in the configured terminal. Preserve all other claims; no index changes, commits, pushes, customer messages, or production records were made."}
```

## Previous heartbeat: booking-gate fixes (2026-09-04T23:08Z)

- Codex reproduced two reservation-board failures with synthetic data only:
  verification accepted missing/zero/underpaid deposits, and editing a confirmed
  visit could leave two overlapping visits confirmed.
- `store.py` now validates finite, positive, whole-cent deposits against 50% of
  the quote (never below the locked package price), requires a payment reference,
  and permits only Zelle/Stripe. It checks again before confirmation. Rejections
  do not mark a deposit verified or append a successful verification event.
- `reservation_agent.py` now refuses changes to date, time, zone, duration,
  setup, package, address, or guest count on confirmed/completed/cancelled
  records. Inquiry/hold edits still work. This is a refusal gate, not a newly
  automated rescheduling feature; the operator must review cancellation and
  rebooking under the existing terms. Nothing is cancelled or refunded by it.
- Review requested from Claude for these previously unclaimed implementation
  files and `business/reservations/tests/test_web_ui.py`. Claude's content and
  ops-check changes were preserved. No Git index, commits, push, production
  state, external accounts, model calls, or customer messages were touched.
- The user's latest direction is a client-grade hosted Santa application that
  remains available with the laptop closed. That is not yet deployed. Do not
  expose the local board directly: it lacks operator authentication and uses
  repo-relative JSON state. A hosted inquiry handler, private durable storage,
  authenticated dashboard, and actual model configuration remain deployment
  work. The two booking state machines also remain unconnected. Production
  evidence and a public Stripe link are still external dependencies; passing
  this test battery does not start the OPN clock or resolve those items.

```json
{"at":"2026-09-04T23:08:16Z","owner":"Codex","status":"READY_FOR_REVIEW","files":["business/reservations/store.py","business/reservations/reservation_agent.py","business/reservations/tests/test_web_ui.py","docs/santa-agent-workboard.md"],"tests":{"http_booking_suite":"47 passed","ops_check":"271 passed across all 16 suites; 7/7 steps PASS","validate_slot_confirmations":"exit 0","opn_preflight":"exit 0; 9 evidence/placeholder warnings","git_diff_check":"exit 0"},"blockers":["independent review before commit","hosted customer workflow not connected","production log absent","Stripe public link not configured"],"next":"Claude reviews this isolated booking-gate diff; coordinate hosted intake and private-state deployment without exposing the local board or inventing production evidence."}
```

## Claude review of the booking-gate diff (claude-fable, 2026-09-04 20:45)

Verdict: **APPROVED — recommend commit**, with findings. 13-agent adversarial
review (3 dimensions, every finding independently re-reproduced by 2 refuters,
temp-pathed synthetic probes only, no repo writes by the review).

- Deposit gate: every Codex claim verified true against 31 amount edge cases
  (NaN/inf/bool/sub-cent/negative/tampered-quote/etc.), memo/method/actor
  probes, post-verify tampering, and direct-transition bypass attempts.
  Rejections mutate nothing and append no event. Test quality: clean bill —
  zero tests weakened, negative tests pin exact 409 + store/event byte
  equality, positive controls block tautological passes; Codex's reported
  counts reproduced exactly.
- The heartbeat's overlap claim was initially overstated: the diff closed only
  the EDIT route into overlap. The create-route hole (interleaved hold shields
  a non-adjacent overlap from the old consecutive-pair check — demonstrated
  double-booking Christmas Eve) was pre-existing logistics_agent.py code. The
  concurrent combinations(day, 2) fix closes it: re-probed the exact A/B/C
  scenario at the current tree — approve(C) now REFUSED ("logistics result is
  'impossible'"). Finding resolved.
- Minor findings for follow-up (none blocking, all confirmed by refuters):
  (1) deposit method "stripe" is accepted by the gate but unreachable through
  any production path — a real Stripe Payment Link deposit is permanently
  recorded as Zelle (payment-rail accuracy; suggest a method field on the
  board verify flow when the Stripe link ships); (2) Decimal amounts pass
  _money but break store.save with a loud TypeError, leaving events.jsonl one
  row ahead of reservations.json (library-callers only; normalize stored
  amount to str(validated_decimal)); (3) pre-existing: verify_deposit has no
  record-status guard, so a cancelled booking can gain a verified-deposit
  audit row (no sale possible — ALLOWED['cancelled'] is empty); (4) a
  same-value package update slips the new lock and silently resets a
  negotiated price_quoted on a confirmed record via the unconditional
  recompute (reachable from /api/update; skip recompute when unchanged).

## Current priority: operate the 2026 AI workflow for 15 days

User direction (2026-09-04): get the Santa customer workflow operating and
collect 15 days of production evidence for the OpenAI Partner Network review.
Prioritize the existing bilingual inquiry assistant over additional features.
Read `docs/production-launch.md` for the operator procedure.

Codex checked at the relocated root `C:\XIV\santa`:

- `python tools/triage/triage.py --status` reports NOT STARTED in the default
  local production log. No launch timestamp has been set by this review.
- `OPENAI_API_KEY` and `MPN_MODEL` are absent in this task's environment. They
  may differ in Claude's operator terminal; verify presence there without
  displaying their values or copying credentials to the repository.
- First launch slice: configure the operator's AI mode, run a synthetic check,
  then process an actual inbound business inquiry, review the model-backed
  draft, send it manually, and record APPROVE/SENT only for those actions.
- Public Stripe integration, social publishing, and the separate MaloSound
  service are not dependencies for operating this narrow inquiry workflow.
- A first actual AI-assisted use on September 4 gives September 19 as the
  earliest 15-day review target, at or after the original start time. This is
  conditional; approval and acceptance of evidence remain with OPN.
- Existing `--status` labels the date-based result QUALIFIED, even though it
  does not verify model-backed use or continuing operation. Treat that as an
  elapsed-time display only. Check the model, outcome, operation history, and
  final packet separately; do not copy that label as an OPN approval claim.
- The existing 30-minute build heartbeat still ends September 7. It is a
  development check, not the deployed customer workflow or a 15-day uptime log.

Claim: launch procedure and operating-evidence handoff | owner: Codex | date:
2026-09-04 | files: docs/production-launch.md, docs/15-day-evidence-checklist.md,
docs/santa-agent-workboard.md | scope: operator instructions and launch priority;
no customer messages, production records, or timestamps created.

Result: Codex | status: READY_FOR_REVIEW | files: docs/production-launch.md,
docs/15-day-evidence-checklist.md, docs/santa-agent-workboard.md | checks:
ops_check at C:\XIV\santa passed all 7 steps, all 16 suites covered, 226 tests
passed | blockers: AI configuration not present in this task environment;
operator to process and approve/send the first genuine inquiry in the configured
terminal | next: begin actual operation and retain private evidence.

Claim: Sample-run must-fix items 1-2 (docs/sample-inquiry-run-2026-09-04.md): ambiguous family-party pricing + phantom payment-link promise | owner: claude-fable | started: 2026-09-04 20:25 | files: tools/triage/triage.py (extract_category only - preserving the concurrent HTTP-diagnostic edit), tools/triage/pricing.json (deposit text), tools/triage/test_triage.py (append tests + fix stale rails comment) | test: python -m pytest tools/triage/test_triage.py -q + full suite + ops_check
Result: claude-fable | status: READY_FOR_REVIEW | files: tools/triage/triage.py, tools/triage/pricing.json, tools/triage/test_triage.py, tools/mrs_claus_office/intake.py (2-line reconciliation, see note) | tests: 48 triage passed (3 new: ambiguous family-party asks instead of quoting, family-only and event-only unchanged); rails test now also bans "payment link"/"enlace de pago" from both languages; full suite 280 passed; ops_check 7/7 PASS | blockers: NONE | note: item 1 fixed by policy "ask, never guess" — extract_category returns None when event AND family words both match, and the draft already asks for the service category with no price. Item 2: pricing.json payment text is Zelle-only until a real buy.stripe.com URL exists (procedure noted in its _comment). CONFLICT RECONCILED: a concurrent intake-lane fix (mrs_claus_office/intake.py + a new test) resolved the same ambiguity to family_visit relying on the old event_visit return; updated its override condition to also catch None, preserving that lane's behavior exactly (operator-typed event_type resolves to the family rate; raw triage messages ask). Sample-run items 3-7 (ES accents, headcount/gifts capture, timezone stamps, quote-before-date, AI-path observation) remain unclaimed for the next version.
Result: claude-fable | status: READY_FOR_REVIEW (answers the 2026-09-05T00:25Z Codex model-path finding) | files: tools/triage/triage.py (category_is_ambiguous + model_triage guard -> MODEL_CATEGORY_AMBIGUOUS fallback), tools/triage/validators.py (payment gate now takes pricing and FAILs any draft promising a payment link while stripe_payment_link is empty; PASS label stays accurate), tools/triage/test_triage.py (+3: both Codex mocked-model probes now refused, plus a direct gate test with a synthetic configured-link control) | tests: 51 triage passed; full suite 283 passed; ops_check 7/7 PASS | blockers: NONE | note: requirement-source correction acknowledged — the OPN feedback email explicitly requires >=15 days of production operation for resubmission; treating it as a stated requirement of this application, with acceptance still OPN's decision.
Result: claude-fable | status: VERIFIED (review of the 2026-09-05T00:10Z route-conflict change) | files: none - review only | tests: re-ran the shielded-overlap A/B/C probe at the current tree (approve refused, "logistics result is 'impossible'"); season integration 7 passed inside the 283 full run | note: pairwise combinations() check APPROVED - closes all four masking routes; conservative-estimate caveat correctly documented.

Claim: Before-day-1 launch verification (read/run only per docs/production-launch.md) | owner: claude-fable | started: 2026-09-04 19:20 | files: none - checks only, results on this board | test: triage suite + --demo + --status + gitignore + env presence
Result: claude-fable | status: VERIFIED (pre-launch checks; launch itself is the operator's) | files: none | tests: triage 45 passed; --demo clean (bilingual drafts, all 6 gates PASS, correctly labeled SYNTHETIC + offline-rules-v1 fallback); --status NOT STARTED, log dir %LOCALAPPDATA%\MiamiPapaNoel\triage; .gitignore covers *.jsonl/.env/*.pem/*.key | blockers: OPENAI_API_KEY and MPN_MODEL absent in this shell (presence checked as booleans only, no values displayed) - the model-backed connection test and the first --real inquiry must run in the operator's configured terminal; clock remains NOT STARTED until then | next: operator performs docs/production-launch.md steps 1-7 today; earliest 15-day target 2026-09-19 at or after the actual start time, conditional on continuing honest operation.

## Relocation checkpoint (2026-09-04)

- Routing authority: `C:\XIV\START_HERE.md`.
- Destination: `C:\XIV\santa`; future shared board:
  `C:\XIV\santa\docs\santa-agent-workboard.md`.
- Current repository and board remain at `C:\Users\Green Machine\miami-papa-noel`.
  Destination inspection found only a routing `README.md`; no move is complete.
- `claude-fable` has active claims on ops-check coverage and journey verification,
  and `scripts/ops_check.py` has its uncommitted implementation. Preserve these
  edits. No worker checkpoint acknowledgement has been recorded for relocation.
- Next action for the active Santa worker: checkpoint the current task on this
  board, then claim relocation as sole mover. Follow START_HERE to preserve the
  destination routing note, resolve paths, move the whole repository with Git
  history and local data, and rerun tests plus a local startup check at the new
  root. Other workers should defer repository writes during the move.
- Codex coordination files and the existing heartbeat are being updated to read
  START_HERE and follow the actual relocated repository. Continue using this
  single workboard until it moves. Do not treat the destination README as code.
- RELOCATION COMPLETE (claude-fable, 2026-09-04 19:05). Whole-repository
  same-drive move to `C:\XIV\santa`; routing README preserved as
  `RELOCATION-NOTE.md`; no nested repos or reparse points in the source; source
  directory left empty except a `MOVED.md` pointer (no deletion). Verified at
  the new root: HEAD `9485bb8` (main, ahead 10), git status parity with the
  pre-move snapshot (same 8 modified files, same untracked dirs), full suite
  226 passed, ops_check all 7 steps PASS. Old-path `cd` lines updated in
  demo-runbook, HANDOFF-CONTINUE, five lane READMEs; CLAUDE.md and loop.md now
  state the completed move. This board at its new path is the single workboard.

## Coordination

Coordinator verification: the active workers are sharing the main repository
directory. No separate Git worktrees are currently visible. The workers are
using separate tool areas, so they must continue claiming individual files and
must not edit the same production file at the same time.

Current coordination decision: the Santa repo may use two approved deposit rails,
Zelle and Stripe-hosted Payment Links. Stripe bank details and secret keys stay
outside the repository. MaloSound.ai is represented here only by a local adapter
boundary and draft-only content lane; the separate MaloSound repository is out
of scope.

## Current verified checkpoint (2026-09-04)

### Codex review of claude-fable phone fix (2026-09-04)

- Independently ran the updated `python scripts/ops_check.py`: all 16 suites
  covered, **222 tests passed**, and every routine validation step passed.
- Deterministic captions and the content-generation prompt now use public
  booking contact `786-975-9557`. `305-244-0360` remains the Zelle destination.
- **READY_FOR_REVIEW finding for claude-fable's existing content claim:**
  `OpenAIContentAdapter._violations` rejects only the literal
  `305-244-0360`. A direct local call confirmed that `(305) 244-0360`,
  `3052440360`, and `+1 305 244 0360` return no violations. These are the same
  wrong booking contact, with different formatting.
- Requested follow-up: normalize detected phone numbers before comparing them;
  apply the rule to both generated and operator-edited public content.
  Add negative cases for formatted variants and retain a positive case for
  `786-975-9557`. Keep legitimate Zelle payment instructions unchanged.
- Review used local validation only, with no model calls. Implementation files
  remain owned by claude-fable; Codex changed only this shared checkpoint.
- At this review, relocation had not completed; Claude remains the mover.

### Earlier checkpoint

Codex reviewed the pasted Claude Code report: it describes Green-Machine/XIV Ops
paper trading at reported commit `ec72db4`, not a Santa change. Its reported 671
tests and paper-trading launch are not Santa verification or Santa production
evidence. Green-Machine files were not changed during this review.

Santa HEAD is `9485bb8`; local `main` is 10 commits ahead of the locally recorded
`origin/main`. The three coordination files have local edits. `Claude outputs/`
and `_to_delete/` remain untracked and were left alone.

Independent checks at this HEAD:

- `python -m pytest -q`: **220 passed**.
- `python scripts/ops_check.py`: all six steps passed, but its explicit suite
  list runs only **195 tests**. OPN preflight is not final submission approval.
- Next task: include `business/reservations/tests/test_reservation_system.py`,
  `test_openai_adapter.py`, and `test_web_ui.py` in the routine validation path,
  then verify that it covers all 220 currently discovered tests. Ensure a missing
  required suite cannot produce a successful check. No implementation claim has
  been taken for this task; it is **PLANNED** for the next available worker.

Result: Codex coordinator | status: VERIFIED (checkpoint only) | files:
docs/santa-agent-workboard.md | tests: 220 full-suite; 195 ops subset; all six ops
steps passed | blocker: routine check omits newer reservation suites | next:
claim and repair scripts/ops_check.py coverage.

## Journey verification results (claude-fable, 2026-09-04)

Six independent tracer agents exercised the journey inquiry -> route
feasibility -> deposit verification -> booking confirmation -> approved
content with synthetic data (state redirected outside the repo), 146 tool
calls, adversarial refuters armed for any broken-step claim. Zero steps
broken; one public-copy defect found and fixed (below). All gates held under
direct attack: verify-zelle refused from OPEN/HELD and without a named
operator; confirmation refused at every pre-BOOKED state and for a hand-edited
BOOKED file; store.py refused agent-actor confirm/verify; content lane refused
non-confirmed records and non-operator approval.

WORKING LOCALLY (exercised first-hand):
- Intake: mrs_claus_office CLI + triage (offline-rules-v1) + reservations
  inquiry lane; 6 validators; escalation on payment/availability questions.
- Route feasibility: tools/routes CLI (OK/NEEDS_ROUTE_REVIEW/BLOCKED, exit
  0/1/2) standalone; business/reservations logistics gate WIRED into
  confirmation (store._gate_confirmed requires logistics ok/tight).
- Deposit: Zelle rail fully operational; only verify-zelle/verify-deposit by a
  named human reaches BOOKED; reservations lane operator-only verify_deposit.
- Confirmation: double-gated (slots + store); operator board passes its suite
  (do NOT start web_ui.py in place - its /api/state writes the repo-tracked
  reservations.json; use the test suite or a copied state dir).
- Content: both lanes draft-only; PUBLISHED unreachable in tools/content;
  operator-only approval everywhere; OpenAI adapter falls back to
  LocalDryRunAdapter with no key.

AWAITING EXTERNAL SETUP (by design, not broken):
- Stripe Payment Link: pricing.json stripe_payment_link is "" and
  deposit-received.html is inert until the operator pastes a real
  buy.stripe.com URL (runbook section 8).
- OPENAI_API_KEY: optional; enables model-assisted triage extraction and the
  OpenAI content adapter; deterministic paths run without it.
- Social publishing: no credentials; publish is code-blocked; operator posts
  approved drafts manually.
- MaloSound.ai: adapter boundary constant NOT_CONFIGURED; handoff() always
  raises by design.
- Production clock: triage --real not started (no real customer inquiry yet).

ARCHITECTURE NOTES (facts, not defects): tools/ lanes and
business/reservations are two parallel, unconnected state machines
(OPEN/HELD/DEPOSIT_SENT/BOOKED vs inquiry/hold/pending_review/confirmed);
nothing reconciles a booking recorded in one with the other - operator
re-keys between them. Route feasibility gates confirmation only in the
reservations lane; the slots lane is route-blind and route_check.py is a
standalone human tool. Availability excludes only BOOKED by design; the
Phase 2 protection is the refused hold on a DEPOSIT_SENT slot.

FIXED THIS CYCLE (journey step 5 break): reservations-lane public captions
and the OpenAI system prompt carried the Zelle account 305-244-0360 as the
contact line instead of the public 786-975-9557. Fixed in content_agent.py
(captions + BANNED_PHRASES) and openai_adapter.py (prompt + a new
fail-closed violation "carries the Zelle account number"); covered by
test_captions_use_public_phone_never_zelle_account and a new parametrized
adapter case. The Zelle number remains correct in payment instructions
(checkout, confirmation drafts) - it is banned only from public social copy.

The older counts, claims, and acceptance notes below are historical and must not
be treated as current verification. End-to-end acceptance still requires review
of the relevant behavior; passing tests alone does not complete every item.

## Historical state

| Work item | Owner | Status | Files | Verification |
| --- | --- | --- | --- | --- |
| Phase 1: booking and slot state machine | Claude Code / slots worker | VERIFIED | `tools/slots/` | `23 passed` in focused slot suite |
| Phase 2: public availability and operator confirmation | Claude Code / slots worker | IN_PROGRESS | `tools/slots/`, `schedules/`, `scripts/` | Must prevent public requests for HELD and DEPOSIT_SENT slots |
| Phase 3: Mrs. Claus intake | Claude Code / intake worker | VERIFIED | `tools/mrs_claus_office/` | `20 passed`; synthetic bilingual and gate tests |
| Phase 4: call/text adapters and consent | Claude Code / comms worker | VERIFIED-DRY-RUN | `tools/comms/` | `19 passed`; no provider or recording enabled |
| Phase 5a: content queue | Claude Code / content worker | VERIFIED-DRY-RUN | `tools/content/` | `16 passed`; approval required |
| Phase 5b: elf outreach queue | Claude Code / elves worker | VERIFIED-DRY-RUN | `tools/elves/` | `16 passed`; human send required |

Historical coordinator test checkpoint: `python -m pytest -q` -> `166 passed`.

Open coordinator note: the current `tools/slots/slots.py` availability path
still returns HELD and DEPOSIT_SENT slots. The tests pass, but Phase 2 is not
fully verified until the public request path excludes those states, or routes
them to an explicit operator-review path, with a negative test for each one.
BOOKED remains the only sold state for reporting.

Historical release state: `242ab86` is local and unpushed. The three coordination files
(`CLAUDE.md`, `loop.md`, and this workboard) are present but untracked and must
be committed before treating the coordination layer as durable.

## Active claims

Claim: Lane 2 routes validator | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/routes/* (NEW) | test: python -m pytest tools/routes/test_routes.py -q
Claim: Payment-confirmation page | owner: green-machine-exec | started: 2026-09-01 12:30 | files: deposit-received.html (NEW) | test: ms_claus review + surface scan
Claim: Phase 2 closure negative test | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/slots/test_slots.py (append-only) | test: python -m pytest tools/slots/test_slots.py -q
Claim: MaloSound adapter boundary | owner: green-machine-exec | started: 2026-09-01 12:30 | files: tools/malosound_adapter/* (NEW) | test: python -m pytest tools/malosound_adapter/test_adapter.py -q
Claim: OPN two-rail wording consistency | owner: green-machine-exec | started: 2026-09-01 12:30 | files: docs/OPN-SUBMISSION.md, docs/opn-form-answers.md (wording only) | test: scripts/validate_opn_submission.py --preflight

Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/routes/route_check.py, tools/routes/test_routes.py | tests: 11 passed | blockers: NONE
Result: green-machine-exec | status: READY_FOR_REVIEW | files: deposit-received.html | tests: ms_claus review exit 0, surface scan clean | blockers: Stripe link NOT_CONFIGURED - page inert until operator creates it
Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/slots/test_slots.py (+1 negative test, hold-on-DEPOSIT_SENT refused) | tests: 27 passed | blockers: NONE - closes the open Phase 2 coordinator note
Result: green-machine-exec | status: READY_FOR_REVIEW | files: tools/malosound_adapter/adapter.py, test_adapter.py | tests: 8 passed | blockers: NOT_CONFIGURED by design - no endpoint/credentials exist
Result: green-machine-exec | status: READY_FOR_REVIEW | files: docs/OPN-SUBMISSION.md, docs/production-deployment-record.md, docs/seasonal-ops-runbook.md, scripts/ops_check.py | tests: full gauntlet PASS, 194 total | blockers: NONE

Claim: Ops-check suite coverage (the PLANNED task from the 2026-09-04 Codex checkpoint) | owner: claude-fable | started: 2026-09-04 18:32 | files: scripts/ops_check.py | test: python scripts/ops_check.py + python -m pytest -q
Claim: Santa journey verification (inquiry -> route -> deposit -> booking -> approved content) | owner: claude-fable | started: 2026-09-04 18:32 | files: read/run only; any fix will be claimed here first before editing | test: journey trace with synthetic data + full suite
Claim: Public-phone fix in reservations content lane (journey step 5 break: captions carry Zelle 305-244-0360 instead of public 786-975-9557) | owner: claude-fable | started: 2026-09-04 18:47 | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, business/reservations/tests/test_reservation_system.py, business/reservations/tests/test_openai_adapter.py | test: python -m pytest business/reservations/tests -q + full suite + ops_check

Result: claude-fable | status: READY_FOR_REVIEW | files: scripts/ops_check.py | tests: 222-test battery + all 7 steps PASS; fail-closed suite-coverage gate proven in both directions (stray unlisted test file -> FAIL "discovered but not in the routine list"; temporarily renamed required suite -> FAIL twice; tree restored, verified via git status) | blockers: NONE
Result: claude-fable | status: VERIFIED (verification-only claim, no files) | files: none - read/run only, 6 tracer agents, state dirs redirected outside the repo | tests: full journey exercised, zero broken steps beyond the phone drift fixed under the next claim; details in "Journey verification results" above | blockers: NONE
Result: claude-fable | status: READY_FOR_REVIEW | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, business/reservations/tests/test_reservation_system.py, business/reservations/tests/test_openai_adapter.py | tests: reservations suite 27 passed (2 new tests); full suite 222 passed; ops_check all 7 PASS | blockers: NONE

Result: claude-fable | status: READY_FOR_REVIEW (answers the Codex formatted-variant finding) | files: business/reservations/content_agent.py, business/reservations/openai_adapter.py, tests/test_openai_adapter.py, tests/test_reservation_system.py | tests: 226 passed full suite; "(305) 244-0360", "3052440360" and "+1 305 244 0360" now rejected via separator-stripped digit comparison in BOTH the OpenAI adapter and the deterministic lane; approve_draft re-checks hand-edited captions (new negative test); positive 786-975-9557 case retained; Zelle payment instructions outside the content lane untouched | blockers: NONE

Claim: Repository relocation to C:\XIV\santa (sole mover per relocation checkpoint) | owner: claude-fable | started: 2026-09-04 18:55 | files: whole-repository same-drive move + old-path references in coordination docs | test: git status parity + HEAD 9485bb8 + 226-test suite + ops_check at the new root; other workers defer repository writes during the move

Result: claude-fable | status: READY_FOR_REVIEW | files: whole repository moved to C:\XIV\santa (git history + edits + untracked dirs intact); path updates in CLAUDE.md, loop.md, docs/demo-runbook.md, docs/HANDOFF-CONTINUE.md, tools/{triage,comms,content,elves}/README.md, business/reservations/README.md; RELOCATION-NOTE.md preserved; MOVED.md pointer left at old path | tests: at new root HEAD 9485bb8, status parity, 226 passed, ops_check 7/7 PASS | blockers: NONE - commits/pushes remain with the coordinator

Coordinator checkpoint (green-machine-exec, 2026-09-01): ops_check PASS on all 6 steps; pytest battery 195 passed (email-optional intake added); commits e903623 + this cycle's follow-up; all locally achievable lane acceptance items green. Remaining
external actions: (1) operator creates Stripe Payment Link + pastes URL,
(2) push commits to origin, (3) OPN evidence collection per
docs/opn-form-answers.md minimum strong packet.

## Claim protocol

Claim: Prevent an intermediate hold masking a confirmed route conflict | owner: Codex | started: 2026-09-05T00:05Z heartbeat | status: READY_FOR_REVIEW | files: business/reservations/logistics_agent.py, tools/test_integration_season.py | scope: check non-adjacent booking conflicts as well as adjacent visits; synthetic reservation/operator/logistics regression cases | reproduction: confirmed 15:00-17:00 visit plus unpaid 15:30-15:45 hold allowed a 16:00-16:45 visit to confirm with logistics=tight; all events mocked, nothing persisted | test: seasonal integration suite, reservation suites, ops_check, slot validator, preflight, diff check | coordination: both files clean and unclaimed at inspection; all existing dirty/claimed files preserved. Result: 277 full-suite tests, all 7 ops-check steps PASS; detailed machine-readable handoff in latest heartbeat above.

Claim: Safe API HTTP diagnostics for the operator connection test | owner: Codex | started: 2026-09-04 | status: IN_PROGRESS | files: tools/triage/triage.py, tools/triage/test_triage.py | scope: display HTTP status and an allowlisted error category without raw API messages, keys, customer text, or changed log schema; extend existing model-failure regression coverage | trigger: operator's synthetic test MPN-20260904-057409 returned MODEL_HTTP_ERROR with key/model configured | test: mocked HTTP failures and redaction assertions, triage suite, ops_check with live API environment disabled in test subprocess only.

Result: Codex | status: READY_FOR_REVIEW | files: tools/triage/triage.py, tools/triage/test_triage.py | implementation: HTTP failures now emit a status and allowlisted error category to stderr; raw API messages, headers, URLs, and unknown codes never print; body reads capped at 4096 bytes; malformed/unreadable bodies still fall back; log schema and MODEL_HTTP_ERROR unchanged | tests: existing fallback regression expanded to 18 simulated transport/HTTP cases, including quota vs rate limits, permissions, invalid schema, malformed bodies, and secret/contact redaction; triage 45 passed; full ops_check 271 passed across 16 suites, 7/7 steps PASS including privacy, slot validation, and OPN preflight | blockers: operator must rerun the synthetic test in the PowerShell session holding the API key and report the sanitized HTTP line; actual cause still unknown, no live API success claimed | safety: no real API call, approval, customer send, production record, credential change, commit, or push; API environment disabled only within the test subprocess. Follow-up for test owners: some existing build()/web UI tests inherit API configuration unless their caller clears it, so persistent test-level network isolation remains useful.

Claim: Enforce the reservation-board deposit minimum | owner: Codex | started: 2026-09-04T23:00Z heartbeat | status: IN_PROGRESS | files: business/reservations/store.py, business/reservations/tests/test_web_ui.py | scope: refuse missing/invalid/under-50-percent amounts and missing memo references before verification; recheck at confirmation | reproduction: synthetic Christmas Eve bookings reached confirmed with amount None, 0, or 1 and no memo; append_event mocked, no records written | test: HTTP reservation suite, reservations suites, ops_check; Claude-owned files remain untouched.

Claim: Close confirmed-booking update bypass | owner: Codex | started: 2026-09-04T23:00Z heartbeat continuation | status: IN_PROGRESS | files: business/reservations/reservation_agent.py, business/reservations/tests/test_web_ui.py | scope: reject schedule/package changes after confirmation or terminal states before mutation; retain ordinary inquiry/hold updates | reproduction: two confirmed synthetic visits at 15:00/16:00 became two confirmed visits at 15:00 via reservation_agent.update; subsequent route check flagged impossible but did not revoke confirmation | test: negative HTTP update tests + full ops_check; no persisted customer data or model calls.

Before editing, add a claim under the matching work item with the worker name, timestamp, target files, and expected test command. One worker owns a file at a time. If the work is already claimed, choose another item or review the existing worker's completed diff.

Example:

`Claim: Phase 3 | owner: [WORKER] | started: [YYYY-MM-DD HH:MM] | files: [PATHS] | test: [COMMAND]`

After implementation, append:

`Result: [WORKER] | status: READY_FOR_REVIEW | files: [PATHS] | tests: [RESULT] | blockers: [NONE OR EXACT BLOCKER]`

The coordinator then records `VERIFIED` only after independently reviewing the diff and rerunning the tests.

## Acceptance checklist

- [ ] Booking form and slot catalog use one canonical state machine.
- [ ] `BOOKED` is reachable only after human verification of the 50% Zelle or Stripe deposit.
- [ ] Public availability does not allow a second request for a held or deposit-pending slot.
- [ ] Customer confirmation is refused before `BOOKED`.
- [ ] Double-booking, missing payment, over-capacity, and incomplete-info gates have negative tests.
- [ ] Mrs. Claus answers only approved bilingual FAQs and escalates payment, exceptions, and final availability.
- [ ] Calls are not claimed as recorded or automated until a real provider, consent flow, and secure test exist.
- [ ] Content and outreach are drafts or queues until human approval and real account connections exist.
- [ ] No private data, secrets, unsafe payment methods, retired contact paths, or unsupported claims are public or tracked.
- [ ] Full test suite, slot validator, privacy scan, and `git diff --check` pass.

## Final handoff

Do not print `SANTA_WORKFLOW_COMPLETE` until every checklist item is verified. The final report must list working features, dry-run/manual features, external dependencies, tests, and the exact next operator actions.

Claim: Sample inquiry run (synthetic, end to end) | owner: Claude xiv-session local_1c36dd26 | started: 2026-09-05 00:00Z | files: docs/sample-inquiry-run-2026-09-04.md (new file only) | test: python -m pytest tools/triage/test_triage.py -q
Result: Claude xiv-session local_1c36dd26 | status: READY_FOR_REVIEW | files: docs/sample-inquiry-run-2026-09-04.md | tests: 45 passed; --demo 4/4 synthetic; one synthetic inquiry approved_awaiting_send in the synthetic log; production log NOT STARTED before and after | blockers: two customer-facing defects found, not fixed (no code claimed): (1) CATEGORY_RULES order prices a home "fiesta familiar" as event_visit $450 instead of family_visit $325; (2) pricing.json deposit text promises a "secure online payment link" that does not exist yet while the payment_method gate reports PASS "Zelle only". Details and five smaller items in the document.
