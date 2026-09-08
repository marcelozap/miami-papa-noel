# Day One Operator Card — Marcelo

The shortest honest path to the first genuine AI-assisted customer reply,
using the inboxes you already have (786-975-9557 text/WhatsApp, Instagram,
santa@miamipapanoel.com). Nothing here requires hosting, Stripe, or a
phone integration. Full detail: docs/production-launch.md.

**Paid steps are not approved right now.** The owner has raised affordability
concerns. The rebuilt v2 spending controls passed coordinator review
(2026-09-05), but paid generation stays off by default and unapproved until
the owner explicitly opts in. Keep using manual/offline replies. This card
is a future procedure, not permission to spend or a claim that Day 1 began.

## Once, before the first inquiry

1. **Rotate the exposed API key** in the OpenAI dashboard (the test key
   appeared in chat and must be treated as burned). Never paste the new
   one into chat, files, or Git.
2. In the PowerShell window you will actually use:

   ```powershell
   Set-Location 'C:\XIV\santa'
   $secret = Read-Host 'New OpenAI API key' -AsSecureString
   $env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new('', $secret).Password
   Remove-Variable secret
   $env:MPN_MODEL = 'gpt-5.6-luna'
   $env:MPN_REVIEWER = 'Marcelo Zapata'
   ```

3. **One bounded synthetic test** through the real gated path (this is
   the step that verifies gpt-5.6-luna for Santa — the haiku did not):

   ```powershell
   python -B C:\XIV\santa\tools\triage\triage.py --check-model
   ```

   PASS = exit 0 and `MODEL CHECK PASSED`, with the selected model and
   all six gates passing. Review both languages. Exit 1 / NOT VERIFIED
   means the model path or sample checks failed; read the sanitized hint
   and do not retry repeatedly. This may consume API credit; the haiku
   success does not prove ongoing free access. No local inquiry log,
   approval or send is written. Never add `--real` to a test.

## Every genuine inquiry (the actual Day 1)

1. A real customer writes to one of the existing inboxes. Copy their
   message exactly.
2. Same terminal:

   ```powershell
   $inquiryFile = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\intake\inquiry.txt'
   python tools\triage\triage.py --real --channel whatsapp --reviewer 'Marcelo Zapata' --file $inquiryFile
   ```

   Put the genuine message in that private file outside Git before running
   the command. Channels: `instagram_dm`, `whatsapp`, `phone`, `web_form`,
   `email`, `referral`; use the true source.
3. Read both drafts and every gate. Type `APPROVE` only if you approve.
4. **You** send the reply from the actual inbox. Then answer the second
   prompt (`SENT`) so the send is recorded truthfully.
5. Check the actual record: real customer, non-fallback model, named
   reviewer, approval/send times and `approved_and_sent`. That is evidence
   of an operated model-assisted reply. Run
   `python tools\triage\triage.py --status` to see the first valid model-backed reviewed/sent record and
   its 15-full-day review target in UTC. Fallback and unsent records do not
   start this counter. It does not certify OPN acceptance or continuous
   operation. Never backdate the evidence. Quiet days remain quiet; never
   manufacture an inquiry.

## What Day 1 is NOT

No `--real` on tests. No public website change (the new queue is local
only). No Stripe link until a real one exists. No automated calls/texts.
A model success on synthetic input is progress, not customer evidence —
only step "Every genuine inquiry" creates Day 1, and OPN decides
acceptance, not this card.

## Spending controls (v2 - coordinator-VERIFIED 2026-09-05)

The rejected limiter was rebuilt: paid generation is now **off by default
even with a key** - nothing spends until you explicitly set a daily
allowance in the same terminal:

```powershell
$env:MPN_API_DAILY_CALL_CAP = '3'   # your explicit opt-in; unset/0 = no spending
```

The allowance is one shared atomic count across BOTH paid adapters and all
concurrent processes; it survives restarts, and any accounting failure
refuses to spend rather than resetting. `--demo` draws 4 from it,
`--check-model` and each inquiry draw 1. Inquiries over 6000 characters
and responses over the token bound are never sent/accepted.

Still true and unchanged: this caps calls and tokens, **not dollars**.
No provider-side hard cutoff has been verified for this account, and
synthetic data is not free usage. The coordinator re-review passed
2026-09-05; paid steps still remain unapproved until you authorize them.
