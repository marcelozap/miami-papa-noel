# Santa Content Queue - Drafts Only, Nothing Ever Posts

Queue for performer-recorded Santa videos: deterministic bilingual draft
texts, mandatory human approval, dry-run scheduling.

**What it does:** tracks each video by file path, generates deterministic
English + Spanish script and caption drafts from the topic, walks the item
through operator approval, and suggests a post time.

**What it never does:** post, send, publish, call, or submit anything
anywhere; read or copy the video file; invent testimonials, customers,
partners, sponsors, or guarantees. Every artifact is a DRAFT a human posts
manually.

---

## State machine

```
DRAFT -> PENDING_APPROVAL -> APPROVED -> SCHEDULED_DRY_RUN
```

| Transition | Command | Notes |
|---|---|---|
| (new) -> DRAFT | `draft` | deterministic bilingual texts from the topic |
| DRAFT -> PENDING_APPROVAL | `submit` | |
| PENDING_APPROVAL -> APPROVED | `approve` | **requires `--operator`**, recorded in `approvals[]` |
| APPROVED -> SCHEDULED_DRY_RUN | `schedule` | assigns `suggested_post_time`; posts nothing |

Anything else is rejected with `REFUSED` and exit code 2.

### Why `publish` always fails

A `PUBLISHED` state exists in the enum so the vocabulary is stable, but
**every path to it raises**. Publishing requires configured social
credentials AND explicit operator approval at publish time - neither exists
in this version. The refusal is logged (`publish-refused`) so the audit
trail shows every attempt. When you are ready to post, copy the approved
caption and post the video yourself.

---

## Setup

Nothing to install. Python 3.10+ and the standard library.

Queue state lives OUTSIDE the repository and is never committed:

| Variable | Effect |
|---|---|
| `MPN_CONTENT_DIR` | State directory. Default `%LOCALAPPDATA%\MiamiPapaNoel\content` |

Files in that directory: `queue.json` (current items) and
`content-log.jsonl` (append-only audit trail, one line per action).

---

## Daily use

```powershell
cd "C:\XIV\santa"

python tools\content\queue.py draft --video "D:\santa-videos\take-03.mp4" --topic "how a Santa visit works"
python tools\content\queue.py submit --item C-001
python tools\content\queue.py approve --item C-001 --operator "Marcelo"
python tools\content\queue.py schedule --item C-001
python tools\content\queue.py status
python tools\content\queue.py show --item C-001
python tools\content\queue.py audit
```

- **`--video` is a reference, not an upload.** The path may live anywhere
  (external drive, phone backup folder). The tool never opens, reads, or
  copies the file, so drafting works even if the drive is unplugged.
- **Drafts are deterministic.** Same topic in, same text out - fixed
  template strings, no model, no network. Templates mention only: Santa
  visits, Miami, bilingual EN/ES service, the public phone 786-975-9557,
  and booking via text. The topic is inserted verbatim into both languages;
  polish the wording by hand before posting if you want to.
- **`schedule` picks the post time deterministically:** the next Tue/Thu/Sat
  strictly after today, at 10:00 or 18:00 local, round-robin across
  scheduled items (Tue 10:00, Thu 18:00, Sat 10:00, Tue 18:00, ...). It
  then prints exactly what it is: `DRY RUN - no account connected, post
  manually.`

### Forbidden topics

`draft` refuses any topic containing: `testimonial`, `review from`,
`customer said`, `partnered with`, `official partner`, `sponsored by`,
`guaranteed` (case-insensitive). Fabricated social proof and unverified
affiliations are forbidden. **Do not reword the topic to sneak past the
filter - the block is the product.** If a real, verifiable partnership ever
exists, that is a business-document change first, not a caption.

---

## Manual fallback

The business runs without this tool. The queue is a typing-saver: if Python
breaks, write the caption by hand from the same rules - Santa visits,
Miami, bilingual EN/ES, book by text at 786-975-9557 - get a second pair of
eyes on it, and post it yourself. Note what you posted and when, and log it
here later.

---

## Tests

```powershell
python -m pytest tools\content\test_content.py -q
```

16 tests: the full legal path, publish blocked from every state, every
forbidden phrase refused, bilingual drafts with the public phone,
determinism, schedule-only-from-APPROVED, operator-required approval,
round-robin post times, and the audit log. All data synthetic; tests run in
a temp directory and never touch the real state dir.

---

## Files

| File | Purpose |
|---|---|
| `queue.py` | The operator tool |
| `test_content.py` | 16 tests, all synthetic |
| `README.md` | This file |
