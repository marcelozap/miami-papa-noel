#!/usr/bin/env python3
"""Fail-closed OpenAI Partner Network submission validator for Miami Papa Noel.

    python scripts/validate_opn_submission.py --preflight
    python scripts/validate_opn_submission.py --final

--preflight reports every gap but exits 0 unless a hard defect exists
(privacy violation, contaminated log, failing test suite, broken JSON).
--final fails closed: it exits non-zero until every submission requirement
is satisfied by real, dated evidence. Placeholders, guessed model names,
guessed dates, missing production days, and unsupported claims all block.

Standard library only. ASCII output only (Windows consoles).

The production log and evidence folder live OUTSIDE the repository:
    log:      %MPN_LOG_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\triage\\production-log.jsonl
    evidence: %MPN_EVIDENCE_DIR%  or  %LOCALAPPDATA%\\MiamiPapaNoel\\evidence\\

This tool never creates, edits, or backdates evidence. --init-evidence only
scaffolds empty directories and an empty index header. See docs/OPN-VALIDATION.md.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

FAIL = "FAIL"
WARN = "WARN"
INFO = "INFO"

QUALIFYING_DAYS = 15

# --------------------------------------------------------------- inventory --

REQUIRED_DOCS = [
    "docs/OPN-SUBMISSION.md",
    "docs/production-deployment-record.md",
    "docs/agent-workflow-architecture.md",
    "docs/release-monitoring-and-failure-handling.md",
    "docs/evidence-index.md",
    "docs/gap-report.md",
    "docs/operator-attestation-2025-season.md",
    "docs/release-checklist.md",
    "docs/15-day-evidence-checklist.md",
    "docs/evidence-intake.md",
    "docs/OPN-VALIDATION.md",
    "docs/evidence-manifest-schema.md",
    "scripts/evidence_index.py",
    "scripts/test_evidence_index.py",
]

REQUIRED_TRIAGE_FILES = [
    "tools/triage/triage.py",
    "tools/triage/validators.py",
    "tools/triage/pricing.json",
    "tools/triage/test_triage.py",
    "tools/triage/README.md",
    "tools/triage/log-schema.md",
]

# Docs whose open placeholders block a --final run. Everything else warns.
STRICT_DOCS = ["docs/OPN-SUBMISSION.md", "docs/production-deployment-record.md"]

# Docs excluded from placeholder/count scans because they document the
# placeholder convention itself.
SCAN_EXCLUDED_DOCS = {"docs/OPN-VALIDATION.md"}

SUBMISSION_DOC = "docs/OPN-SUBMISSION.md"

COVERAGE_PATTERNS = {
    "operational owner": r"operational\s+owner",
    "live AI functionality": r"live\s+ai\s+functionality|##\s*what\s+is\s+live",
    "production model": r"production\s+model",
    "concrete outcome": r"concrete\s+outcome",
    "testing and release approval": r"testing\s+and\s+release\s+approval",
    "monitoring": r"monitoring",
    "failure handling": r"failure\s+handling",
    "production status / 15-day duration": r"15[\s-]?day|15\s+days",
}

# ------------------------------------------------------------- log schema ---

LOG_REQUIRED_KEYS = [
    "inquiry_id", "received_at", "channel", "language", "requested_date",
    "category", "missing_fields", "model", "prompt_version", "reviewer",
    "approved_at", "sent_at", "fallback_used", "outcome", "error_code",
    "real_customer",
]

LOG_OUTCOMES = {
    "pending_review", "approved_awaiting_send", "approved_and_sent",
    "rejected_by_operator", "blocked_by_validation",
}

# Keys that must never appear in a log record (privacy).
FORBIDDEN_LOG_KEYS = {
    "draft_en", "draft_es", "message", "message_text", "inquiry_text",
    "customer", "customer_name", "phone", "email", "address", "memo",
    "payment_memo",
}

PHONE_RE = re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]?\d{4}\b|\b\d{10}\b")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
STREET_RE = re.compile(
    r"\b\d{1,6}\s+\w+\s+(?:st|street|ave|avenue|rd|road|dr|drive|ln|lane|"
    r"ct|court|blvd|boulevard|ter|terrace|pl|place|way|cir|circle)\b",
    re.IGNORECASE,
)

# ------------------------------------------------------- claim-drift scans --

MODEL_NAME_RE = re.compile(
    r"\b(gpt-[\w.]+|chatgpt[\w.-]*|claude-[\w.-]+|gemini[\w.-]*|llama[\w.-]*|"
    r"mistral[\w.-]*|deepseek[\w.-]*)\b",
    re.IGNORECASE,
)
# Models that are legitimate without appearing in the production log.
LOCAL_MODEL_IDS = {"offline-rules-v1", "manual"}

TEST_COUNT_RES = [
    re.compile(r"(\d+)\s+pass(?:ed|ing)\s+tests?"),
    re.compile(r"#\s*(\d+)\s+passed\b"),
    re.compile(r"(\d+)\s+passed\b"),
]

LAUNCH_LINE_RE = re.compile(r"launch\s+date|first\s+real\s+(?:customer\s+)?inquiry", re.IGNORECASE)
ISO_DATE_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
PLACEHOLDER_RE = re.compile(r"\[TO FILL[^\]]*\]|\[VERIFY[^\]]*\]|\[NOT YET MET\]")

# ---------------------------------------------------------- surface scans ---

NON_ZELLE_RE = re.compile(
    r"\b(venmo|cash\s?app|paypal|stripe|square|apple\s?pay|google\s?pay|"
    r"wire\s+transfer|credit\s+card|debit\s+card|zinli)\b",
    re.IGNORECASE,
)
RETIRED_EMAIL = "bookings@miamipapanoel.com"
INSURANCE_RE = re.compile(
    r"\binsurance\b|\binsured\b|general\s+liability|certificate\s+of\s+insurance|"
    r"additional\s+insured|liability\s+(?:policy|insurance)|\$\s*1M\b|"
    r"\bCOI\b|asegurad|p[oó]liza|cobertura\s+de\s+seguro|seguro\s+de\s+responsabilidad",
    re.IGNORECASE,
)
COI_RE = re.compile(r"\bCOI\b")  # case-sensitive on purpose
PRICE_RE = re.compile(r"\$\s?(\d{1,4})\b(?![MKmk])")
POLICY_VERIFIED_RE = re.compile(r"policy\s+verified\s*:\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE)

INSURANCE_PREFLIGHT_DOC = "business/insurance-and-wave1-preflight.md"

PUBLIC_SURFACE_PATHS = [
    "index.html", "book.html", "checkout.html", "christmas-eve.html",
    "events.html", "hoa-apartments.html", "schools-daycares.html",
    "service-areas.html", "partners.html", "links.html", "reviews.html",
    "after-visit.html", "summer-santa.html", "business/content-engine.html",
]


class Finding:
    def __init__(self, level: str, area: str, detail: str):
        self.level = level
        self.area = area
        self.detail = detail

    def as_dict(self) -> dict:
        return {"level": self.level, "area": self.area, "detail": self.detail}


class Config:
    def __init__(self, repo_root: Path, final: bool, today: dt.date | None = None,
                 log_path: Path | None = None, evidence_dir: Path | None = None,
                 run_external: bool = True):
        self.repo_root = Path(repo_root)
        self.final = final
        self.today = today or dt.date.today()
        self.log_path = Path(log_path) if log_path else default_log_path()
        self.evidence_dir = Path(evidence_dir) if evidence_dir else default_evidence_dir()
        self.run_external = run_external


def default_log_path() -> Path:
    override = os.environ.get("MPN_LOG_DIR")
    if override:
        return Path(override) / "production-log.jsonl"
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "triage" / "production-log.jsonl"


def default_evidence_dir() -> Path:
    override = os.environ.get("MPN_EVIDENCE_DIR")
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / "MiamiPapaNoel" / "evidence"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def gate(cfg: Config) -> str:
    """Severity for findings that block --final but only warn in --preflight."""
    return FAIL if cfg.final else WARN


# ------------------------------------------------------------------ checks --

def check_required_files(cfg: Config) -> list:
    findings = []
    for rel in REQUIRED_DOCS + REQUIRED_TRIAGE_FILES:
        if not (cfg.repo_root / rel).is_file():
            findings.append(Finding(FAIL, "files", "missing required file: %s" % rel))
    if not findings:
        findings.append(Finding(INFO, "files", "all %d required files present"
                                % (len(REQUIRED_DOCS) + len(REQUIRED_TRIAGE_FILES))))
    return findings


def check_submission_coverage(cfg: Config) -> list:
    path = cfg.repo_root / SUBMISSION_DOC
    if not path.is_file():
        return [Finding(FAIL, "coverage", "%s missing; coverage not checkable" % SUBMISSION_DOC)]
    text = read_text(path)
    findings = []
    for label, pattern in COVERAGE_PATTERNS.items():
        if not re.search(pattern, text, re.IGNORECASE):
            findings.append(Finding(FAIL, "coverage",
                                    "%s does not cover: %s" % (SUBMISSION_DOC, label)))
    if not findings:
        findings.append(Finding(INFO, "coverage",
                                "%s covers all %d required topics"
                                % (SUBMISSION_DOC, len(COVERAGE_PATTERNS))))
    return findings


def check_placeholders(cfg: Config) -> list:
    findings = []
    for rel in REQUIRED_DOCS:
        if rel in SCAN_EXCLUDED_DOCS:
            continue
        path = cfg.repo_root / rel
        if not path.is_file():
            continue
        hits = PLACEHOLDER_RE.findall(read_text(path))
        if not hits:
            continue
        strict = rel in STRICT_DOCS
        level = gate(cfg) if strict else WARN
        findings.append(Finding(level, "placeholders",
                                "%s has %d open placeholder(s)%s"
                                % (rel, len(hits),
                                   " [blocks --final]" if strict else "")))
    if cfg.final:
        gap = cfg.repo_root / "docs/gap-report.md"
        if gap.is_file() and re.search(r"\*\*NOT MET\*\*", read_text(gap)):
            findings.append(Finding(FAIL, "placeholders",
                                    "docs/gap-report.md still lists a requirement as NOT MET"))
    if not findings:
        findings.append(Finding(INFO, "placeholders", "no open placeholders in required docs"))
    return findings


def check_model_name_claims(cfg: Config, log_models: set) -> list:
    findings = []
    permitted = {m.lower() for m in (log_models | LOCAL_MODEL_IDS)}
    for rel in STRICT_DOCS:
        path = cfg.repo_root / rel
        if not path.is_file():
            continue
        for name in set(MODEL_NAME_RE.findall(read_text(path))):
            if name.lower() not in permitted:
                findings.append(Finding(gate(cfg), "claims",
                                        "%s names model %r which never appears in the "
                                        "production log" % (rel, name)))
    if not findings:
        findings.append(Finding(INFO, "claims", "no unsupported model names in strict docs"))
    return findings


def check_date_claims(cfg: Config, earliest: dt.date | None) -> list:
    findings = []
    for rel in STRICT_DOCS:
        path = cfg.repo_root / rel
        if not path.is_file():
            continue
        for line in read_text(path).splitlines():
            if not LAUNCH_LINE_RE.search(line):
                continue
            if re.search(r"\bif\s+started\b|\bexample\b|\bfor\s+example\b|ready\s+for\s+first\b", line, re.IGNORECASE):
                continue
            for raw in ISO_DATE_RE.findall(line):
                claimed = dt.date.fromisoformat(raw)
                if earliest is None:
                    findings.append(Finding(gate(cfg), "claims",
                                            "%s asserts launch/first-inquiry date %s but no "
                                            "production log exists" % (rel, raw)))
                elif claimed != earliest:
                    findings.append(Finding(FAIL, "claims",
                                            "%s asserts launch date %s but the earliest "
                                            "production record is %s"
                                            % (rel, raw, earliest.isoformat())))
    if not findings:
        findings.append(Finding(INFO, "claims", "no contradicted launch dates in strict docs"))
    return findings


def check_test_count_claims(cfg: Config, actual_passed: int | None) -> list:
    if actual_passed is None:
        return [Finding(WARN, "claims", "triage suite not run; test-count claims unchecked")]
    findings = []
    scan_files = [cfg.repo_root / rel for rel in REQUIRED_DOCS
                  if rel not in SCAN_EXCLUDED_DOCS]
    scan_files.append(cfg.repo_root / "docs/demo-runbook.md")
    scan_files.append(cfg.repo_root / "tools/triage/README.md")
    for path in scan_files:
        if not path.is_file():
            continue
        text = read_text(path)
        claimed = set()
        for rx in TEST_COUNT_RES:
            claimed.update(int(n) for n in rx.findall(text))
        for n in sorted(claimed):
            if n != actual_passed:
                findings.append(Finding(gate(cfg), "claims",
                                        "%s claims %d passing tests; the triage suite "
                                        "actually passes %d"
                                        % (path.relative_to(cfg.repo_root), n, actual_passed)))
    if not findings:
        findings.append(Finding(INFO, "claims",
                                "every test-count claim matches the suite (%d passed)"
                                % actual_passed))
    return findings


def _scan_private_values(value, path="") -> list:
    """Recursively scan a JSON value for phone/email/street-address strings."""
    hits = []
    if isinstance(value, dict):
        for k, v in value.items():
            hits.extend(_scan_private_values(v, path + "." + str(k)))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            hits.extend(_scan_private_values(v, "%s[%d]" % (path, i)))
    elif isinstance(value, str):
        if PHONE_RE.search(value):
            hits.append("phone-number-like value at %s" % path)
        if EMAIL_RE.search(value):
            hits.append("email-address-like value at %s" % path)
        if STREET_RE.search(value):
            hits.append("street-address-like value at %s" % path)
    return hits


def check_production_log(cfg: Config):
    """Returns findings, earliest date, models, approved/sent count, model-backed flag."""
    findings = []
    path = cfg.log_path
    if not path.is_file():
        level = FAIL if cfg.final else WARN
        findings.append(Finding(level, "log",
                                "no production log at %s (clock not started)" % path))
        return findings, None, set(), 0, False

    earliest = None
    models = set()
    approved_sent = 0
    model_backed = False
    records = 0
    for lineno, line in enumerate(read_text(path).splitlines(), 1):
        if not line.strip():
            continue
        records += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            findings.append(Finding(FAIL, "log", "line %d is not valid JSON" % lineno))
            continue
        if not isinstance(rec, dict):
            findings.append(Finding(FAIL, "log", "line %d is not a JSON object" % lineno))
            continue

        missing = [k for k in LOG_REQUIRED_KEYS if k not in rec]
        if missing:
            findings.append(Finding(FAIL, "log",
                                    "line %d missing required key(s): %s"
                                    % (lineno, ", ".join(missing))))

        bad_keys = FORBIDDEN_LOG_KEYS & set(rec.keys())
        if bad_keys:
            findings.append(Finding(FAIL, "log-privacy",
                                    "line %d contains forbidden key(s): %s"
                                    % (lineno, ", ".join(sorted(bad_keys)))))
        for hit in _scan_private_values(rec, "$"):
            findings.append(Finding(FAIL, "log-privacy", "line %d: %s" % (lineno, hit)))

        if rec.get("real_customer") is not True:
            findings.append(Finding(FAIL, "log",
                                    "line %d: real_customer is not true - synthetic data "
                                    "in the production log" % lineno))

        received = rec.get("received_at")
        try:
            received_date = dt.datetime.fromisoformat(received).date()
            if earliest is None or received_date < earliest:
                earliest = received_date
        except (TypeError, ValueError):
            findings.append(Finding(FAIL, "log",
                                    "line %d: received_at %r is not an ISO timestamp"
                                    % (lineno, received)))

        outcome = rec.get("outcome")
        if outcome not in LOG_OUTCOMES:
            findings.append(Finding(FAIL, "log",
                                    "line %d: unknown outcome %r" % (lineno, outcome)))
        if outcome == "approved_and_sent":
            empty = [f for f in ("reviewer", "approved_at", "sent_at") if not rec.get(f)]
            for field in empty:
                findings.append(Finding(FAIL, "log",
                                        "line %d: outcome approved_and_sent but %s "
                                        "is empty" % (lineno, field)))
            if not empty:
                approved_sent += 1
                if (rec.get("fallback_used") is False
                        and rec.get("model") not in {"", "offline-rules-v1", "manual"}):
                    model_backed = True

        if not isinstance(rec.get("fallback_used"), bool):
            findings.append(Finding(FAIL, "log",
                                    "line %d: fallback_used is not a boolean" % lineno))
        model = rec.get("model")
        if isinstance(model, str) and model:
            models.add(model)
        else:
            findings.append(Finding(FAIL, "log", "line %d: model is empty" % lineno))

    if records == 0:
        level = FAIL if cfg.final else WARN
        findings.append(Finding(level, "log", "production log exists but holds no records"))
        return findings, None, models, 0, model_backed

    findings.append(Finding(INFO, "log",
                            "%d production record(s); models: %s; approved+sent: %d"
                            % (records, ", ".join(sorted(models)) or "-", approved_sent)))
    return findings, earliest, models, approved_sent, model_backed


def check_duration(cfg: Config, earliest: dt.date | None, approved_sent: int,
                    model_backed: bool) -> list:
    findings = []
    if earliest is None:
        if cfg.final:
            findings.append(Finding(FAIL, "duration",
                                    "15-day requirement NOT MET: no real production "
                                    "record exists"))
            findings.append(Finding(FAIL, "outcome",
                                    "no approved_and_sent record exists; there is no concrete outcome to report"))
            findings.append(Finding(FAIL, "model",
                                    "no real non-fallback model record was approved and sent"))
        else:
            findings.append(Finding(INFO, "duration",
                                    "clock not started; qualification is first real "
                                    "inquiry + %d days" % QUALIFYING_DAYS))
        return findings

    elapsed = (cfg.today - earliest).days
    qualify_on = earliest + dt.timedelta(days=QUALIFYING_DAYS)
    if elapsed >= QUALIFYING_DAYS:
        findings.append(Finding(INFO, "duration",
                                "first real inquiry %s; %d day(s) elapsed; 15-day "
                                "requirement met on %s"
                                % (earliest.isoformat(), elapsed, qualify_on.isoformat())))
    else:
        level = FAIL if cfg.final else INFO
        findings.append(Finding(level, "duration",
                                "first real inquiry %s; only %d day(s) elapsed; "
                                "qualifies on %s"
                                % (earliest.isoformat(), elapsed, qualify_on.isoformat())))
    if cfg.final and approved_sent == 0:
        findings.append(Finding(FAIL, "duration",
                                "no approved_and_sent record exists; there is no "
                                "concrete outcome to report"))
    if cfg.final and not model_backed:
        findings.append(Finding(FAIL, "model",
                                "no real non-fallback model record was approved and sent"))
    return findings


EVIDENCE_INDEX_KEYS = ["ref", "type", "date", "artifact", "sha256", "redacted", "notes"]
EVIDENCE_TYPES = {"receipt", "booking_record", "message_thread", "screenshot",
                  "statement", "calendar", "zelle_history"}
EVIDENCE_FORBIDDEN_KEYS = {"name", "customer_name", "phone", "email", "address",
                           "memo", "payment_memo", "message_text", "raw_text"}


def check_evidence_dir(cfg: Config) -> list:
    findings = []
    root = cfg.evidence_dir
    if not root.is_dir():
        findings.append(Finding(gate(cfg), "evidence",
                                "evidence directory absent: %s (required for the final packet)" % root))
        return findings
    index = root / "evidence-index.jsonl"
    if not index.is_file():
        findings.append(Finding(gate(cfg), "evidence",
                                "evidence directory exists but has no evidence-index.jsonl"))
        return findings
    entries = 0
    refs = set()
    types = set()
    errors = []
    for lineno, line in enumerate(read_text(index).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        entries += 1
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d is not valid JSON" % lineno))
            continue
        if not isinstance(rec, dict):
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d is not an object" % lineno))
            continue
        missing = [k for k in EVIDENCE_INDEX_KEYS if k not in rec]
        if missing:
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d missing key(s): %s"
                                    % (lineno, ", ".join(missing))))
            continue
        ref = str(rec.get("ref", ""))
        if not ref or ref in refs:
            errors.append("line %d has a duplicate or empty ref" % lineno)
        refs.add(ref)
        artifact_type = rec.get("type")
        if artifact_type not in EVIDENCE_TYPES:
            errors.append("line %d (%s) has unsupported type %r" % (lineno, ref, artifact_type))
        else:
            types.add(artifact_type)
        if set(rec) & EVIDENCE_FORBIDDEN_KEYS:
            errors.append("line %d (%s) includes a private-data field" % (lineno, ref))
        errors.extend("line %d (%s): %s" % (lineno, ref, hit)
                      for hit in _scan_private_values(rec, "evidence"))
        if rec.get("redacted") is not True:
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d (%s): redacted is not true - do not "
                                    "index unredacted material" % (lineno, rec.get("ref"))))
        if not re.fullmatch(r"[0-9a-fA-F]{64}", str(rec.get("sha256", ""))):
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d (%s): sha256 is not 64 hex chars"
                                    % (lineno, rec.get("ref"))))
            continue
        try:
            dt.date.fromisoformat(str(rec.get("date")))
        except ValueError:
            findings.append(Finding(FAIL, "evidence",
                                    "index line %d (%s): date is not ISO YYYY-MM-DD"
                                    % (lineno, rec.get("ref"))))
        raw_artifact = rec.get("artifact")
        if not isinstance(raw_artifact, str) or not raw_artifact.strip():
            errors.append("line %d (%s): artifact path is empty" % (lineno, ref))
            continue
        artifact_rel = Path(raw_artifact)
        if artifact_rel.is_absolute() or ".." in artifact_rel.parts:
            errors.append("line %d (%s): artifact path must stay inside evidence folder" % (lineno, ref))
            continue
        artifact = (root / artifact_rel).resolve()
        try:
            artifact.relative_to(root.resolve())
        except ValueError:
            errors.append("line %d (%s): artifact path escapes evidence folder" % (lineno, ref))
            continue
        if artifact.is_file():
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            if digest.lower() != str(rec["sha256"]).lower():
                findings.append(Finding(FAIL, "evidence",
                                        "index line %d (%s): sha256 mismatch for %s"
                                        % (lineno, rec.get("ref"), rec["artifact"])))
        else:
            findings.append(Finding(gate(cfg), "evidence",
                                    "index line %d (%s): artifact file not found: %s"
                                    % (lineno, rec.get("ref"), rec["artifact"])))
    if errors:
        findings.append(Finding(FAIL, "evidence", "; ".join(errors[:10])))
    if entries == 0:
        findings.append(Finding(gate(cfg), "evidence", "evidence index has no artifacts"))
    elif cfg.final and not (types & {"receipt", "statement"}):
        findings.append(Finding(FAIL, "evidence",
                                "final evidence must include at least one receipt or statement"))
    findings.append(Finding(INFO, "evidence", "evidence index holds %d entr(ies)" % entries))
    return findings


def _policy_verified(cfg: Config) -> bool:
    path = cfg.repo_root / INSURANCE_PREFLIGHT_DOC
    return path.is_file() and bool(POLICY_VERIFIED_RE.search(read_text(path)))


def check_public_surfaces(cfg: Config) -> list:
    findings = []
    pricing_path = cfg.repo_root / "tools/triage/pricing.json"
    allowed = set()
    if pricing_path.is_file():
        try:
            allowed = set(json.loads(read_text(pricing_path)).get("allowed_amounts", []))
        except json.JSONDecodeError:
            findings.append(Finding(FAIL, "surfaces", "tools/triage/pricing.json is not valid JSON"))
    else:
        findings.append(Finding(FAIL, "surfaces", "tools/triage/pricing.json missing"))

    policy_ok = _policy_verified(cfg)
    # Every HTML file can become reachable if it is deployed; scan internal
    # demos and planning pages too so stale public copy cannot hide there.
    pages = sorted(cfg.repo_root.rglob("*.html"))
    if not pages:
        findings.append(Finding(WARN, "surfaces", "no root-level HTML pages found to scan"))
    for page in pages:
        rel = str(page.relative_to(cfg.repo_root)).replace("\\", "/")
        for lineno, line in enumerate(read_text(page).splitlines(), 1):
            m = NON_ZELLE_RE.search(line)
            if m:
                findings.append(Finding(FAIL, "surfaces",
                                        "%s:%d non-Zelle payment method %r"
                                        % (rel, lineno, m.group(0))))
            if RETIRED_EMAIL in line:
                findings.append(Finding(FAIL, "surfaces",
                                        "%s:%d references %s (not yet receiving mail)"
                                        % (rel, lineno, RETIRED_EMAIL)))
            if not policy_ok and (INSURANCE_RE.search(line) or COI_RE.search(line)):
                findings.append(Finding(FAIL, "surfaces",
                                        "%s:%d insurance language with no verified policy"
                                        % (rel, lineno)))
            for raw in PRICE_RE.findall(line):
                if allowed and int(raw) not in allowed:
                    findings.append(Finding(FAIL, "surfaces",
                                            "%s:%d price $%s is not in the locked list"
                                            % (rel, lineno, raw)))
    if not [f for f in findings if f.level != INFO]:
        findings.append(Finding(INFO, "surfaces",
                                "%d public page(s) clean: Zelle-only, no retired email, "
                                "no unverified insurance, all prices locked" % len(pages)))
    return findings


def check_external_suites(cfg: Config):
    """Returns (findings, actual_triage_pass_count_or_None)."""
    findings = []
    actual = None
    if not cfg.run_external:
        return [Finding(INFO, "suites", "external suites skipped (run_external=false)")], None

    triage_tests = cfg.repo_root / "tools/triage/test_triage.py"
    if triage_tests.is_file():
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(triage_tests), "-q"],
            capture_output=True, text=True, timeout=300, cwd=str(cfg.repo_root),
        )
        tail = (proc.stdout or "").strip().splitlines()
        summary = tail[-1] if tail else ""
        m = re.search(r"(\d+)\s+passed", summary)
        if proc.returncode == 0 and m:
            actual = int(m.group(1))
            findings.append(Finding(INFO, "suites", "triage suite: %s" % summary))
        else:
            findings.append(Finding(FAIL, "suites",
                                    "triage suite failed (exit %d): %s"
                                    % (proc.returncode, summary or "no output")))
    else:
        findings.append(Finding(WARN, "suites", "tools/triage/test_triage.py not found"))

    validator_tests = cfg.repo_root / "scripts/test_validate_opn_submission.py"
    if validator_tests.is_file():
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(validator_tests), "-q"],
            capture_output=True, text=True, timeout=300, cwd=str(cfg.repo_root),
        )
        summary = ((proc.stdout or "").strip().splitlines() or [""])[-1]
        if proc.returncode == 0:
            findings.append(Finding(INFO, "suites", "submission validator suite: %s" % summary))
        else:
            findings.append(Finding(FAIL, "suites",
                                    "submission validator suite failed (exit %d): %s"
                                    % (proc.returncode, summary or "no output")))
    else:
        findings.append(Finding(WARN, "suites", "scripts/test_validate_opn_submission.py not found"))

    evidence_tests = cfg.repo_root / "scripts/test_evidence_index.py"
    if evidence_tests.is_file():
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(evidence_tests), "-q"],
            capture_output=True, text=True, timeout=300, cwd=str(cfg.repo_root),
        )
        summary = ((proc.stdout or "").strip().splitlines() or [""])[-1]
        if proc.returncode == 0:
            findings.append(Finding(INFO, "suites", "evidence index suite: %s" % summary))
        else:
            findings.append(Finding(FAIL, "suites",
                                    "evidence index suite failed (exit %d): %s"
                                    % (proc.returncode, summary or "no output")))
    else:
        findings.append(Finding(WARN, "suites", "scripts/test_evidence_index.py not found"))

    slot = cfg.repo_root / "scripts/validate_slot_confirmations.py"
    if slot.is_file():
        proc = subprocess.run([sys.executable, str(slot)], capture_output=True,
                              text=True, timeout=120, cwd=str(cfg.repo_root))
        if proc.returncode == 0:
            findings.append(Finding(INFO, "suites",
                                    "slot validator: %s" % (proc.stdout or "").strip()))
        else:
            findings.append(Finding(FAIL, "suites",
                                    "slot validator failed (exit %d)" % proc.returncode))
    else:
        findings.append(Finding(WARN, "suites", "slot validator not found"))
    return findings, actual


GIT_FORBIDDEN_TRACKED = re.compile(
    r"(^|/)\.env(\.|$)|\.pem$|\.key$|\.jsonl$", re.IGNORECASE)
GIT_ALLOWED_TRACKED = {"tools/triage/examples/inquiry-redacted.jsonl"}


def check_git_privacy(cfg: Config) -> list:
    """No secret, key, or log file may ever be tracked in Git."""
    if not (cfg.repo_root / ".git").exists():
        return [Finding(INFO, "git-privacy",
                        "not a git checkout; tracked-file scan skipped")]
    try:
        proc = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                              timeout=60, cwd=str(cfg.repo_root))
    except (OSError, subprocess.TimeoutExpired):
        return [Finding(WARN, "git-privacy",
                        "git unavailable; tracked-file scan skipped")]
    if proc.returncode != 0:
        return [Finding(WARN, "git-privacy",
                        "git ls-files failed; tracked-file scan skipped")]
    offenders = [line for line in proc.stdout.splitlines()
                 if GIT_FORBIDDEN_TRACKED.search(line)
                 and line not in GIT_ALLOWED_TRACKED]
    findings = [Finding(FAIL, "git-privacy",
                        "tracked file must never be in Git: %s" % line)
                for line in offenders]
    if not offenders:
        findings.append(Finding(INFO, "git-privacy",
                                "no .env, .pem, .key, or log files tracked "
                                "(redacted example excepted)"))
    return findings


# ------------------------------------------------------------ orchestration --

def run_validation(cfg: Config) -> list:
    findings = []
    findings += check_required_files(cfg)
    findings += check_submission_coverage(cfg)
    findings += check_placeholders(cfg)
    findings += check_git_privacy(cfg)

    log_findings, earliest, models, approved_sent, model_backed = check_production_log(cfg)
    findings += log_findings
    findings += check_duration(cfg, earliest, approved_sent, model_backed)
    findings += check_model_name_claims(cfg, models)
    findings += check_date_claims(cfg, earliest)

    suite_findings, actual = check_external_suites(cfg)
    findings += suite_findings
    findings += check_test_count_claims(cfg, actual)

    findings += check_evidence_dir(cfg)
    findings += check_public_surfaces(cfg)
    return findings


def init_evidence(evidence_dir: Path) -> None:
    """Scaffold empty evidence directories and an index header. Creates no data."""
    for sub in ("receipts", "messages", "screenshots", "statements"):
        (evidence_dir / sub).mkdir(parents=True, exist_ok=True)
    index = evidence_dir / "evidence-index.jsonl"
    if not index.exists():
        index.write_text(
            "# One JSON object per line. Keys: ref, type, date (YYYY-MM-DD), artifact\n"
            "# (path relative to this folder), sha256 (of the REDACTED file), redacted\n"
            "# (must be true), notes. Never index unredacted material. Never commit\n"
            "# this folder to Git.\n",
            encoding="utf-8",
        )
    print("evidence scaffold ready at %s (no data created)" % evidence_dir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = ap.add_mutually_exclusive_group(required=False)
    mode.add_argument("--preflight", action="store_true",
                      help="report all gaps; exit 0 unless a hard defect exists")
    mode.add_argument("--final", action="store_true",
                      help="fail closed until every requirement is satisfied")
    ap.add_argument("--init-evidence", action="store_true",
                    help="create the empty evidence folder scaffold and exit")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--today", help="override today's date (YYYY-MM-DD), for testing")
    ap.add_argument("--repo-root", default=None, help="repository root (default: cwd)")
    ap.add_argument("--log-dir", default=None, help="external triage log directory")
    ap.add_argument("--evidence-dir", default=None, help="external evidence directory")
    ap.add_argument("--skip-tests", action="store_true", help="skip repository test commands")
    args = ap.parse_args(argv)

    if args.init_evidence:
        init_evidence(Path(args.evidence_dir) if args.evidence_dir else default_evidence_dir())
        return 0
    if not (args.preflight or args.final):
        ap.error("choose a mode: --preflight or --final")

    root = Path(args.repo_root) if args.repo_root else Path.cwd()
    today = dt.date.fromisoformat(args.today) if args.today else None
    log_path = (Path(args.log_dir) / "production-log.jsonl") if args.log_dir else None
    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else None
    cfg = Config(repo_root=root, final=bool(args.final), today=today,
                 log_path=log_path, evidence_dir=evidence_dir,
                 run_external=not args.skip_tests)

    findings = run_validation(cfg)
    fails = [f for f in findings if f.level == FAIL]
    warns = [f for f in findings if f.level == WARN]

    if args.json:
        print(json.dumps({
            "mode": "final" if cfg.final else "preflight",
            "result": "FAIL" if fails else "PASS",
            "findings": [f.as_dict() for f in findings],
        }, indent=2))
        return 1 if fails else 0

    mode_name = "FINAL (fail-closed)" if cfg.final else "PREFLIGHT"
    print("OPN SUBMISSION VALIDATION - %s - %s" % (mode_name, cfg.today.isoformat()))
    print("repo: %s" % cfg.repo_root)
    print("log:  %s" % cfg.log_path)
    print("=" * 72)
    for level in (FAIL, WARN, INFO):
        group = [f for f in findings if f.level == level]
        if not group:
            continue
        print()
        for f in group:
            print("  %-4s %-12s %s" % (f.level, f.area, f.detail))
    print()
    print("=" * 72)
    if fails:
        print("RESULT: FAIL - %d blocking finding(s), %d warning(s)."
              % (len(fails), len(warns)))
        if cfg.final:
            print("The submission is NOT ready. Every blocking finding above must be")
            print("resolved by real evidence. Do not work around this result.")
        return 1
    print("RESULT: PASS - 0 blocking findings, %d warning(s)." % len(warns))
    if not cfg.final:
        print("Preflight passing does NOT mean the submission is ready; run --final.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
