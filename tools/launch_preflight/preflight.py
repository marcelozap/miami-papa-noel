#!/usr/bin/env python3
"""Launch preflight for the Mrs. Claus inquiry workflow - read-only.

Tells the operator what is actually missing for the operator-assisted
bilingual inquiry launch, for one explicitly selected mode:

    python tools/launch_preflight/preflight.py --mode demo --data-dir PATH
    python tools/launch_preflight/preflight.py --mode public --data-dir PATH \
        --origin https://HOST [--json]

Guarantees, by construction and by test:
- No network, no model call, no writes. The queue database is opened
  read-only through the maintenance tool; nothing is created, migrated,
  leased, or logged to production. One SQLite caveat, inherited from the
  maintenance tool and documented there: reading a WAL-journal database may
  cause SQLite to maintain its standard -wal/-shm sidecars next to the
  source. No queue row is ever changed.
- Secrets never appear in output. OPENAI_API_KEY and MPN_OPERATOR_TOKEN are
  reported by presence/policy status only - never contents, prefixes,
  hashes, or lengths. Usage errors never echo argument values.
- A configured key or model is CONFIGURED, never VERIFIED. The last
  supplied live API result was HTTP 429; only a successful synthetic
  model-backed test ends that, and this tool cannot run one.
- Exit 0 means the locally checkable items pass for the selected mode. It
  never certifies a public launch: host TLS, reboot persistence, alert
  delivery, off-host restore, and model access stay NOT VERIFIED until
  checked where they actually run.

Exit codes: 0 no blocking findings, 1 blocking findings, 2 usage error.
"""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import platform
import sys
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tools" / "web_inquiry"))
import maintenance  # noqa: E402  (read-only queue validation API)

CONFIGURATION = "configuration"
LOCAL = "locally verified"
HOST = "owner/host verification still needed"
FEATURES = "separate unfinished features"

# Fail closed on anything that looks like a stand-in hostname. A real
# domain containing one of these tokens must be reviewed by a human anyway.
PLACEHOLDER_TOKENS = ("example", "invalid", "placeholder", "yourdomain",
                      "mydomain", "your-domain", "changeme", "change-me",
                      "todo", "sample", "hostname", "localhost")
PLACEHOLDER_TLDS = (".test", ".example", ".invalid", ".localhost", ".local")
PUBLIC_PHONE = "786-975-9557"
PRICING_PATH = ROOT / "tools" / "triage" / "pricing.json"
STRIPE_LINK_PREFIX = "https://buy.stripe.com/"


def clean(text):
    """Render-safe text: control characters can forge report lines."""
    return "".join(ch if ch.isprintable() or ch == " " else "?" for ch in str(text))


def finding(section, check, status, detail, blocking=False):
    return {"section": section, "check": check, "status": status,
            "detail": clean(detail), "blocking": blocking}


def check_runtime(mode):
    out = []
    if sys.version_info >= (3, 10):
        out.append(finding(LOCAL, "python-runtime", "OK",
                           "Python %d.%d" % sys.version_info[:2]))
    else:
        out.append(finding(LOCAL, "python-runtime", "INVALID",
                           "Python 3.10+ required", blocking=True))
    system = platform.system() or "unknown"
    if mode == "public":
        out.append(finding(HOST, "host-platform", "NOT_VERIFIED",
                           "public host prescribes Linux/systemd (deploy/inquiry/README.md); "
                           "checks run on %s certify nothing about that host" % system))
    else:
        out.append(finding(LOCAL, "local-platform", "OK", system))
    return out


def check_secrets(mode):
    out = []
    token = os.environ.get("MPN_OPERATOR_TOKEN")
    if token is None or token == "":
        out.append(finding(CONFIGURATION, "operator-token", "MISSING",
                           "set MPN_OPERATOR_TOKEN privately (tools/web_inquiry/README.md)",
                           blocking=True))
    elif len(token) < 32 or not token.isascii():
        out.append(finding(CONFIGURATION, "operator-token", "INVALID",
                           "does not meet the documented token policy; generate a new "
                           "private token (tools/web_inquiry/README.md)", blocking=True))
    else:
        out.append(finding(CONFIGURATION, "operator-token", "CONFIGURED",
                           "present and meets the documented policy (value never shown)"))

    if os.environ.get("OPENAI_API_KEY"):
        out.append(finding(CONFIGURATION, "openai-api-key", "CONFIGURED",
                           "present (presence only - NOT proof the reported HTTP 429 "
                           "ended; a synthetic model-backed test must succeed)"))
    else:
        out.append(finding(CONFIGURATION, "openai-api-key", "ABSENT",
                           "offline drafting only until configured privately"))
    model = os.environ.get("MPN_MODEL", "")
    out.append(finding(CONFIGURATION, "model-selection",
                       "CONFIGURED" if model else "ABSENT",
                       model or "MPN_MODEL not set; offline fallback is the only path"))
    out.append(finding(HOST, "model-access", "NOT_VERIFIED",
                       "last supplied live result was HTTP 429 with offline fallback; "
                       "requires one successful synthetic model-backed draft in the "
                       "configured runtime"))
    return out


