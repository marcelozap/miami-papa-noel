# Santa: Handle an Inquiry

## Use it now without API charges

Texts to 786-975-9557 arrive on the existing phone. Mrs. Claus does not
answer that number automatically. You read the message, prepare a reply,
review it, and send it from your normal inbox.

In the PowerShell window used for Santa, explicitly keep paid calls off:

```powershell
Set-Location 'C:\XIV\santa'
$env:MPN_API_DAILY_CALL_CAP = '0'
```

Put the customer's actual message in a private text file outside this
repository. For example, use your existing private intake folder, then run:

```powershell
$inquiryFile = Join-Path $env:LOCALAPPDATA 'MiamiPapaNoel\intake\inquiry.txt'
python -B tools\triage\triage.py --real --channel whatsapp --reviewer 'Marcelo Zapata' --file $inquiryFile
```

Use the actual source channel: whatsapp, instagram_dm, phone, web_form,
email, or referral. The file must exist before running the command.

1. Read the English and Spanish drafts and all six checks.
2. Check availability and travel time yourself. Templates do not reserve dates.
3. Approve only a correct reply. Send it yourself from the customer's inbox.
4. Type SENT only after actually sending it. Never use --real for test data.

No automatic texts, calls, posts, payments, or customer sends occur here.
These local template replies make no OpenAI API request. Existing phone,
website, and computer costs are assumed covered; this is not a promise that
future hosting or phone automation has no service charges.

## Paid drafting remains off

The new estimated-cost guard requires a private pricing/budget policy as
well as a positive call allowance. No daily amount has been selected or
authorized. Do not add credits or enable calls just to follow this card.

With approval later, an engineer verifies the selected model's current
official prices, creates the private policy, and tests the configured path
once within the agreed allowance. The exposed chat key must be replaced.
Never paste API keys or bank details into this guide, Git, or chat.

Generate, regenerate, --check-model, each of the four --demo inquiries, and
content generation can cost money when enabled. Visiting the site, queueing
an inquiry, reviewing drafts, and --status do not themselves call the model.

The guard conservatively reserves an estimated amount before dispatch.
It retains that amount after success, rejection, timeout, or crash. A full
allowance, invalid/stale pricing, unsupported payload, or accounting error
refuses the request. There is no automatic retry. It is NOT a provider
billing guarantee or an account-wide limit covering other applications.

## Check evidence without spending

```powershell
python -B tools\triage\triage.py --status
```

Offline replies and synthetic tests do not start the model-backed evidence
counter. A genuine model-backed, reviewed-and-sent customer reply can start
the local evidence record. The displayed 15-full-day UTC target does not
certify continuous production operation or OpenAI Partner Network acceptance.

## Engineer Notes: Cost Policy

Both adapters use tools/triage/spend_guard.py and the same absolute private
MPN_API_QUOTA_DIR (default: LOCALAPPDATA\MiamiPapaNoel\api-quota).
MPN_API_COST_POLICY points to an absolute JSON path outside the repository.
No policy file is supplied or activated by this change.

Required policy fields: daily_cents (positive decimal string), verified_on
(UTC YYYY-MM-DD, at most seven days old), and models. Each exact model ID
maps to input_usd_per_million, output_usd_per_million (positive decimal
strings), and source (official https://developers.openai.com/ pricing URL).
The source/date are operator attestations, not an automatic web verification.
Do not invent rates or use the synthetic test fixture prices for deployment.

Accounting uses SQLite BEGIN IMMEDIATE and durable commit before dispatch.
Same-day budget changes refuse requests rather than silently raising the
allowance. Input estimate covers the full serialized UTF-8 text envelope
(instructions and schema included), plus 4096 protocol tokens, with 25%
input-rate headroom. Maximum output includes the endpoint's configured token
limit; payloads over 64 KiB, output over 4096 tokens, and tools/media refuse.
This deliberately conservative estimate may stop drafts earlier than actual
billing would. No unused reservation is released. Call slots may also be
consumed by a later monetary refusal; neither counter automatically retries.

Use one shared private directory and policy across both adapters/processes.
Do not delete accounting files, change directories, or run older unguarded
copies to restore allowance. Separate machines/users/directories, tampering,
provider pricing changes, or costs outside these two adapters are not covered.
At midnight UTC the next day's allowance becomes available; two daily
allowances could be used close together across midnight, not a rolling 24h cap.
