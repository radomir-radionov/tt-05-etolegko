from app.core.config import Settings
from app.models.campaign_record import CampaignRecord
from app.services.campaign_creator import CampaignCreatorService
from app.services.errors import CampaignValidationError
import pytest


class FakeKeitaro:
    def __init__(self):
        self.campaigns: list[dict] = []
        self.streams: list[dict] = []
        self._campaign_id = 1000
        self._stream_id = 2000

    def create_campaign(self, payload):
        self._campaign_id += 1
        self.campaigns.append(payload)
        return self._campaign_id

    def create_stream(self, payload):
        self._stream_id += 1
        self.streams.append(payload)
        return self._stream_id


def test_create_campaign_builds_geo_then_offer_stream(db_session):
    fake = FakeKeitaro()
    settings = Settings(campaign_name_prefix="test_radionov_")
    service = CampaignCreatorService(db_session, fake, settings)  # type: ignore[arg-type]
    record = service.create("test_radionov_c1", "MX,AU", 18813)

    assert record.keitaro_campaign_id == 1001
    assert record.offer_stream_id == 2002
    assert len(fake.streams) == 2
    assert fake.streams[0]["filters"][0]["payload"] == ["MX", "AU"]
    assert fake.streams[1]["offers"][0]["offer_id"] == 18813
    assert db_session.query(CampaignRecord).count() == 1


def test_create_rejects_bad_prefix(db_session):
    fake = FakeKeitaro()
    settings = Settings(campaign_name_prefix="test_radionov_")
    service = CampaignCreatorService(db_session, fake, settings)  # type: ignore[arg-type]
    with pytest.raises(CampaignValidationError):
        service.create("wrong_name", "US", 1)