def check_origin(mode, origin):
    if mode == "demo":
        raw = os.environ.get("MPN_PUBLIC_ORIGIN")
        if raw is None:
            return [finding(LOCAL, "public-origin", "NOT_APPLICABLE",
                            "no override; server uses its loopback HTTP origin")]
        valid = False
        try:
            parts = urllib.parse.urlsplit(raw)
            port = parts.port
            host = parts.hostname or ""
            canonical = "http://" + host + ("" if port is None else ":%d" % port)
            valid = (raw == canonical and parts.scheme == "http"
                     and host in ("localhost", "127.0.0.1")
                     and port not in (0, 80))
        except ValueError:
            pass
        if not valid:
            return [finding(CONFIGURATION, "public-origin", "INVALID",
                            "MPN_PUBLIC_ORIGIN must be a canonical loopback HTTP "
                            "origin for the direct demo; unset it to use the "
                            "server default (value not shown)", blocking=True)]
        return [finding(CONFIGURATION, "public-origin", "CONFIGURED",
                        "canonical loopback HTTP override; match the server port "
                        "and browser URL to it (reachability not verified)")]
    if not origin:
        return [finding(CONFIGURATION, "public-origin", "MISSING",
                        "--origin is required in public mode (exact external HTTPS origin)",
                        blocking=True)]

    def invalid(detail):
        return [finding(CONFIGURATION, "public-origin", "INVALID", detail,
                        blocking=True)]

    if any(ord(ch) < 33 or ord(ch) == 127 for ch in origin):
        return invalid("origin contains whitespace or control characters")
    try:
        parts = urllib.parse.urlsplit(origin)
        port = parts.port  # raises ValueError for a malformed port
    except ValueError:
        return invalid("unparseable origin")
    host = parts.hostname or ""
    problems = []
    if parts.scheme != "https":
        problems.append("must be https")
    if not host:
        problems.append("missing hostname")
    if parts.path or parts.query or parts.fragment or "@" in parts.netloc:
        problems.append("must be a bare origin with no path, query, or credentials")
    if host and (not host.isascii() or "%" in host or "xn--" in host):
        problems.append("hostname must be plain ASCII with no encoded or punycode form")
    if host.endswith("."):
        problems.append("trailing dot is not the canonical form browsers send")
    if host and (any(token in host for token in PLACEHOLDER_TOKENS)
                 or host.endswith(PLACEHOLDER_TLDS)):
        problems.append("placeholder hostname is not a launch origin")
    if host:
        try:
            ipaddress.ip_address(host)
            problems.append("IP-literal origin is not the documented topology")
        except ValueError:
            pass
    if host and "." not in host:
        problems.append("hostname is not a public domain")
    if port == 443:
        problems.append("omit the default port - browsers send the origin without :443")
    if not problems:
        canonical = "https://" + host + ("" if port is None else ":%d" % port)
        if origin != canonical:
            # server.py compares the browser Origin header exactly; a
            # non-canonical serialization would 403 every real submission.
            problems.append("must be written exactly as the canonical origin "
                            "the browser sends: %s" % canonical)
    if problems:
        return invalid("; ".join(problems))
    out = [finding(CONFIGURATION, "public-origin", "CONFIGURED",
                   "%s (set MPN_PUBLIC_ORIGIN to exactly this on the host; DNS, "
                   "certificate, and routing remain owner/host work)" % origin),
           finding(HOST, "host-tls", "NOT_VERIFIED",
                   "certificate and HTTPS routing must be verified on the host")]
    local_env = os.environ.get("MPN_PUBLIC_ORIGIN")
    if local_env and local_env != origin:
        out.append(finding(CONFIGURATION, "public-origin-env", "MISMATCH",
                           "this shell's MPN_PUBLIC_ORIGIN differs from --origin; the "
                           "HOST environment must carry exactly the approved origin"))
    return out


