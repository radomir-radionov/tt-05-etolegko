from app.models.campaign_record import CampaignRecord
from app.services.campaign_editor import CampaignEditorService
from app.services.errors import OfferAlreadyExistsError
import pytest


class FakeKeitaroEditor:
    def __init__(self):
        self.stream = {
            "id": 55,
            "offers": [{"offer_id": 10, "share": 100}],
        }
        self.report_rows = [
            {"offer_id": 10, "clicks": 5, "campaign_unique_clicks": 3, "bots": 1},
        ]
        self.updated_payloads: list[dict] = []

    def get_stream(self, stream_id):
        return self.stream

    def update_stream(self, stream_id, payload):
        self.updated_payloads.append(payload)
        self.stream["offers"] = [
            {"offer_id": o["offer_id"], "share": o["share"]}
            for o in payload["offers"]
        ]
        return self.stream

    def build_report(self, payload):
        return self.report_rows


def _seed(db_session) -> CampaignRecord:
    record = CampaignRecord(
        name="test_radionov_e",
        geo_countries="AU",
        keitaro_campaign_id=77,
        offer_stream_id=55,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


def test_get_state_includes_stats(db_session):
    record = _seed(db_session)
    service = CampaignEditorService(db_session, FakeKeitaroEditor())  # type: ignore[arg-type]
    state = service.get_state(record.id)
    assert state["offers"] == [
        {"id": 10, "share": 100, "clicks": 5, "unique": 3, "bots": 1}
    ]


def test_add_offer_rebalances_shares(db_session):
    record = _seed(db_session)
    fake = FakeKeitaroEditor()
    fake.report_rows.append(
        {"offer_id": 20, "clicks": 0, "campaign_unique_clicks": 0, "bots": 0}
    )
    service = CampaignEditorService(db_session, fake)  # type: ignore[arg-type]
    state = service.add_offer(record.id, 20)
    assert len(state["offers"]) == 2
    shares = {o["id"]: o["share"] for o in state["offers"]}
    assert shares == {10: 50, 20: 50}


def test_add_duplicate_raises(db_session):
    record = _seed(db_session)
    service = CampaignEditorService(db_session, FakeKeitaroEditor())  # type: ignore[arg-type]
    with pytest.raises(OfferAlreadyExistsError):
        service.add_offer(record.id, 10)