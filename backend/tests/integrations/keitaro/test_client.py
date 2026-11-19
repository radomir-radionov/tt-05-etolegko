import httpx
import pytest
import respx

from app.core.config import Settings
from app.integrations.keitaro.client import KeitaroClient
from app.integrations.keitaro.errors import KeitaroAPIError


@pytest.fixture
def settings():
    return Settings(
        keitaro_base_url="https://tlgk.host/admin_api/v1",
        keitaro_api_key="abc123",
    )


@respx.mock
def test_create_campaign_sends_api_key(settings):
    route = respx.post("https://tlgk.host/admin_api/v1/campaigns").mock(
        return_value=httpx.Response(200, json={"id": 99})
    )
    client = KeitaroClient(settings)
    campaign_id = client.create_campaign({"name": "test_radionov_x", "alias": "x"})
    client.close()
    assert campaign_id == 99
    assert route.calls[0].request.headers["Api-Key"] == "abc123"


@respx.mock
def test_create_stream(settings):
    respx.post("https://tlgk.host/admin_api/v1/streams").mock(
        return_value=httpx.Response(200, json={"id": 501})
    )
    client = KeitaroClient(settings)
    stream_id = client.create_stream({"campaign_id": 1})
    client.close()
    assert stream_id == 501


@respx.mock
def test_keitaro_api_error(settings):
    respx.get("https://tlgk.host/admin_api/v1/campaigns/1/streams").mock(
        return_value=httpx.Response(401, text="Unauthorized")
    )
    client = KeitaroClient(settings)
    with pytest.raises(KeitaroAPIError) as exc:
        client.get_campaign_streams(1)
    assert exc.value.status_code == 401
    client.close()