from app.api.deps import get_keitaro_client
from app.main import app
from app.models.campaign_record import CampaignRecord


class FakeKeitaroEditorApi:
    def __init__(self):
        self.offers = [{"offer_id": 10, "share": 100}]

    def get_stream(self, stream_id):
        return {"id": stream_id, "offers": self.offers}

    def update_stream(self, stream_id, payload):
        self.offers = payload["offers"]
        return {"offers": self.offers}

    def build_report(self, payload):
        return [
            {
                "offer_id": 10,
                "clicks": 7,
                "campaign_unique_clicks": 4,
                "bots": 0,
            }
        ]

    def close(self):
        pass


def _seed(db_session) -> int:
    record = CampaignRecord(
        name="test_radionov_ed",
        geo_countries="AU",
        keitaro_campaign_id=1,
        offer_stream_id=55,
    )
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record.id


def test_get_campaign(client, db_session):
    local_id = _seed(db_session)
    app.dependency_overrides[get_keitaro_client] = lambda: FakeKeitaroEditorApi()
    response = client.get(f"/api/campaigns/{local_id}")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["offers"][0]["clicks"] == 7


def test_add_offer_409_when_duplicate(client, db_session):
    local_id = _seed(db_session)
    app.dependency_overrides[get_keitaro_client] = lambda: FakeKeitaroEditorApi()
    response = client.post(
        f"/api/campaigns/{local_id}/offers",
        json={"offer_id": 10},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 409