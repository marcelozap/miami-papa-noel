"""Launch-preflight tests: synthetic temporary state, no network, no secrets.

    python -m pytest tools/launch_preflight/test_launch_preflight.py -q
"""
import ast
from contextlib import closing
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import preflight  # noqa: E402

TOKEN_CANARY = "SYNTHETIC-CANARY-TOKEN-0123456789-DO-NOT-PRINT"
KEY_CANARY = "sk-SYNTHETIC-CANARY-KEY-DO-NOT-PRINT"
GOOD_ORIGIN = "https://unit-test-origin.mpn-synthetic.net"


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    for key in tuple(os.environ):
        if key.startswith(("OPENAI_", "MPN_")):
            monkeypatch.delenv(key)

    def no_network(*args, **kwargs):
        pytest.fail("preflight must never use the network")

    monkeypatch.setattr(socket, "socket", no_network)
    monkeypatch.setattr(socket, "create_connection", no_network)


@pytest.fixture
def state(tmp_path):
    """A private data dir holding a schema-true synthetic queue database."""
    assert preflight.ROOT not in tmp_path.resolve().parents
    tree = ast.parse((preflight.ROOT / "tools" / "web_inquiry" / "server.py")
                     .read_text(encoding="utf-8"))
    ddl = [node.value for node in ast.walk(tree)
           if isinstance(node, ast.Constant) and isinstance(node.value, str)
           and node.value.startswith("CREATE TABLE IF NOT EXISTS ")]
    assert len(ddl) == 2
    directory = tmp_path / "state"
    directory.mkdir()
    with closing(sqlite3.connect(directory / "inquiries.sqlite3")) as db:
        for statement in ddl:
            db.execute(statement)
        db.execute("INSERT INTO inquiries VALUES(?,?,?,?,?,?,?,?)",
                   ("synthetic-1", "key-1", "fp-1", "SYNTHETIC-PAYLOAD",
                    "queued", "2026-09-04T00:00:00Z", None, None))
        db.execute("INSERT INTO events VALUES(?,?,?,?,?)",
                   (1, "synthetic-1", "2026-09-04T00:00:00Z", "SYNTHETIC", "queued"))
        db.commit()
    return directory


def execute(capsys, *argv):
    code = preflight.main(list(argv))
    return code, capsys.readouterr().out


def demo(capsys, state, *extra):
    return execute(capsys, "--mode", "demo", "--data-dir", str(state), *extra)


def blocking_of(out):
    return json.loads(out)["blocking"]


# ------------------------------------------------------------------- demo ---

