import uuid

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.integrations.keitaro.client import KeitaroClient
from app.models.campaign_record import CampaignRecord
from app.services.campaign_payloads import (
    build_geo_stream_payload,
    build_offer_stream_payload,
    parse_geo_countries,
)
from app.services.errors import CampaignValidationError


class CampaignCreatorService:
    def __init__(
        self,
        db: Session,
        keitaro: KeitaroClient,
        settings: Settings,
    ) -> None:
        self._db = db
        self._keitaro = keitaro
        self._settings = settings

    def create(self, name: str, geo_raw: str, offer_id: int) -> CampaignRecord:
        prefix = self._settings.campaign_name_prefix
        if not name.startswith(prefix):
            raise CampaignValidationError(f"Campaign name must start with {prefix}")
        if offer_id <= 0:
            raise CampaignValidationError("offer_id must be positive")

        countries = parse_geo_countries(geo_raw)
        alias = f"{name}_{uuid.uuid4().hex[:8]}"

        campaign_payload = {
            "name": name,
            "alias": alias,
            "type": "position",
            "cost_type": "CPC",
            "cost_value": 0,
            "cost_currency": "USD",
            "cost_auto": True,
            "domain_id": self._settings.keitaro_domain_id,
            "group_id": self._settings.keitaro_group_id,
            "traffic_source_id": self._settings.keitaro_traffic_source_id,
        }
        keitaro_id = self._keitaro.create_campaign(campaign_payload)

        geo_payload = build_geo_stream_payload(keitaro_id, countries)
        self._keitaro.create_stream(geo_payload)

        offer_payload = build_offer_stream_payload(keitaro_id, [(offer_id, 100)])
        offer_stream_id = self._keitaro.create_stream(offer_payload)

        record = CampaignRecord(
            name=name,
            geo_countries=",".join(countries),
            keitaro_campaign_id=keitaro_id,
            offer_stream_id=offer_stream_id,
        )
        self._db.add(record)
        self._db.commit()
        self._db.refresh(record)
        return record