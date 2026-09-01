"""Run the local Ms. Claus review without network access or file writes.

The review is intentionally conservative: it reports issues for a human to
approve rather than editing the website, sending messages, or touching accounts.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from html.parser import HTMLParser
from pathlib import Path


PUBLIC_PHONE = "786-975-9557"
OLD_PUBLIC_PHONE = "305-244-0360"
ZELLE_PHONE = "305-244-0360"
FORBIDDEN_PAYMENT_TERMS = ("cash app", "venmo", "paypal", "square", "wire")  # stripe = official rail since 2026-08-30
INSURANCE_TERMS = ("insured", "general liability", "certificate of insurance", "additional insured")
REQUIRED_CHECKLIST = {
    "chair": ("chair", "silla"),
    "air conditioning": ("air conditioning", "aire acondicionado"),
    "gift/photo adult": ("designated adult", "adulto encargado"),
    "parking": ("parking within 100 feet", "estacionamiento a menos de 100 pies"),
}


class VisibleTextParser(HTMLParser):
    """Extract titles, headings, and visible copy with only the stdlib."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.headings: list[str] = []
        self.text: list[str] = []
        self._skip_depth = 0
        self._in_title = False
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template"}:
            self._skip_depth += 1
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = True
        if tag in {"h1", "h2", "h3"}:
            self._heading_tag = tag
            self._heading_parts = []

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "template"}:
            self._skip_depth = max(0, self._skip_depth - 1)
            return
        if self._skip_depth:
            return
        if tag == "title":
            self._in_title = False
        if self._heading_tag == tag:
            heading = normalize(" ".join(self._heading_parts))
            if heading:
                self.headings.append(heading)
            self._heading_tag = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        value = normalize(data)
        if not value:
            return
        if self._in_title:
            self.title = normalize(f"{self.title} {value}")
        if self._heading_tag:
            self._heading_parts.append(value)
        self.text.append(value)


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", unescape(value)).strip()


def phone_patterns(phone: str) -> tuple[str, ...]:
    digits = re.sub(r"\D", "", phone)
    return (phone, digits, f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}", f"+1{digits}")


def contains_any(text: str, terms: tuple[str, ...]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def scan_page(path: Path, public_phone: str = PUBLIC_PHONE) -> dict[str, object]:
    raw = path.read_text(encoding="utf-8")
    parser = VisibleTextParser()
    parser.feed(raw)
    visible = " ".join(parser.text)
    old_patterns = phone_patterns(OLD_PUBLIC_PHONE)
    stale_lines = [
        line.strip()
        for line in raw.splitlines()
        if any(pattern in line for pattern in old_patterns)
        and "zelle" not in line.lower()
    ]
    forbidden = contains_any(raw, FORBIDDEN_PAYMENT_TERMS)
    insurance = contains_any(raw, INSURANCE_TERMS)
    return {
        "file": path.name,
        "title": parser.title,
        "heading_count": sum(1 for heading in parser.headings if heading),
        "h2_plus_count": max(0, len(parser.headings) - 1),
        "visible_characters": len(visible),
        "public_phone_count": sum(raw.count(pattern) for pattern in phone_patterns(public_phone)),
        "stale_public_phone_lines": stale_lines,
        "forbidden_payment_terms": forbidden,
        "insurance_terms": insurance,
    }


def audit(root: Path, public_phone: str = PUBLIC_PHONE) -> dict[str, object]:
    pages = [scan_page(path, public_phone) for path in sorted(root.glob("*.html"))]
    clear: list[str] = []
    cluttered: list[str] = []
    remove_or_merge: list[str] = []
    simplify: list[str] = []

    stale = [page for page in pages if page["stale_public_phone_lines"]]
    forbidden = [page for page in pages if page["forbidden_payment_terms"]]
    insurance = [page for page in pages if page["insurance_terms"]]
    if not stale:
        clear.append(f"Public contact number is consistent: {public_phone}.")
    else:
        clear.append("Public contact number still needs review on one or more pages.")
    if not forbidden:
        clear.append("Customer-facing payment language contains no unapproved method.")
    else:
        clear.append("Payment language needs human review before publication.")
    if not insurance:
        clear.append("No unverified insurance wording is present on public pages.")
    else:
        clear.append("Insurance wording is present and must be verified before sending traffic.")

    for page in pages:
        if page["h2_plus_count"] > 14 or page["visible_characters"] > 14000:
            cluttered.append(
                f"{page['file']}: {page['h2_plus_count']} secondary headings, "
                f"{page['visible_characters']} visible characters."
            )
    if cluttered:
        remove_or_merge.append("Review the longest pages for repeated calls to action before adding new sections.")
    else:
        remove_or_merge.append("Nothing needs removal from this pass; keep the site small.")

    checkout = root / "checkout.html"
    if checkout.exists():
        checkout_text = checkout.read_text(encoding="utf-8").lower()
        missing = [
            label
            for label, signals in REQUIRED_CHECKLIST.items()
            if not any(signal in checkout_text for signal in signals)
        ]
        if missing:
            simplify.append("Checkout is missing: " + ", ".join(missing) + ".")
        else:
            simplify.append("Checkout states the booking requirements in English and Spanish.")
    else:
        simplify.append("Checkout page was not found; verify the booking path manually.")

    blockers: list[str] = []
    for page in stale:
        blockers.append(f"{page['file']}: old public phone remains outside Zelle instructions")
    for page in forbidden:
        blockers.append(f"{page['file']}: unapproved payment term(s): {', '.join(page['forbidden_payment_terms'])}")
    for page in insurance:
        blockers.append(f"{page['file']}: insurance wording requires verification")
    if checkout.exists():
        checkout_text = checkout.read_text(encoding="utf-8").lower()
        for label, signals in REQUIRED_CHECKLIST.items():
            if not any(signal in checkout_text for signal in signals):
                blockers.append(f"checkout.html: missing booking requirement: {label}")

    if blockers:
        next_change = blockers[0] + "."
    else:
        next_change = "Use this report before each campaign release; Ms. Claus recommends one human-approved change at a time."

    return {
        "agent": "Ms. Claus",
        "mode": "local-rules",
        "root": str(root),
        "public_phone": public_phone,
        "zelle_phone_preserved": ZELLE_PHONE,
        "pages_scanned": len(pages),
        "blockers": blockers,
        "pages": pages,
        "clear": clear,
        "cluttered": cluttered,
        "remove_or_merge": remove_or_merge,
        "simplify_wording": simplify,
        "one_next_change": next_change,
    }


def print_report(result: dict[str, object]) -> None:
    print("Ms. Claus local review")
    print(f"Pages scanned: {result['pages_scanned']}")
    print("Network: none | Writes: none")
    print("\nClear:")
    for item in result["clear"]:
        print(f"- {item}")
    print("\nCluttered:")
    for item in result["cluttered"] or ["No page crossed the review threshold."]:
        print(f"- {item}")
    print("\nRemove or merge:")
    for item in result["remove_or_merge"]:
        print(f"- {item}")
    print("\nSimplify wording:")
    for item in result["simplify_wording"]:
        print(f"- {item}")
    print("\nOne next change:")
    print(f"- {result['one_next_change']}")
    if result["blockers"]:
        print("\nBlockers:")
        for item in result["blockers"]:
            print(f"- {item}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local Ms. Claus site review.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--contact-phone", default=PUBLIC_PHONE)
    parser.add_argument("--json", action="store_true", help="Print machine-readable output.")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when a release blocker is found.")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"Root does not exist: {root}", file=sys.stderr)
        return 2
    result = audit(root, args.contact_phone)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_report(result)
    return 1 if args.strict and result["blockers"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
