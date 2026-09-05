"""Validation gates for drafted customer replies.

Every draft passes through these before an operator ever sees it. A FAIL blocks
approval; a WARN is shown and the operator decides.

Stdlib only, on purpose: this must keep running with no installs, no network,
and no subscription.
"""
from __future__ import annotations

import re
import unicodedata

FAIL = "FAIL"
WARN = "WARN"
PASS = "PASS"

MONEY = re.compile(r"\$\s?([0-9][0-9,]{1,6})")
# Numbers that legitimately appear in copy without being prices.
NON_PRICE_TOKENS = {"1", "2", "3", "4", "15", "20", "25", "30", "45", "50", "60", "90"}


def _fold(text: str) -> str:
    """Lowercase and strip accents so 'depósito' matches 'deposito'."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


class Finding:
    def __init__(self, check: str, level: str, detail: str):
        self.check = check
        self.level = level
        self.detail = detail

    def __repr__(self) -> str:
        return "%s [%s] %s" % (self.check, self.level, self.detail)

    def as_dict(self) -> dict:
        return {"check": self.check, "level": self.level, "detail": self.detail}


# --------------------------------------------------------------- validators --

def validate_pricing(draft_en: str, draft_es: str, pricing: dict) -> list:
    """Every dollar figure in a draft must exist in the locked price list."""
    allowed = set(pricing["allowed_amounts"])
    findings = []
    for label, draft in (("en", draft_en), ("es", draft_es)):
        for raw in MONEY.findall(draft):
            value = int(raw.replace(",", ""))
            if value not in allowed:
                findings.append(Finding(
                    "pricing",
                    FAIL,
                    "draft_%s quotes $%d, which is not in locked price list %s"
                    % (label, value, pricing["price_list_version"]),
                ))
    if not findings:
        findings.append(Finding(
            "pricing", PASS,
            "all quoted amounts present in locked list %s" % pricing["price_list_version"],
        ))
    return findings


def validate_bilingual_parity(draft_en: str, draft_es: str) -> list:
    """The two languages must carry identical commercial terms.

    A Spanish draft that states a different price, deposit, or duration than its
    English twin is a defect, not a translation choice.
    """
    def numbers(text: str) -> set:
        found = set(MONEY.findall(text))
        return {n.replace(",", "") for n in found}

    en_money, es_money = numbers(draft_en), numbers(draft_es)
    findings = []
    if en_money != es_money:
        findings.append(Finding(
            "bilingual_parity", FAIL,
            "money differs: EN=%s ES=%s" % (sorted(en_money) or "-", sorted(es_money) or "-"),
        ))

    def durations(text: str) -> set:
        raw = re.findall(r"\b(\d{1,3})\s*-?\s*(?:min|minut|hour|hora)", _fold(text))
        return {r for r in raw if r not in NON_PRICE_TOKENS} or set(raw)

    en_dur, es_dur = durations(draft_en), durations(draft_es)
    if en_dur != es_dur:
        findings.append(Finding(
            "bilingual_parity", WARN,
            "durations differ: EN=%s ES=%s" % (sorted(en_dur) or "-", sorted(es_dur) or "-"),
        ))

    if not draft_en.strip() or not draft_es.strip():
        findings.append(Finding("bilingual_parity", FAIL, "one language draft is empty"))

    if not findings:
        findings.append(Finding("bilingual_parity", PASS, "EN and ES carry the same terms"))
    return findings


def validate_missing_information(extracted: dict, draft_en: str) -> list:
    """Required fields must either be present or explicitly asked for."""
    required = ["requested_date", "category", "location"]
    findings = []
    missing = [f for f in required if not extracted.get(f)]
    if missing:
        asked = "?" in draft_en
        level = WARN if asked else FAIL
        findings.append(Finding(
            "missing_information", level,
            "missing %s; draft %s ask the customer a question"
            % (", ".join(missing), "does" if asked else "does NOT"),
        ))
    else:
        findings.append(Finding("missing_information", PASS, "date, category and location present"))
    return findings


def validate_no_unsafe_confirmation(draft_en: str, draft_es: str, pricing: dict) -> list:
    """The tool must never confirm a booking or acknowledge a deposit.

    Only a human confirms, and only after the deposit clears.
    """
    forbidden = pricing["forbidden_claims"]["confirmation_terms"]
    findings = []
    for label, draft in (("en", draft_en), ("es", draft_es)):
        folded = _fold(draft)
        for term in forbidden:
            if _fold(term) in folded:
                findings.append(Finding(
                    "unsafe_confirmation", FAIL,
                    "draft_%s contains confirmation language: %r" % (label, term),
                ))
    if not findings:
        findings.append(Finding("unsafe_confirmation", PASS, "no booking or deposit confirmation language"))
    return findings


def validate_no_insurance_claim(draft_en: str, draft_es: str, pricing: dict,
                                policy_verified: bool = False) -> list:
    """No insurance promise until the commercial policy is verified.

    business/insurance-and-wave1-preflight.md is the authority; until it records
    an active policy, insurance language may not leave this tool.
    """
    if policy_verified:
        return [Finding("insurance_claim", PASS, "policy marked verified by operator")]
    forbidden = pricing["forbidden_claims"]["insurance_terms"]
    findings = []
    for label, draft in (("en", draft_en), ("es", draft_es)):
        folded = _fold(draft)
        for term in forbidden:
            if _fold(term) in folded:
                findings.append(Finding(
                    "insurance_claim", FAIL,
                    "draft_%s claims insurance (%r) with no verified policy" % (label, term),
                ))
    if not findings:
        findings.append(Finding("insurance_claim", PASS, "no insurance claim in draft"))
    return findings


def validate_payment_method(draft_en: str, draft_es: str, pricing: dict | None = None) -> list:
    """Zelle, plus the business's own Stripe Payment Link once it exists.

    Stripe is deliberately absent from the banned list: the business's own
    Stripe Payment Link became an official deposit rail alongside Zelle
    (operator decision, 2026-08-30). But a draft may not PROMISE a payment
    link while pricing.json carries no real link URL - that tells a customer
    to expect something that does not exist. Everything else stays forbidden.
    """
    banned = ["cash app", "cashapp", "venmo", "paypal", "square",
              "credit card", "debit card", "apple pay", "wire transfer", "zinli"]
    link_configured = bool(((pricing or {}).get("payment") or {}).get("stripe_payment_link"))
    link_phrases = ["payment link", "enlace de pago", "link de pago"]
    findings = []
    for label, draft in (("en", draft_en), ("es", draft_es)):
        folded = _fold(draft)
        for term in banned:
            if term in folded:
                findings.append(Finding(
                    "payment_method", FAIL,
                    "draft_%s mentions non-Zelle payment method: %r" % (label, term),
                ))
        if not link_configured:
            for term in link_phrases:
                if _fold(term) in folded:
                    findings.append(Finding(
                        "payment_method", FAIL,
                        "draft_%s promises a payment link but no Stripe Payment "
                        "Link is configured" % label,
                    ))
                    break
    if not findings:
        label = "Zelle and the configured payment link" if link_configured else "Zelle only"
        findings.append(Finding("payment_method", PASS, label))
    return findings


def run_all(extracted: dict, draft_en: str, draft_es: str, pricing: dict,
            policy_verified: bool = False) -> list:
    findings = []
    findings += validate_pricing(draft_en, draft_es, pricing)
    findings += validate_bilingual_parity(draft_en, draft_es)
    findings += validate_missing_information(extracted, draft_en)
    findings += validate_no_unsafe_confirmation(draft_en, draft_es, pricing)
    findings += validate_no_insurance_claim(draft_en, draft_es, pricing, policy_verified)
    findings += validate_payment_method(draft_en, draft_es, pricing)
    return findings


def blocking(findings: list) -> list:
    return [f for f in findings if f.level == FAIL]
