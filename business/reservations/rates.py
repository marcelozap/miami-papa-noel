"""The LOCKED rate card (decided 2026-08-26). Do not change prices here —
this file mirrors packages-and-pricing.md / checkout.html. If the card ever
changes on the site, change it there first, then mirror it here."""


RATE_CARD = {
    "standard": {
        "label_en": "Standard home visit (first hour)",
        "label_es": "Visita estándar a domicilio (primera hora)",
        "price": 325,
        "extra": "+$150 per extra half hour",
        "default_duration_min": 60,
    },
    "jingle": {
        "label_en": "Jingle entry visit (capped)",
        "label_es": "Visita Jingle (cupos limitados)",
        "price": 195,
        "extra": "Mon-Thu daytime, Dec 1-18 only, ~12 max, traded for a review + photo release",
        "default_duration_min": 30,
    },
    "school": {
        "label_en": "School / daycare (weekday daytime)",
        "label_es": "Escuela / guardería (día de semana)",
        "price": 275,
        "extra": "",
        "default_duration_min": 60,
    },
    "corporate": {
        "label_en": "Corporate party",
        "label_es": "Fiesta corporativa",
        "price": 450,
        "extra": "",
        "default_duration_min": 60,
    },
    "hoa": {
        "label_en": "HOA / community event (2 hours)",
        "label_es": "Evento comunitario / HOA (2 horas)",
        "price": 550,
        "extra": "",
        "default_duration_min": 120,
    },
    "peak_evening": {
        "label_en": "Peak evening (Dec 12/13/19/20 after 4pm)",
        "label_es": "Noche pico (12/13/19/20 de dic. después de las 4pm)",
        "price": 425,
        "extra": "",
        "default_duration_min": 60,
    },
    "christmas_eve": {
        "label_en": "Christmas Eve slot (45 min)",
        "label_es": "Nochebuena (45 min)",
        "price": 500,
        "extra": "First come with deposit",
        "default_duration_min": 45,
    },
    "sneak_a_peek": {
        "label_en": "Sneak-a-peek (after 9pm)",
        "label_es": "Sneak-a-peek (después de las 9pm)",
        "price": 375,
        "extra": "",
        "default_duration_min": 30,
    },
    "photographer_4hr": {
        "label_en": "Photographer block (4 hours)",
        "label_es": "Bloque para fotógrafo (4 horas)",
        "price": 600,
        "extra": "",
        "default_duration_min": 240,
    },
    "photographer_day": {
        "label_en": "Photographer block (full day)",
        "label_es": "Bloque para fotógrafo (día completo)",
        "price": 850,
        "extra": "",
        "default_duration_min": 480,
    },
}


class UnknownPackage(Exception):
    pass


def validate_package(key):
    if key not in RATE_CARD:
        raise UnknownPackage(
            "unknown package '%s' — valid: %s" % (key, ", ".join(sorted(RATE_CARD)))
        )
    return RATE_CARD[key]
