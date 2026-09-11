"""Disposable local Santa workshop. No paid generation or production evidence."""
import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import secrets
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.web_inquiry.server import App, Server


@contextmanager
def offline_environment():
    settings = {"OPENAI_API_KEY": "", "MPN_MODEL": "", "MPN_CHAT_ALLOW_MODEL": "0",
                "MPN_API_DAILY_CALL_CAP": "0", "MPN_API_COST_POLICY": "",
                "MPN_CHAT_SECRET": secrets.token_hex(32)}
    saved = {key: os.environ.get(key) for key in settings}
    os.environ.update(settings)
    try:
        yield
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8240)
    parser.add_argument("--check", action="store_true", help="Verify startup without opening a listener")
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error("Choose a port between 1024 and 65535")
    origin = "http://127.0.0.1:%d" % args.port
    with offline_environment(), tempfile.TemporaryDirectory(prefix="santa-offline-workshop-") as folder:
        token = secrets.token_hex(24)
        app = App(Path(folder).resolve() / "queue", token, origin, live=False)
        try:
            if args.check:
                assert app.chat_service is not None and not app.chat_service.allow_model
                print("OFFLINE WORKSHOP READY: templates only; no listener or paid calls.")
                return 0
            with Server(("127.0.0.1", args.port), app) as server:
                print("Santa workshop: " + origin, flush=True)
                print("Operator desk: " + origin + "/operator", flush=True)
                print("Temporary local demo access token: " + token, flush=True)
                print("Synthetic practice only. Closing clears this session. Ctrl+C to stop.", flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    pass
        finally:
            app.close()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except OSError:
        print("Workshop could not start. Check local storage or choose another --port.", file=sys.stderr)
        raise SystemExit(1)