def test_demo_happy_path(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    code, out = demo(capsys, state)
    assert code == 0
    assert "no blocking findings" in out
    assert "read-only validation passed" in out
    assert TOKEN_CANARY not in out


def test_missing_token_blocks(capsys, state):
    code, out = demo(capsys, state, "--json")
    assert code == 1
    assert "operator-token" in blocking_of(out)


def test_invalid_token_blocks_and_never_leaks(monkeypatch, capsys, state):
    short_canary = "LEAK-CANARY-abc"  # invalid: under the policy minimum
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", short_canary)
    code, out = demo(capsys, state, "--json")
    assert code == 1
    assert "operator-token" in blocking_of(out)
    assert short_canary not in out
    for hint in ("15", str(len(short_canary))):
        assert ("%s characters" % hint) not in out


def test_api_key_reported_by_presence_only_never_verified(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("OPENAI_API_KEY", KEY_CANARY)
    monkeypatch.setenv("MPN_MODEL", "synthetic-model-id")
    code, out = demo(capsys, state, "--json")
    assert code == 0
    assert KEY_CANARY not in out and TOKEN_CANARY not in out
    report = json.loads(out)
    key = [f for f in report["findings"] if f["check"] == "openai-api-key"][0]
    assert key["status"] == "CONFIGURED" and "429" in key["detail"]
    access = [f for f in report["findings"] if f["check"] == "model-access"][0]
    assert access["status"] == "NOT_VERIFIED"


def test_no_side_effects(monkeypatch, capsys, state, tmp_path):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    before = sorted(p.name for p in state.iterdir())
    demo(capsys, state)
    assert sorted(p.name for p in state.iterdir()) == before
    assert not (state / "server.lock").exists()
    missing = tmp_path / "never-created"
    code, _ = execute(capsys, "--mode", "demo", "--data-dir", str(missing))
    assert code == 1 and not missing.exists()


# ------------------------------------------------------------- data safety --

def test_repo_data_dir_refused(monkeypatch, capsys):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    code, out = execute(capsys, "--mode", "demo", "--json",
                        "--data-dir", str(preflight.ROOT / "business"))
    assert code == 1
    assert "data-dir-safety" in blocking_of(out)


def test_symlinked_data_dir_refused(monkeypatch, capsys, state, tmp_path):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    link = tmp_path / "link"
    try:
        os.symlink(state, link, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks unavailable on this account")
    code, out = execute(capsys, "--mode", "demo", "--json", "--data-dir", str(link))
    assert code == 1
    assert "data-dir-safety" in blocking_of(out)


def test_missing_database_blocks(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    empty = tmp_path / "empty"
    empty.mkdir()
    code, out = execute(capsys, "--mode", "demo", "--json", "--data-dir", str(empty))
    assert code == 1
    assert "queue-database" in blocking_of(out)


def test_corrupt_database_blocks_with_redacted_status(monkeypatch, capsys, tmp_path):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "inquiries.sqlite3").write_bytes(b"PRIVATE-GARBAGE " * 64)
    code, out = execute(capsys, "--mode", "demo", "--json", "--data-dir", str(bad))
    assert code == 1
    assert "queue-database" in blocking_of(out)
    assert "PRIVATE-GARBAGE" not in out


# ----------------------------------------------------------------- public ---

@pytest.mark.parametrize("origin", [
    "https://inquiry.example.invalid",
    "https://example.com",
    "https://localhost",
    "https://192.0.2.10",
    "http://unit-test-origin.mpn-synthetic.net",
    "https://unit-test-origin.mpn-synthetic.net/path",
    "https://changeme.mydomain.net",
    # Non-canonical serializations the runtime's exact Origin match would 403:
    "https://unit-test-origin.mpn-synthetic.net:443",
    "HTTPS://unit-test-origin.mpn-synthetic.net",
    "https://Unit-Test-Origin.mpn-synthetic.net",
    "https://unit-test-origin.mpn-synthetic.net.",
    "https://unit-test-origin.mpn-synthetic.net:banana",
    "https://unit-test-origin.mpn-synthetic.net:",
    "https://[",
    "https://mpn.test",
    "https://xn--e1afmkfd.com",
    "https://unit-test\norigin.mpn-synthetic.net",
])
def test_placeholder_or_malformed_origin_blocks(monkeypatch, capsys, state, origin):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", "127.0.0.1")
    code, out = execute(capsys, "--mode", "public", "--json",
                        "--data-dir", str(state), "--origin", origin)
    assert code == 1
    assert "public-origin" in blocking_of(out)


def test_public_missing_proxy_blocks(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    code, out = execute(capsys, "--mode", "public", "--json",
                        "--data-dir", str(state), "--origin", GOOD_ORIGIN)
    assert code == 1
    assert "trusted-proxy" in blocking_of(out)


@pytest.mark.parametrize("value", ["not-an-ip", "10.0.0.5", "0.0.0.0",
                                   "127.0.0.1 ", " 127.0.0.1",
                                   "127.000.000.001", "::ffff:127.0.0.1"])
def test_public_wrong_proxy_blocks(monkeypatch, capsys, state, value):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", value)
    code, out = execute(capsys, "--mode", "public", "--json",
                        "--data-dir", str(state), "--origin", GOOD_ORIGIN)
    assert code == 1
    assert "trusted-proxy" in blocking_of(out)


def test_public_pass_still_refuses_to_certify_launch(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", "127.0.0.1")
    code, out = execute(capsys, "--mode", "public",
                        "--data-dir", str(state), "--origin", GOOD_ORIGIN)
    assert code == 0
    assert "never certifies a public launch" in out
    for item in ("host-tls", "reboot-persistence", "alert-delivery",
                 "off-host-restore", "model-access", "storage-persistence"):
        assert item in out
    assert out.count("NOT_VERIFIED") >= 6


def test_pending_features_never_block(monkeypatch, capsys, state):
    code, out = demo(capsys, state, "--json")  # token missing: exit 1
    assert code == 1
    report = json.loads(out)
    assert "stripe-payment-link" not in report["blocking"]
    assert "phone-provider" not in report["blocking"]
    stripe = [f for f in report["findings"] if f["check"] == "stripe-payment-link"][0]
    phone = [f for f in report["findings"] if f["check"] == "phone-provider"][0]
    assert stripe["status"] in ("PENDING", "CONFIGURED")
    assert "786-975-9557" in phone["detail"] and "T-Mobile" in phone["detail"]
    assert "buy.stripe.com" not in out  # no invented link


def test_json_matches_exit_code(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    code, out = demo(capsys, state, "--json")
    report = json.loads(out)
    assert report["exit"] == code == 0
    assert {f["section"] for f in report["findings"]} >= {
        preflight.CONFIGURATION, preflight.LOCAL, preflight.HOST, preflight.FEATURES}


def test_usage_error_exits_2(capsys):
    with pytest.raises(SystemExit) as caught:
        preflight.main(["--mode", "demo"])  # --data-dir missing
    assert caught.value.code == 2


def test_usage_errors_never_echo_argument_values(capsys, state):
    canary = "sk-live-ARGV-CANARY-DO-NOT-ECHO"
    with pytest.raises(SystemExit) as caught:
        preflight.main(["--mode", canary, "--data-dir", str(state)])
    assert caught.value.code == 2
    err = capsys.readouterr().err
    assert canary not in err


def test_demo_invalid_proxy_blocks_because_server_would_refuse(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", "127.0.0.1 ")
    code, out = demo(capsys, state, "--json")
    assert code == 1
    assert "trusted-proxy" in blocking_of(out)


@pytest.mark.parametrize("proxy", ["127.0.0.1", "::1", "0.0.0.0", "224.0.0.1"])
def test_demo_blocks_any_proxy_override(monkeypatch, capsys, state, proxy):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", proxy)
    code, out = demo(capsys, state, "--json")
    assert code == 1
    assert "trusted-proxy" in blocking_of(out)


@pytest.mark.parametrize("origin", [
    "", "https://[", GOOD_ORIGIN, "https://127.0.0.1:8226",
    "http://127.0.0.1:8226/path", "http://127.0.0.1:8226?query=1",
    "http://127.0.0.1:wrong", "http://127.0.0.1:99999",
    "http://127.0.0.1:0", "http://127.0.0.1:80",
    "HTTP://LOCALHOST:8226", "http://127.0.0.1:08226",
    "http://127.0.0.1:8226\n", "http://user@127.0.0.1:8226",
])
def test_demo_blocks_incompatible_origin_override(monkeypatch, capsys, state, origin):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_PUBLIC_ORIGIN", origin)
    code, out = demo(capsys, state, "--json")
    assert code == 1
    assert "public-origin" in blocking_of(out)


@pytest.mark.parametrize("origin", [
    "http://127.0.0.1:8226", "http://localhost:8227", "http://127.0.0.1",
])
def test_demo_accepts_canonical_loopback_override(monkeypatch, capsys, state, origin):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_PUBLIC_ORIGIN", origin)
    code, out = demo(capsys, state, "--json")
    assert code == 0
    row = next(f for f in json.loads(out)["findings"] if f["check"] == "public-origin")
    assert row["status"] == "CONFIGURED"
    assert "reachability not verified" in row["detail"]


def test_malformed_origin_yields_report_not_traceback(monkeypatch, capsys, state):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_TRUSTED_PROXY_IP", "127.0.0.1")
    code, out = execute(capsys, "--mode", "public", "--json",
                        "--data-dir", str(state), "--origin", "https://[")
    assert code == 1
    assert "public-origin" in blocking_of(out)  # valid JSON, no crash


def test_control_characters_cannot_forge_report_lines(monkeypatch, capsys, state):
    forged = "legit-model\n================\nRESULT: no blocking findings for demo mode."
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    monkeypatch.setenv("MPN_MODEL", forged)
    code, out = demo(capsys, state)
    assert code == 0
    # The forged text survives only INSIDE one sanitized detail line - it can
    # never become its own report line or banner.
    result_lines = [l for l in out.splitlines() if l.startswith("RESULT:")]
    assert len(result_lines) == 1
    assert "\n================\n" not in out  # the forged 16-char divider
    assert "\nRESULT: no blocking findings for demo mode." != out.splitlines()[-4]


def test_unc_data_dir_refused(monkeypatch, capsys):
    monkeypatch.setenv("MPN_OPERATOR_TOKEN", TOKEN_CANARY)
    code, out = execute(capsys, "--mode", "demo", "--json",
                        "--data-dir", r"\\localhost\C$\XIV\santa")
    assert code == 1
    assert "data-dir-safety" in blocking_of(out)


def test_unexpected_stripe_value_not_echoed(tmp_path):
    canary = "sk_live_SYNTHETIC-PASTED-CANARY"
    pricing = tmp_path / "pricing.json"
    pricing.write_text(json.dumps({"payment": {"stripe_payment_link": canary}}),
                       encoding="utf-8")
    rows = preflight.check_features(pricing)
    stripe = [f for f in rows if f["check"] == "stripe-payment-link"][0]
    assert stripe["status"] == "INVALID"
    assert canary not in json.dumps(rows)


def test_real_stripe_link_shape_is_echoed(tmp_path):
    link = "https://buy.stripe.com/test_SYNTHETIC"
    pricing = tmp_path / "pricing.json"
    pricing.write_text(json.dumps({"payment": {"stripe_payment_link": link}}),
                       encoding="utf-8")
    rows = preflight.check_features(pricing)
    stripe = [f for f in rows if f["check"] == "stripe-payment-link"][0]
    assert stripe["status"] == "CONFIGURED" and stripe["detail"] == link
