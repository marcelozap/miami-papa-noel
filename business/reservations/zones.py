"""Driving zones + December-evening drive-time estimates (minutes).

IMPORTANT — SYNC STEP: business/december-slot-board.html already carries the
canonical 10-zone drive-time matrix. On the Windows machine, export that
matrix to business/reservations/data/zones.json (format below) and it will
override everything in this file. The values below are placeholder ESTIMATES
so the system runs before the sync; they are labelled as estimates in every
output and are NOT live traffic.

zones.json format:
  {"zones": {"doral": "Doral", ...},
   "drive_min": {"doral": {"hialeah": 15, ...}, ...}}
"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
OVERRIDE_PATH = os.path.join(BASE, "data", "zones.json")

ZONES = {
    "doral": "Doral",
    "hialeah": "Hialeah",
    "miami_beach": "Miami Beach",
    "downtown_brickell": "Downtown / Brickell",
    "coral_gables": "Coral Gables",
    "kendall": "Kendall",
    "homestead": "Homestead",
    "north_miami": "North Miami",
    "fort_lauderdale": "Fort Lauderdale",
    "pembroke_pines": "Pembroke Pines / Weston",
}

_SAME_ZONE_MIN = 10
_DEFAULT_MIN = 35  # unknown pair fallback, deliberately conservative

# One direction listed; lookups are symmetric.
_EST = {
    ("doral", "hialeah"): 15,
    ("doral", "miami_beach"): 30,
    ("doral", "downtown_brickell"): 25,
    ("doral", "coral_gables"): 20,
    ("doral", "kendall"): 25,
    ("doral", "homestead"): 45,
    ("doral", "north_miami"): 25,
    ("doral", "fort_lauderdale"): 40,
    ("doral", "pembroke_pines"): 30,
    ("hialeah", "miami_beach"): 25,
    ("hialeah", "downtown_brickell"): 25,
    ("hialeah", "coral_gables"): 25,
    ("hialeah", "kendall"): 30,
    ("hialeah", "homestead"): 50,
    ("hialeah", "north_miami"): 20,
    ("hialeah", "fort_lauderdale"): 35,
    ("hialeah", "pembroke_pines"): 25,
    ("miami_beach", "downtown_brickell"): 15,
    ("miami_beach", "coral_gables"): 25,
    ("miami_beach", "kendall"): 35,
    ("miami_beach", "homestead"): 55,
    ("miami_beach", "north_miami"): 20,
    ("miami_beach", "fort_lauderdale"): 40,
    ("miami_beach", "pembroke_pines"): 45,
    ("downtown_brickell", "coral_gables"): 15,
    ("downtown_brickell", "kendall"): 25,
    ("downtown_brickell", "homestead"): 45,
    ("downtown_brickell", "north_miami"): 20,
    ("downtown_brickell", "fort_lauderdale"): 40,
    ("downtown_brickell", "pembroke_pines"): 40,
    ("coral_gables", "kendall"): 15,
    ("coral_gables", "homestead"): 40,
    ("coral_gables", "north_miami"): 25,
    ("coral_gables", "fort_lauderdale"): 45,
    ("coral_gables", "pembroke_pines"): 40,
    ("kendall", "homestead"): 30,
    ("kendall", "north_miami"): 35,
    ("kendall", "fort_lauderdale"): 50,
    ("kendall", "pembroke_pines"): 40,
    ("homestead", "north_miami"): 55,
    ("homestead", "fort_lauderdale"): 70,
    ("homestead", "pembroke_pines"): 60,
    ("north_miami", "fort_lauderdale"): 25,
    ("north_miami", "pembroke_pines"): 30,
    ("fort_lauderdale", "pembroke_pines"): 25,
}


class UnknownZone(Exception):
    pass


def _load_override():
    if os.path.exists(OVERRIDE_PATH):
        with open(OVERRIDE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def zone_map():
    ov = _load_override()
    return ov["zones"] if ov else dict(ZONES)


def validate_zone(key):
    zm = zone_map()
    if key not in zm:
        raise UnknownZone("unknown zone '%s' — valid: %s" % (key, ", ".join(sorted(zm))))
    return zm[key]


def drive_min(a, b):
    """Estimated December-evening drive time in minutes between two zones."""
    validate_zone(a)
    validate_zone(b)
    ov = _load_override()
    if ov:
        dm = ov.get("drive_min", {})
        if a in dm and b in dm[a]:
            return dm[a][b]
        if b in dm and a in dm[b]:
            return dm[b][a]
    if a == b:
        return _SAME_ZONE_MIN
    return _EST.get((a, b)) or _EST.get((b, a)) or _DEFAULT_MIN


def using_estimates():
    """True while running on the built-in placeholder matrix."""
    return _load_override() is None
