from typing import Any

from sqlalchemy.orm import Session

from app.integrations.keitaro.client import KeitaroClient
from app.models.campaign_record import CampaignRecord
from app.services.campaign_payloads import equal_shares
from app.services.errors import (
    CampaignNotFoundError,
    OfferAlreadyExistsError,
    OfferNotFoundError,
)


class CampaignEditorService:
    def __init__(self, db: Session, keitaro: KeitaroClient) -> None:
        self._db = db
        self._keitaro = keitaro

    def _get_record(self, local_id: int) -> CampaignRecord:
        record = self._db.get(CampaignRecord, local_id)
        if record is None:
            raise CampaignNotFoundError(f"Campaign {local_id} not found")
        if record.offer_stream_id is None:
            raise CampaignNotFoundError("Campaign has no offer stream")
        return record

    def _current_offer_ids(self, stream: dict[str, Any]) -> list[int]:
        return [int(o["offer_id"]) for o in stream.get("offers", [])]

    def _report_by_offer(self, keitaro_campaign_id: int) -> dict[int, dict[str, int]]:
        rows = self._keitaro.build_report(
            {
                "range": {"interval": "all_time", "timezone": "Europe/Moscow"},
                "columns": [],
                "metrics": ["clicks", "campaign_unique_clicks", "bots"],
                "grouping": ["offer_id"],
                "filters": [
                    {
                        "name": "campaign_id",
                        "operator": "EQUALS",
                        "expression": keitaro_campaign_id,
                    }
                ],
                "limit": 1000,
            }
        )
        result: dict[int, dict[str, int]] = {}
        for row in rows:
            offer_id = int(row.get("offer_id", 0))
            result[offer_id] = {
                "clicks": int(row.get("clicks", 0) or 0),
                "unique": int(row.get("campaign_unique_clicks", 0) or 0),
                "bots": int(row.get("bots", 0) or 0),
            }
        return result

    def get_state(self, local_id: int) -> dict[str, Any]:
        record = self._get_record(local_id)
        stream = self._keitaro.get_stream(record.offer_stream_id)
        stats = self._report_by_offer(record.keitaro_campaign_id)
        offers: list[dict[str, Any]] = []
        for offer in stream.get("offers", []):
            oid = int(offer["offer_id"])
            offer_stats = stats.get(oid, {"clicks": 0, "unique": 0, "bots": 0})
            offers.append(
                {
                    "id": oid,
                    "share": int(offer.get("share", 0)),
                    "clicks": offer_stats["clicks"],
                    "unique": offer_stats["unique"],
                    "bots": offer_stats["bots"],
                }
            )
        return {
            "id": record.id,
            "name": record.name,
            "geo_countries": record.geo_countries,
            "keitaro_campaign_id": record.keitaro_campaign_id,
            "offer_stream_id": record.offer_stream_id,
            "offers": offers,
        }

    def add_offer(self, local_id: int, offer_id: int) -> dict[str, Any]:
        record = self._get_record(local_id)
        stream = self._keitaro.get_stream(record.offer_stream_id)
        offer_ids = self._current_offer_ids(stream)
        if offer_id in offer_ids:
            raise OfferAlreadyExistsError(f"Offer {offer_id} already in campaign")
        offer_ids.append(offer_id)
        payload = {
            "offers": [
                {"offer_id": oid, "share": share}
                for oid, share in equal_shares(offer_ids)
            ]
        }
        self._keitaro.update_stream(record.offer_stream_id, payload)
        return self.get_state(local_id)

    def remove_offer(self, local_id: int, offer_id: int) -> dict[str, Any]:
        record = self._get_record(local_id)
        stream = self._keitaro.get_stream(record.offer_stream_id)
        offer_ids = self._current_offer_ids(stream)
        if offer_id not in offer_ids:
            raise OfferNotFoundError(f"Offer {offer_id} not in campaign")
        offer_ids = [oid for oid in offer_ids if oid != offer_id]
        if not offer_ids:
            raise OfferNotFoundError("Cannot remove the last offer from the stream")
        payload = {
            "offers": [
                {"offer_id": oid, "share": share}
                for oid, share in equal_shares(offer_ids)
            ]
        }
        self._keitaro.update_stream(record.offer_stream_id, payload)
        return self.get_state(local_id)