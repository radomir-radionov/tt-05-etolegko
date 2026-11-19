import os

import pytest

from app.core.config import Settings
from app.integrations.keitaro.client import KeitaroClient
from app.services.campaign_payloads import (
    build_geo_stream_payload,
    build_offer_stream_payload,
)


@pytest.mark.keitaro_live
def test_live_create_and_cleanup():
    api_key = os.environ.get("KEITARO_API_KEY")
    if not api_key:
        pytest.skip("KEITARO_API_KEY not set")

    settings = Settings(keitaro_api_key=api_key)
    client = KeitaroClient(settings)
    campaign_id = None
    try:
        campaign_id = client.create_campaign(
            {
                "name": "test_radionov_live",
                "alias": "test_radionov_live_tmp",
                "type": "position",
                "cost_type": "CPC",
                "cost_value": 0,
                "cost_currency": "USD",
                "cost_auto": True,
                "domain_id": settings.keitaro_domain_id,
                "group_id": settings.keitaro_group_id,
                "traffic_source_id": settings.keitaro_traffic_source_id,
            }
        )
        client.create_stream(build_geo_stream_payload(campaign_id, ["AU"]))
        client.create_stream(build_offer_stream_payload(campaign_id, [(18813, 100)]))
        streams = client.get_campaign_streams(campaign_id)
        assert len(streams) >= 2
    finally:
        if campaign_id is not None:
            client.archive_campaign(campaign_id)
        client.close()