def check_trusted_proxy(mode):
    raw = os.environ.get("MPN_TRUSTED_PROXY_IP")
    if not raw:
        if mode == "demo":
            return [finding(LOCAL, "trusted-proxy", "NOT_APPLICABLE",
                            "not required for the loopback demo")]
        return [finding(CONFIGURATION, "trusted-proxy", "MISSING",
                        "MPN_TRUSTED_PROXY_IP is required for the single-host nginx "
                        "topology (deploy/inquiry/README.md)", blocking=True)]
    if mode == "demo":
        return [finding(CONFIGURATION, "trusted-proxy", "INVALID",
                        "unset MPN_TRUSTED_PROXY_IP for the direct loopback demo; "
                        "browser requests do not carry the required proxy header",
                        blocking=True)]
    # The server validates the EXACT value and refuses startup otherwise -
    # no stripping here, or the preflight would green-light a value the
    # service rejects.
    try:
        address = ipaddress.ip_address(raw)
    except ValueError:
        return [finding(CONFIGURATION, "trusted-proxy", "INVALID",
                        "not a valid IP address exactly as written (no extra "
                        "whitespace); the server refuses to start with this value",
                        blocking=True)]
    if str(address) != "127.0.0.1":
        return [finding(CONFIGURATION, "trusted-proxy", "INVALID",
                        "documented single-host topology expects 127.0.0.1; a different "
                        "proxy address needs its own reviewed topology", blocking=True)]
    return [finding(CONFIGURATION, "trusted-proxy", "CONFIGURED", "127.0.0.1")]


def check_data_dir(raw, timeout):
    out = []
    if raw.startswith(("\\\\", "//")):
        out.append(finding(LOCAL, "data-dir-safety", "INVALID",
                           "UNC paths are not supported; use a direct local drive path",
                           blocking=True))
        return out
    absolute = Path(os.path.normpath(os.path.abspath(os.path.expanduser(raw))))
    resolved = Path(os.path.realpath(absolute))
    if resolved == ROOT or ROOT in resolved.parents or absolute == ROOT or ROOT in absolute.parents:
        out.append(finding(LOCAL, "data-dir-safety", "INVALID",
                           "private state must live outside the repository", blocking=True))
        return out
    if str(resolved).lower() != str(absolute).lower():
        out.append(finding(LOCAL, "data-dir-safety", "INVALID",
                           "path resolves differently than written (link, junction, or "
                           "8.3 short name); use the direct full path of a private "
                           "directory", blocking=True))
        return out
    if not resolved.is_dir():
        out.append(finding(LOCAL, "data-dir", "MISSING",
                           "directory does not exist (this tool never creates it)",
                           blocking=True))
        return out
    out.append(finding(LOCAL, "data-dir-safety", "OK",
                       "outside the repository, no link indirection"))
    database = resolved / "inquiries.sqlite3"
    if not database.is_file():
        out.append(finding(LOCAL, "queue-database", "MISSING",
                           "inquiries.sqlite3 not found; point at the correct private "
                           "directory (never a fresh one to fake readiness)", blocking=True))
        return out
    try:
        result = maintenance.check(database, timeout=timeout)
        counts = result.get("counts", {})
        out.append(finding(LOCAL, "queue-database", "OK",
                           "read-only validation passed; rows: %s" % json.dumps(counts, sort_keys=True)))
    except maintenance.MaintenanceError as error:
        out.append(finding(LOCAL, "queue-database", "INVALID",
                           "read-only validation failed: %s" % error.status, blocking=True))
    out.append(finding(HOST, "storage-persistence", "NOT_VERIFIED",
                       "whether this mount survives reboot cannot be checked here; "
                       "verify on the host and complete the restore drill"))
    return out


def check_deploy_templates(mode):
    if mode == "demo":
        return [finding(LOCAL, "deploy-templates", "NOT_APPLICABLE",
                        "not needed for the loopback demo")]
    directory = ROOT / "deploy" / "inquiry"
    expected = ["README.md", "inquiry.env.example", "nginx.conf.example"]
    missing = [name for name in expected if not (directory / name).is_file()]
    units = sorted(p.name for p in directory.glob("*.service")) + \
        sorted(p.name for p in directory.glob("*.timer")) if directory.is_dir() else []
    if missing or not units:
        detail = "missing: %s" % ", ".join(missing + ([] if units else ["systemd units"]))
        return [finding(CONFIGURATION, "deploy-templates", "INVALID", detail, blocking=True)]
    return [finding(CONFIGURATION, "deploy-templates", "CONFIGURED",
                    "present locally (%d unit files); installation on the host is "
                    "separate work" % len(units)),
            finding(HOST, "reboot-persistence", "NOT_VERIFIED",
                    "systemd units must be installed, enabled, and survive a reboot "
                    "on the actual host"),
            finding(HOST, "alert-delivery", "NOT_VERIFIED",
                    "an owner-approved alert destination for failed health/backup "
                    "units must be configured and tested"),
            finding(HOST, "off-host-restore", "NOT_VERIFIED",
                    "encrypted off-host backup copy and a completed restore drill "
                    "are required before real intake")]


