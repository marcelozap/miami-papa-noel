# Microsoft 365 Email Runbook

Use this when the family is ready to make `bookings@miamipapanoel.com` a real inbox.

Current safe status:

- Website is live.
- DNS is managed in Vercel.
- `bookings@miamipapanoel.com` does not receive email yet because there are no MX records.
- The live booking form is temporarily routed to `rubiosally@hotmail.com`.
- Do not switch FormSubmit back to `bookings@miamipapanoel.com` until that inbox receives test email.

## Tonight If Tired

Do nothing else in DNS.

The temporary booking form route is already set. The only useful tonight step is:

1. Open `rubiosally@hotmail.com`.
2. Find the FormSubmit activation email.
3. Click the activation link.
4. Submit one more test at `https://miamipapanoel.com/book?source=tonight-test`.

## Microsoft 365 Setup

### 1. Buy Microsoft 365 Business Basic

Use a new family/business admin account, not a work account.

After purchase, sign in at:

`https://admin.microsoft.com`

### 2. Add The Domain

In Microsoft 365 Admin Center:

1. Open `Settings > Domains`.
2. Click `Add domain`.
3. Enter `miamipapanoel.com`.
4. Choose `I'll manage my own DNS records`.
5. Continue until Microsoft shows the DNS records.

Screenshot needed:

`m365-dns-records.png`

It must show every DNS row Microsoft gives for `miamipapanoel.com`, including TXT verification, MX, SPF, Autodiscover/CNAME, and DKIM if shown.

### 3. Add Records In Vercel

Only after Microsoft shows the exact records, open:

`https://vercel.com`

Then go to:

`miami-papa-noel > Domains > miamipapanoel.com > DNS Records`

For each Microsoft row:

- Type: use Microsoft's type, such as TXT, MX, or CNAME.
- Name: use `@` for root records, or the exact subdomain Microsoft shows.
- Value: paste exactly what Microsoft shows.
- Priority: use Microsoft's priority for MX records.

Do not guess. Do not change website A records or nameservers.

Screenshot needed after adding:

`vercel-dns-after.png`

### 4. Create The Mailbox

In Microsoft 365 Admin Center:

1. Open `Users > Active users`.
2. Add a user.
3. Username: `bookings`.
4. Domain: `miamipapanoel.com`.
5. Assign the Business Basic license.

Result:

`bookings@miamipapanoel.com`

### 5. Verify And Test

1. In Microsoft 365, click verify after the TXT record is added.
2. Send a test email from Gmail, Hotmail, or another outside inbox to `bookings@miamipapanoel.com`.
3. Confirm it arrives in Outlook web.
4. Reply from Outlook web to confirm outbound mail works.

## Autoresponder

Set this in Outlook Web or Exchange Admin Center for `bookings@miamipapanoel.com`.

Subject:

`Thank you - Papa Noel booking request received / Gracias - solicitud recibida`

Body:

```text
Hello from Miami Papa Noel,
Thank you for contacting our family business. We received your message and will review your request shortly. To check exact dates and times, please request availability through our booking form: https://miamipapanoel.com/book. If you already completed the booking form, we'll reply with available options as soon as we can. For quick questions, text or call 305-244-0360.
Warmly,
Miami Papa Noel - family owned

Gracias por escribir a Miami Papa Noel. Recibimos su mensaje y lo revisaremos pronto. Para confirmar fechas y horarios, por favor solicite disponibilidad en el formulario: https://miamipapanoel.com/book. Si ya completo el formulario, le responderemos con opciones disponibles. Para preguntas rapidas, envie texto o llame al 305-244-0360.
Con carino,
Miami Papa Noel - negocio familiar
```

## Final Switch Back

Do this only after `bookings@miamipapanoel.com` receives email.

1. In `book.html`, change the FormSubmit action to:

   `https://formsubmit.co/bookings@miamipapanoel.com`

2. Change the `mailto:` fallback in `book.html` to:

   `bookings@miamipapanoel.com`

3. Submit one test request at:

   `https://miamipapanoel.com/book?source=formsubmit-final-test`

4. Open `bookings@miamipapanoel.com`.
5. Click the FormSubmit activation email.
6. Submit one final test and confirm delivery.

## Screenshot Checklist

Need from the Microsoft setup:

- `m365-dns-records.png`
- `vercel-dns-after.png`

Need from final testing:

- A test email arriving in `bookings@miamipapanoel.com`
- A booking form submission arriving in `bookings@miamipapanoel.com`
