# Business Email Setup

The public email should use the domain, not a personal Hotmail/Gmail address.

## Recommended Addresses

Use one main public inbox:

- `bookings@miamipapanoel.com`

Optional aliases:

- `hello@miamipapanoel.com`
- `events@miamipapanoel.com`
- `reviews@miamipapanoel.com`

## Best Setup Options

### Option 1 - Google Workspace

Best if the family wants the easiest professional Gmail-style inbox.

Use when:

- They want to send and receive from `bookings@miamipapanoel.com`.
- They want Google Calendar, Drive, Docs, and Gmail in one place.
- They are okay paying monthly per user.

Suggested setup:

- User: `bookings@miamipapanoel.com`
- Recovery email: a trusted personal email
- Calendar: `Miami Papa Noel Bookings`

### Option 2 - Zoho Mail

Best if they want a low-cost or free custom-domain inbox.

Use when:

- Budget matters.
- They are okay using Zoho's webmail/app instead of Gmail.
- They may want up to a few custom email users.

Suggested setup:

- User: `bookings@miamipapanoel.com`
- Alias: `hello@miamipapanoel.com`

### Option 3 - Cloudflare Email Routing or ImprovMX

Best if they only need forwarding.

Use when:

- They want `bookings@miamipapanoel.com` to forward into an existing inbox.
- They do not need a full hosted mailbox yet.
- They want the fastest, cheapest start.

Important:

- Forwarding receives email.
- Sending replies from the domain may require extra SMTP setup or a paid provider.

## My Recommendation

Start with:

`bookings@miamipapanoel.com`

If money is tight, use Zoho Mail or email forwarding first. If they want the easiest experience and can pay monthly, use Google Workspace.

## Setup Steps

1. Choose provider: Google Workspace, Zoho Mail, Cloudflare Email Routing, or ImprovMX.
2. Create `bookings@miamipapanoel.com`.
3. Add domain DNS records in the domain/DNS dashboard.
4. Add MX records from the email provider.
5. Add SPF, DKIM, and DMARC records if the provider gives them.
6. Send a test email to `bookings@miamipapanoel.com`.
7. Send a reply from `bookings@miamipapanoel.com`.
8. Update the website placeholders:
   - `[EMAIL]` becomes `bookings@miamipapanoel.com`
9. Update Instagram, Facebook, Google Business Profile, and WhatsApp Business.

## DNS Records

The email provider will give exact DNS records. They usually look like:

- MX records for receiving mail
- TXT record for SPF
- TXT or CNAME records for DKIM
- TXT record for DMARC

Do not guess these records. Copy them exactly from the chosen provider.

## Temporary Forwarding

If needed, the business email can forward into a personal inbox at first.

Example:

`bookings@miamipapanoel.com` forwards to `rubiosally@hotmail.com`.

Do not show the personal inbox publicly on the website once the business email is active.

## Website Update After Email Is Ready

Search the project for:

`[EMAIL]`

Replace with:

`bookings@miamipapanoel.com`

Then commit and push:

```powershell
git add .
git commit -m "Update business email"
git push
```