def check_features(pricing_path=PRICING_PATH):
    out = []
    link = ""
    try:
        pricing = json.loads(Path(pricing_path).read_text(encoding="utf-8"))
        link = str(pricing.get("payment", {}).get("stripe_payment_link") or "")
    except (OSError, ValueError):
        pass
    if link.startswith(STRIPE_LINK_PREFIX):
        out.append(finding(FEATURES, "stripe-payment-link", "CONFIGURED", link))
    elif link:
        # Never echo an unexpected value - it should not be there at all.
        out.append(finding(FEATURES, "stripe-payment-link", "INVALID",
                           "pricing.json holds a value that is not a public "
                           "buy.stripe.com link; review it (value not shown)"))
    else:
        out.append(finding(FEATURES, "stripe-payment-link", "PENDING",
                           "no public Payment Link exists; the operator creates one in "
                           "Stripe and pastes the real URL - never a placeholder. Not a "
                           "blocker for the assisted inquiry reply"))
    out.append(finding(FEATURES, "phone-provider", "PENDING",
                       "%s is T-Mobile with manual voice/text only; no automated calls "
                       "or SMS are proven and no transfer/forwarding changes are "
                       "planned. Not a blocker for the assisted inquiry reply" % PUBLIC_PHONE))
    return out


def run(mode, origin, data_dir, timeout):
    findings = []
    findings += check_runtime(mode)
    findings += check_secrets(mode)
    findings += check_origin(mode, origin)
    findings += check_trusted_proxy(mode)
    findings += check_data_dir(data_dir, timeout)
    findings += check_deploy_templates(mode)
    findings += check_features()
    blocking = [f["check"] for f in findings if f["blocking"]]
    return {"mode": mode, "findings": findings, "blocking": blocking,
            "exit": 1 if blocking else 0}


def render(report):
    lines = ["MIAMI PAPA NOEL LAUNCH PREFLIGHT (%s mode, read-only)" % report["mode"],
             "=" * 64]
    if report["blocking"]:
        lines.append("BLOCKING: " + ", ".join(report["blocking"]))
        lines.append("-" * 64)
    for section in (CONFIGURATION, LOCAL, HOST, FEATURES):
        rows = [f for f in report["findings"] if f["section"] == section]
        if not rows:
            continue
        lines.append(section.upper())
        for f in rows:
            marker = "!!" if f["blocking"] else "  "
            lines.append("%s %-22s %-13s %s" % (marker, f["check"], f["status"], f["detail"]))
    lines.append("=" * 64)
    if report["exit"] == 0:
        lines.append("RESULT: no blocking findings for %s mode." % report["mode"])
    else:
        lines.append("RESULT: %d blocking finding(s). Fix before proceeding."
                     % len(report["blocking"]))
    lines.append("This tool never certifies a public launch, model access, or a")
    lines.append("qualification clock. Items under '%s'" % HOST)
    lines.append("must be verified where they actually run.")
    return "\n".join(lines)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        # Never echo argument values: a secret pasted into the wrong argv
        # slot must not land in captured stderr (same rule as maintenance.py).
        print("usage error: check the arguments and run --help "
              "(values are not echoed)", file=sys.stderr)
        raise SystemExit(2)


def main(argv=None):
    parser = Parser(description=__doc__.splitlines()[0], allow_abbrev=False)
    parser.add_argument("--mode", required=True, choices=("demo", "public"),
                        help="demo = local loopback readiness; public = host prerequisites")
    parser.add_argument("--data-dir", required=True,
                        help="existing private data directory (never created here)")
    parser.add_argument("--origin", default="",
                        help="exact external HTTPS origin (public mode)")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--timeout", type=float, default=maintenance.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    report = run(args.mode, args.origin, args.data_dir, args.timeout)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.as_json
          else render(report))
    return report["exit"]


if __name__ == "__main__":
    raise SystemExit(main())
