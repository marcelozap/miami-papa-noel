# Review and Referral System

Use this after every completed visit. The goal is to turn happy moments into proof, referrals, and future bookings without making the client feel pressured.

Public after-visit page:

`https://miamipapanoel.com/after-visit`

## The 24-Hour Rule

Send a thank-you message within 24 hours of the visit while the moment still feels fresh.

Update `../lead-tracker.csv`:

- Status: `Review requested`
- Follow-Up Date: 2 days after the event
- Notes: whether you asked for review, photo permission, referral, or all three

## First Thank-You Message

### English

Hi [NAME], thank you again for having Miami Papa Noel at your event. It was a joy to be part of it.

If you have a moment, this page makes it easy to send a short review, share one approved photo, or refer another family, school, HOA, business, or nonprofit:

https://miamipapanoel.com/after-visit

Even one sentence helps our family business so much.

### Spanish

Hola [NAME], muchas gracias por invitar a Miami Papa Noel a su evento. Fue una alegria ser parte de ese momento.

Si tiene un momento, esta pagina hace facil enviar una resena corta, compartir una foto aprobada o referir otra familia, escuela, comunidad, negocio o nonprofit:

https://miamipapanoel.com/after-visit

Una sola frase ayuda muchisimo a nuestro negocio familiar.

## If They Send a Review

Reply:

Thank you so much. This helps other families feel comfortable booking, and we truly appreciate it.

Tracker:

- Status: `Review received`
- Notes: paste the review text or where it was posted

## If They Send a Photo

Before posting, confirm permission clearly.

### Photo Permission Confirmation

Thank you. Just confirming: may Miami Papa Noel share this approved photo on the website, Instagram, flyers, or Google Business Profile to show real visit moments?

If yes, please reply: `Yes, you may share this photo.`

Tracker:

- Status: keep current booking status or set `Review requested`
- Notes: `Photo permission requested` or `Photo approved`

## If They Refer Someone

Reply:

Thank you for the referral. Please ask them to send the date, city, visit type, and whether gifts will be involved. They can request a visit here:

https://miamipapanoel.com/book?source=referral

Tracker:

- Add the referred person as a new lead.
- Lead Source: `Referral`
- Notes: who referred them, if known.

## Two-Day Follow-Up

If they did not reply after two days, send one gentle follow-up.

### English

Hi [NAME], just following up once. If you have a minute, one short review or approved photo would help Miami Papa Noel so much.

Easy page:

https://miamipapanoel.com/after-visit

Thank you again for including us.

### Spanish

Hola [NAME], solo hago un seguimiento rapido. Si tiene un minuto, una resena corta o una foto aprobada ayudaria muchisimo a Miami Papa Noel.

Pagina facil:

https://miamipapanoel.com/after-visit

Gracias otra vez por incluirnos.

## What Not To Do

- Do not post photos without clear permission.
- Do not pressure a family after they ignore one follow-up.
- Do not promise discounts, commissions, or free visits for referrals unless the family agrees first.
- Do not share private addresses, names of children, or event details publicly.

## Weekly Review Routine

Every Friday:

- Check which completed events have no review request.
- Send the 24-hour message if it was missed.
- Move replies into `../lead-tracker.csv`.
- Save approved review quotes for the website.
- Save approved photos in the marketing photo folder.
- Choose one approved proof moment for a story or post.
