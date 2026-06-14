# Email + Booking Form Finish

This is the last operational step before the booking form is fully automatic.

## Tonight Temporary Setup

To get as much working as possible tonight, the live booking form and email-request fallback are temporarily routed to:

`rubiosally@hotmail.com`

This lets FormSubmit send an activation email to an inbox that already works.

Important:

- This is temporary.
- The public page should push people to the form, text, or WhatsApp while the business inbox is unfinished.
- After Microsoft 365 DNS is active, switch the form action in `book.html` back to `https://formsubmit.co/bookings@miamipapanoel.com`.
- Also switch the `mailto:` fallback in `book.html` back to `bookings@miamipapanoel.com`.
- Then submit the form again and activate FormSubmit for the business email.

Tonight activation test:

1. Open `https://miamipapanoel.com/book?source=tonight-test`.
2. Submit a test request:
   - Name: `Test Lead`
   - Phone: `305-244-0360`
   - City: `Doral`
   - Details: `Temporary Hotmail FormSubmit activation test - please ignore`
3. Open `rubiosally@hotmail.com`.
4. Find the FormSubmit activation email.
5. Click the activation link.
6. Submit the form one more time and confirm the request arrives.

## Current Status

Checked with DNS on June 14, 2026:

- `miamipapanoel.com` is using Vercel DNS.
- The website is live.
- There are no public MX records for `miamipapanoel.com` yet.
- Because there are no MX records, `bookings@miamipapanoel.com` is not ready to receive email yet.
- The booking form is temporarily routed to `rubiosally@hotmail.com` so leads can arrive tonight while Microsoft 365 email is unfinished.

## Best Path Before Father's Day

Keep the website DNS on Vercel for now. Do not move nameservers unless someone is watching the site afterward.

The current preferred path is Microsoft 365 Business Basic because it fits Outlook/Windows and can become a real family business inbox.

Use this step-by-step runbook:

`microsoft-365-email-runbook.md`

Fallback options:

1. Google Workspace if the family wants a real Gmail-style inbox.
2. Zoho Mail if the family wants a low-cost custom inbox.
3. ImprovMX or a similar forwarding service if the family only needs `bookings@miamipapanoel.com` to forward to an existing inbox.

Cloudflare Email Routing is still a good option, but it usually works best when the domain is managed in Cloudflare DNS. Moving DNS right before the Father's Day handoff adds avoidable risk.

## Exact Finish Checklist

### 1. Pick The Email Provider

Recommended for fastest finish:

- If using Outlook/Windows: Microsoft 365 Business Basic.
- If budget allows and Gmail is preferred: Google Workspace.
- If budget matters: Zoho Mail.
- If forwarding only: ImprovMX or similar forwarding service.

Main address:

`bookings@miamipapanoel.com`

Destination inbox if using forwarding:

`rubiosally@hotmail.com`

### 2. Add MX Records In Vercel

Vercel dashboard:

`Project > Domains > miamipapanoel.com > DNS Records`

Add the MX records exactly as the email provider gives them.

Do not guess these values. The provider may also give SPF, DKIM, and DMARC records.

### 3. Add TXT/CNAME Records

Add any verification, SPF, DKIM, or DMARC records from the email provider.

Common examples:

- `TXT` for domain ownership verification
- `TXT` for SPF
- `CNAME` or `TXT` for DKIM
- `TXT` for DMARC

### 4. Verify Receiving

Send a test email from a separate account to:

`bookings@miamipapanoel.com`

Confirm it arrives in the destination inbox.

### 5. Activate FormSubmit

Open the live booking form:

`https://miamipapanoel.com/book?source=formsubmit-test`

Submit a test request with obvious test details:

- Name: `Test Lead`
- Phone: `305-244-0360`
- City: `Doral`
- Details: `FormSubmit activation test - please ignore`

FormSubmit should send an activation email to:

`bookings@miamipapanoel.com`

Click the activation link in that email.

### 6. Test The Full Loop

Submit the booking form again.

Confirm the request arrives in the inbox and includes:

- Name
- Phone
- Date
- City
- Visit option
- Celebration type
- Lead source
- Gift details

### 7. Mark Complete

Once the full loop works:

- Google Business Profile booking link can safely use `https://miamipapanoel.com/book?source=google%20business`
- Instagram bio can safely use `https://miamipapanoel.com/links`
- QR card can safely use the booking form
- The family can treat the website as a real lead catcher

## DNS Commands Used To Check

```powershell
Resolve-DnsName -Name miamipapanoel.com -Type MX
Resolve-DnsName -Name miamipapanoel.com -Type TXT
Resolve-DnsName -Name miamipapanoel.com -Type A
```

## Sources

- Cloudflare Email Routing destination addresses: https://developers.cloudflare.com/email-service/configuration/email-routing-addresses/
- Cloudflare Email Routing domain setup: https://developers.cloudflare.com/email-service/get-started/route-emails/
- Vercel DNS records: https://vercel.com/docs/domains/managing-dns-records
- FormSubmit setup: https://formsubmit.co/
