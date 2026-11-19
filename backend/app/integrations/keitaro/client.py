from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings
from app.integrations.keitaro.errors import KeitaroAPIError


class KeitaroClient:
    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self._settings = settings
        self._owns_client = client is None
        self._client = client or httpx.Client(
            base_url=settings.keitaro_base_url.rstrip("/"),
            headers={
                "Api-Key": settings.keitaro_api_key,
                "Accept": "application/json",
            },
            timeout=30.0,
        )

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._client.request(method, path, **kwargs)
        if response.status_code >= 400:
            detail = response.text[:500]
            raise KeitaroAPIError(response.status_code, detail)
        if not response.content:
            return None
        return response.json()

    def create_campaign(self, payload: dict[str, Any]) -> int:
        data = self._request("POST", "/campaigns", json=payload)
        return int(data["id"])

    def create_stream(self, payload: dict[str, Any]) -> int:
        data = self._request("POST", "/streams", json=payload)
        return int(data["id"])

    def update_stream(self, stream_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("PUT", f"/streams/{stream_id}", json=payload)

    def get_campaign_streams(self, campaign_id: int) -> list[dict[str, Any]]:
        data = self._request("GET", f"/campaigns/{campaign_id}/streams")
        return list(data)

    def get_stream(self, stream_id: int) -> dict[str, Any]:
        return self._request("GET", f"/streams/{stream_id}")

    def list_offers(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/offers")
        return list(data)

    def search_offers(self, query: str, limit: int = 20) -> list[dict[str, Any]]:
        q = query.strip().lower()
        if not q:
            return []
        offers = self.list_offers()
        matches: list[dict[str, Any]] = []
        for offer in offers:
            name = str(offer.get("name", "")).lower()
            oid = str(offer.get("id", ""))
            if q in name or q == oid:
                matches.append(offer)
            if len(matches) >= limit:
                break
        return matches

    def build_report(self, payload: dict[str, Any]) -> list[dict[str, Any]]:
        data = self._request("POST", "/report/build", json=payload)
        return list(data.get("rows", []))

    def archive_campaign(self, campaign_id: int) -> None:
        self._request("DELETE", f"/campaigns/{campaign_id}")