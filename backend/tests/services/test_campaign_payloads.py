import pytest

from app.services.campaign_payloads import (
    build_geo_stream_payload,
    equal_shares,
    parse_geo_countries,
)


def test_parse_geo_countries_multi():
    assert parse_geo_countries("mx, au, RO") == ["MX", "AU", "RO"]


def test_parse_geo_invalid_raises():
    with pytest.raises(ValueError):
        parse_geo_countries("MEX")


def test_geo_stream_filter_uses_country_name():
    payload = build_geo_stream_payload(10, ["AU", "MX"])
    assert payload["filters"][0]["name"] == "country"
    assert payload["filters"][0]["payload"] == ["AU", "MX"]
    assert payload["action_payload"] == "https://www.google.com/"


def test_equal_shares_two_offers():
    assert equal_shares([1, 2]) == [(1, 50), (2, 50)]