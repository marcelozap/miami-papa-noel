# Miami Papa Noel — Reservation System (XIV)

Four lanes, one source of truth. A booking moves
`inquiry → hold → pending_review → confirmed → completed`, and the gates are
enforced in code: no agent can confirm, an unverified deposit blocks review,
an undrivable route blocks confirmation, and content is drafted from
confirmed bookings only.

## Daily use (operator)

```powershell
cd C:\Users\Green Machine\miami-papa-noel

# take an inquiry
python business\reservations\papanoel.py new --client-name "Gomez Family" --phone 3055551234 --package christmas_eve --date 2026-12-24 --start-time 17:00 --zone doral

# complete the data as it comes in
python business\reservations\papanoel.py update <id> --address "123 NW 1st St, Doral" --guest-count 6

# after checking the Zelle payment (50%, memo = date + name)
python business\reservations\papanoel.py verify-deposit <id> --amount 250 --memo "12/24 Gomez"

# what's waiting on you, with route feasibility
python business\reservations\papanoel.py review
python business\reservations\papanoel.py approve <id>

# content drafts for confirmed bookings (never for holds)
python business\reservations\papanoel.py content
python business\reservations\papanoel.py approve-post <id>

# daily — then add one line to OPS-LOG.md
python business\reservations\papanoel.py health
```

## Files

`store.py` state machine + storage · `rates.py` locked rate card (mirror of
the site — change the site first) · `zones.py` 10-zone drive matrix
(**sync step:** export the matrix from `business/december-slot-board.html`
to `data/zones.json`; until then built-in estimates are used and labelled) ·
`logistics_agent.py` route feasibility · `reservation_agent.py` intake ·
`operator_review.py` the only confirm/verify paths · `content_agent.py` +
`malosound_adapter.py` bilingual drafts, dry-run adapter ·
`health.py` monitoring · `tests/` the 17-test release gate.

Run tests before any change ships: `python -m pytest business\reservations\tests -q`

Production evidence: `PRODUCTION.md` (stamp the launch date on first real
run) and `OPS-LOG.md` (one line per day).
