"""OpenAI content adapter — generative drafting for the Papa Noel content lane.

Selected automatically by the `content` command when OPENAI_API_KEY is set in
the environment; otherwise the LocalDryRunAdapter runs. The key lives ONLY in
the environment — never in this repo. Model defaults to gpt-4o-mini and can be
overridden with OPENAI_MODEL.

Fail-closed copy rules: if the generated text violates the copy rules (claims
"insured", wrong brand accent, leaks the client name or address, carries the
Zelle account number instead of the public line), the output is rejected and
the deterministic template captions stand — the manifest says so. Generated
text is always a DRAFT for the operator; nothing here publishes.
"""

import json
import os
import re
import urllib.request

from malosound_adapter import MaloSoundAdapter

API_URL = "https://api.openai.com/v1/chat/completions"

SYSTEM_PROMPT = (
    "You write short social captions and video briefs for Miami Papa Noel, a "
    "bilingual Santa visit business serving Miami-Dade and Broward. Hard rules: "
    "the brand is 'Miami Papa Noel' (unaccented — only the character is called "
    "'Papá Noel'); never claim or imply the business is insured; never include "
    "any client name or street address; always produce BOTH English and Spanish; "
    "tone is warm and family-first, and the angle is the bilingual visit "
    "(English y español) with December dates filling; close with 786-975-9557 / "
    "miamipapanoel.com — never mention any other phone number. Respond with a "
    "JSON object with exactly these keys: "
    "caption_en, caption_es, video_brief."
)


class OpenAIContentAdapter(MaloSoundAdapter):
    """Calls the OpenAI API over stdlib urllib — zero dependencies."""

    name = "openai"

    def __init__(self, api_key=None, model=None, transport=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set — set it in the environment "
                "(never in the repo) or use the dry-run adapter"
            )
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.transport = transport or self._http

    def _http(self, payload):
        req = urllib.request.Request(
            API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode("utf-8"))

    def _violations(self, generated, brief):
        text = " ".join(str(generated.get(k, "")) for k in
                        ("caption_en", "caption_es", "video_brief")).lower()
        bad = []
        if "insured" in text or "asegurado" in text:
            bad.append("claims insured")
        if "miami papá noel" in text:
            bad.append("wrong brand accent")
        # Separators stripped, so "(305) 244-0360", "3052440360" and
        # "+1 305 244 0360" are caught the same as the literal.
        if "3052440360" in re.sub(r"[\s().+\-]", "", text):
            bad.append("carries the Zelle account number")
        for key in ("client_name", "address"):
            val = str(brief.get(key) or "").strip().lower()
            if len(val) > 3 and val in text:
                bad.append("leaks " + key)
        for k in ("caption_en", "caption_es"):
            if not str(generated.get(k, "")).strip():
                bad.append("missing " + k)
        return bad

    def generate(self, brief, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "brief.json"), "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(brief, ensure_ascii=False)},
            ],
            "response_format": {"type": "json_object"},
        }
        resp = self.transport(payload)
        generated = json.loads(resp["choices"][0]["message"]["content"])
        violations = self._violations(generated, brief)

        manifest = {
            "adapter": self.name,
            "model": self.model,
            "asset": None,
        }
        if violations:
            manifest["rejected"] = violations
            manifest["note"] = ("generated text failed copy rules; the "
                                "deterministic template captions stand")
        else:
            gen_path = os.path.join(out_dir, "generated.json")
            with open(gen_path, "w", encoding="utf-8") as f:
                json.dump(generated, f, indent=2, ensure_ascii=False)
            manifest["asset"] = gen_path
            manifest["note"] = "draft only — operator approval required before publishing"
        with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return {"brief": os.path.join(out_dir, "brief.json"),
                "manifest": os.path.join(out_dir, "manifest.json"),
                "asset": manifest["asset"]}
