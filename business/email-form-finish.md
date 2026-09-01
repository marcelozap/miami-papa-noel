# Email + Booking Form Verification

The business email is now hosted in Google Workspace and the domain is verified.
Use this runbook to verify the complete website-to-inbox path.

## Current Setup

- Business inbox: `santa@miamipapanoel.com`
- Domain: `miamipapanoel.com`
- Website: `https://miamipapanoel.com`
- Booking form: `https://miamipapanoel.com/book`
- Form destination: `https://formsubmit.co/santa@miamipapanoel.com`
- Backup contact: phone/text/WhatsApp at `786-975-9557`

The `santa@` address is a separate Google Workspace user. Do not create any
additional accounts for this verification.

## Verify Gmail

1. Sign in to Gmail as `santa@miamipapanoel.com`.
2. Send a test message to a separate outside inbox.
3. Reply to the test from that outside inbox.
4. Confirm that both messages appear in the Santa inbox.
5. Add the business signature after the test succeeds.

## Activate FormSubmit

FormSubmit requires a one-time activation email for the receiving address.

1. Open `https://miamipapanoel.com/book?source=formsubmit-test`.
2. Submit an obvious test request using non-customer details.
3. Open `santa@miamipapanoel.com` and find the FormSubmit activation email.
4. Click the activation link.
5. Submit the test form again.
6. Confirm the request arrives in the Santa inbox with the name, phone, date,
   city, visit option, celebration type, lead source, and gift details.

Do not use a real customer's private information for the activation test.

## Public Contact Update

After the send, receive, and FormSubmit tests pass, use this address in the
website, Google Business Profile, social profiles, and outreach:

`santa@miamipapanoel.com`

Keep the booking form and phone number visible as additional paths. Do not
publish a personal Gmail or Hotmail address.

## DNS Guardrails

- Do not move nameservers or change the website's Vercel records.
- Add only the verification, MX, SPF, DKIM, and DMARC records supplied by
  Google Workspace.
- Monitor the old mail service for up to 24 hours while DNS changes propagate.
- Do not guess DNS values.

## Completion Evidence

Keep the following outside Git:

- Screenshot or exported confirmation that the domain is verified.
- A sent and received test message.
- A successful FormSubmit test.

Never commit customer names, phone numbers, email addresses, street addresses,
payment memos, or message bodies to the repository.
