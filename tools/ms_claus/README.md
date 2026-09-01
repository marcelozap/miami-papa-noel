# Ms. Claus local review agent

Ms. Claus is the local structure and release-review agent for Miami Papa Noel. It scans the deployed root HTML pages and reports one human-approved next change. It does not send messages, edit files, call customers, touch email/DNS/Vercel, or connect to a bank.

The default mode is offline and uses only Python's standard library:

```powershell
python tools\ms_claus\ms_claus.py
```

For a release check that can be used by another local workflow:

```powershell
python tools\ms_claus\ms_claus.py --json --strict
```

The review checks public contact-number consistency, preserves `305-244-0360` as the Zelle destination, blocks unapproved payment methods, flags insurance wording for verification, and checks that the booking requirements are visible in English and Spanish.

## Manual fallback

1. Open `checkout.html` and `thank-you.html` locally.
2. Confirm public calls, texts, and WhatsApp use `786-975-9557`.
3. Confirm Zelle still points to `305-244-0360`.
4. Confirm the client has provided the date, time, address or area, chair, air conditioning, designated gift/photo adult, and parking within 100 feet before a booking is confirmed.
5. Have the operator approve any customer-facing change before publishing.
