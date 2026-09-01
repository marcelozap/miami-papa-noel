import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ms_claus.ms_claus import audit, scan_page


def write_page(root: Path, name: str, body: str) -> None:
    (root / name).write_text(
        f"<html><head><title>Test</title></head><body><h1>Test</h1>\n{body}\n</body></html>",
        encoding="utf-8",
    )


def test_old_public_number_is_blocked_but_zelle_is_allowed(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "checkout.html",
        "<p>Call 305-244-0360.</p>\n<p>Zelle to 305-244-0360.</p>\n"
        "<p>Chair. Air conditioning. Designated adult. Parking within 100 feet.</p>",
    )
    result = audit(tmp_path)
    assert any("old public phone" in item for item in result["blockers"])
    assert scan_page(tmp_path / "checkout.html")["stale_public_phone_lines"]


def test_new_public_number_and_requirements_pass(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "checkout.html",
        "<p>Call 786-975-9557.</p>\n<p>Zelle to 305-244-0360.</p>\n"
        "<p>Chair. Air conditioning. Designated adult. Parking within 100 feet.</p>",
    )
    result = audit(tmp_path)
    assert result["blockers"] == []
    assert result["zelle_phone_preserved"] == "305-244-0360"


def test_unapproved_payment_method_is_blocked(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "checkout.html",
        "<p>Call 786-975-9557.</p>\n<p>Zelle to 305-244-0360.</p>\n"
        "<p>Chair. Air conditioning. Designated adult. Parking within 100 feet.</p>"
        "<p>We accept Venmo.</p>",
    )
    result = audit(tmp_path)
    assert any("unapproved payment" in item for item in result["blockers"])


def test_insurance_wording_is_flagged(tmp_path: Path) -> None:
    write_page(
        tmp_path,
        "checkout.html",
        "<p>Call 786-975-9557.</p>\n<p>Zelle to 305-244-0360.</p>\n"
        "<p>Chair. Air conditioning. Designated adult. Parking within 100 feet.</p>"
        "<p>Fully insured.</p>",
    )
    result = audit(tmp_path)
    assert any("insurance wording" in item for item in result["blockers"])
