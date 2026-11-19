from pydantic import BaseModel, Field


class CreateCampaignRequest(BaseModel):
    name: str = Field(..., min_length=1)
    geo: str = Field(..., min_length=2)
    offer_id: int = Field(..., gt=0)


class CreateCampaignResponse(BaseModel):
    id: int
    name: str
    keitaro_campaign_id: int
    offer_stream_id: int
    geo_countries: str


class OfferStatsItem(BaseModel):
    id: int
    share: int
    clicks: int
    unique: int
    bots: int


class CampaignStateResponse(BaseModel):
    id: int
    name: str
    geo_countries: str
    keitaro_campaign_id: int
    offer_stream_id: int
    offers: list[OfferStatsItem]


class AddOfferRequest(BaseModel):
    offer_id: int = Field(..., gt=0)


class OfferSearchItem(BaseModel):
    id: int
    name: str