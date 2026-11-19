from typing import Any


def parse_geo_countries(geo_raw: str) -> list[str]:
    parts = [p.strip().upper() for p in geo_raw.split(",") if p.strip()]
    unique: list[str] = []
    for code in parts:
        if len(code) != 2 or not code.isalpha():
            raise ValueError(f"Invalid country code: {code}")
        if code not in unique:
            unique.append(code)
    if not unique:
        raise ValueError("At least one country code is required")
    return unique


def build_geo_stream_payload(
    campaign_id: int,
    countries: list[str],
    *,
    google_url: str = "https://www.google.com/",
) -> dict[str, Any]:
    return {
        "campaign_id": campaign_id,
        "type": "regular",
        "name": f"Geo {','.join(countries)} -> Google",
        "position": 1,
        "action_type": "http",
        "action_payload": google_url,
        "schema": "redirect",
        "filters": [
            {"name": "country", "mode": "accept", "payload": countries},
        ],
        "offers": [],
        "landings": [],
    }


def build_offer_stream_payload(
    campaign_id: int,
    offer_entries: list[tuple[int, int]],
) -> dict[str, Any]:
    return {
        "campaign_id": campaign_id,
        "type": "regular",
        "name": "Offers",
        "position": 2,
        "action_type": "http",
        "action_payload": "",
        "schema": "landings",
        "filters": [],
        "offers": [{"offer_id": oid, "share": share} for oid, share in offer_entries],
        "landings": [],
    }


def equal_shares(offer_ids: list[int]) -> list[tuple[int, int]]:
    if not offer_ids:
        return []
    share = 100 // len(offer_ids)
    remainder = 100 - share * len(offer_ids)
    result: list[tuple[int, int]] = []
    for index, offer_id in enumerate(offer_ids):
        extra = 1 if index < remainder else 0
        result.append((offer_id, share + extra))
    return result