"""MaloSound adapter — the creative/content lane boundary.

MaloSound.ai is the creative technology lane. Until its real API or
credentials exist, the ONLY implementation is LocalDryRunAdapter, which
writes the brief and a stub manifest to disk. No endpoints, no credentials,
no invented integration — when the real service exists, add a second
implementation of MaloSoundAdapter and leave this one as the fallback.
"""

import json
import os
from datetime import datetime, timezone


class MaloSoundAdapter:
    """Interface: turn a content brief into (eventually) a generated asset."""

    name = "abstract"

    def generate(self, brief, out_dir):
        raise NotImplementedError


class LocalDryRunAdapter(MaloSoundAdapter):
    """Writes the brief + a stub manifest. Makes zero network calls."""

    name = "local-dry-run"

    def generate(self, brief, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        brief_path = os.path.join(out_dir, "brief.json")
        with open(brief_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, indent=2, ensure_ascii=False)
        manifest = {
            "adapter": self.name,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "asset": None,
            "note": "dry run — no asset generated; real MaloSound.ai adapter not yet available",
        }
        manifest_path = os.path.join(out_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return {"brief": brief_path, "manifest": manifest_path, "asset": None}
