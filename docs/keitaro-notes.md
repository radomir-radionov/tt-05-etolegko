# Keitaro API notes (tlgk.host)

> Do not commit API keys. Get a key in **Profile → API keys → Create** (or use existing).

## Auth

- Base URL: `https://tlgk.host/admin_api/v1`
- Header: `Api-Key: <your-key>`
- Swagger: link **Documentation** on the API keys page

## Default IDs for this test stand (verified 2026-11-19)

| Setting | ID | Name |
|---------|-----|------|
| `domain_id` | **1813** | `kylovoa.com` (`https://kylovoa.com/`) |
| `group_id` | **10332** | `FORTESTS` (type `campaigns`) |
| `traffic_source_id` | **836** | `FORTESTS` |

Note: assignment screenshots show `in.posdk.xyz`; on **tlgk.host** only `kylovoa.com` is available via API for this account.

## Create campaign

`POST /campaigns`

```json
{
  "name": "test_radionov_campaign1",
  "alias": "test_radionov_campaign1_unique",
  "type": "position",
  "cost_type": "CPC",
  "cost_value": 0,
  "cost_currency": "USD",
  "cost_auto": true,
  "domain_id": 1813,
  "group_id": 10332,
  "traffic_source_id": 836
}
```

`type: position` = stream rotation by position (geo stream first).

## Stream 1 — geo → Google

`POST /streams`

```json
{
  "campaign_id": 123,
  "type": "regular",
  "name": "Geo MX,AU -> Google",
  "position": 1,
  "action_type": "http",
  "action_payload": "https://www.google.com/",
  "schema": "redirect",
  "filters": [
    {
      "name": "country",
      "mode": "accept",
      "payload": ["MX", "AU"]
    }
  ],
  "offers": [],
  "landings": []
}
```

Filter name is **`country`**, not `geo`.

## Stream 2 — offers

```json
{
  "campaign_id": 123,
  "type": "regular",
  "name": "Offers",
  "position": 2,
  "action_type": "http",
  "action_payload": "",
  "schema": "landings",
  "filters": [],
  "offers": [{ "offer_id": 18813, "share": 100 }],
  "landings": []
}
```

Multiple offers: equal `share` split (e.g. two offers → 50/50).

## Editor — update offers

`PUT /streams/{stream_id}` with full or partial body; at minimum:

```json
{
  "offers": [
    { "offer_id": 18813, "share": 50 },
    { "offer_id": 18814, "share": 50 }
  ]
}
```

## Stats for editor

`POST /report/build`

```json
{
  "range": { "interval": "all_time", "timezone": "Europe/Moscow" },
  "columns": [],
  "metrics": ["clicks", "campaign_unique_clicks", "bots"],
  "grouping": ["offer_id"],
  "filters": [
    {
      "name": "campaign_id",
      "operator": "EQUALS",
      "expression": 215194
    }
  ],
  "limit": 1000
}
```

Map metrics: `clicks`, `campaign_unique_clicks` → unique, `bots`.

## Probe

`test_radionov_probe` was created with two streams and then deleted via `DELETE /campaigns/{id}`.