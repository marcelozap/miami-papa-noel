"""Offline workshop safety contract; no real credentials or customer state."""
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import offline_workshop as workshop


def test_check_has_no_listener_or_secret_output(monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-key-canary")
    monkeypatch.setenv("MPN_CHAT_ALLOW_MODEL", "1")
    monkeypatch.setenv("MPN_API_DAILY_CALL_CAP", "9")
    def denied(*a, **k):
        pytest.fail("Check must not open a server")
    monkeypatch.setattr(workshop, "Server", denied)
    assert workshop.main(["--check"]) == 0
    assert "OFFLINE WORKSHOP READY" in capsys.readouterr().out
    assert workshop.os.environ["OPENAI_API_KEY"] == "synthetic-key-canary"
    assert workshop.os.environ["MPN_CHAT_ALLOW_MODEL"] == "1"


def test_offline_environment_clears_and_restores_on_failure(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-only")
    monkeypatch.delenv("MPN_API_COST_POLICY", raising=False)
    with pytest.raises(RuntimeError):
        with workshop.offline_environment():
            assert workshop.os.environ["OPENAI_API_KEY"] == ""
            assert workshop.os.environ["MPN_API_DAILY_CALL_CAP"] == "0"
            assert workshop.os.environ["MPN_CHAT_ALLOW_MODEL"] == "0"
            raise RuntimeError()
    assert workshop.os.environ["OPENAI_API_KEY"] == "synthetic-only"
    assert "MPN_API_COST_POLICY" not in workshop.os.environ


@pytest.mark.parametrize("port", ["0", "80", "65536"])
def test_invalid_ports_refused(port):
    with pytest.raises(SystemExit):
        workshop.main(["--port", port, "--check"])
