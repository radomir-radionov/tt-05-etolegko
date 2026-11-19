from app.api.deps import get_keitaro_client
from app.main import app
from app.models.campaign_record import CampaignRecord


class FakeKeitaroApi:
    def create_campaign(self, payload):
        return 9001

    def create_stream(self, payload):
        if payload.get("position") == 1:
            return 8001
        return 8002

    def close(self):
        pass

    def search_offers(self, query):
        return [{"id": 1, "name": "Offer A"}]


def test_post_campaigns_201(client, db_session):
    app.dependency_overrides[get_keitaro_client] = lambda: FakeKeitaroApi()
    response = client.post(
        "/api/campaigns",
        json={"name": "test_radionov_api", "geo": "MX,AU", "offer_id": 18813},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 201
    body = response.json()
    assert body["keitaro_campaign_id"] == 9001
    assert body["offer_stream_id"] == 8002
    assert db_session.query(CampaignRecord).count() == 1


def test_post_campaigns_invalid_geo(client):
    app.dependency_overrides[get_keitaro_client] = lambda: FakeKeitaroApi()
    response = client.post(
        "/api/campaigns",
        json={"name": "test_radionov_api", "geo": "INVALID", "offer_id": 1},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 422


def test_search_offers(client):
    app.dependency_overrides[get_keitaro_client] = lambda: FakeKeitaroApi()
    response = client.get("/api/offers?q=Offer")
    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()[0]["id"] == 1