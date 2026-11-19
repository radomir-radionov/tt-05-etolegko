from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_keitaro_client
from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.integrations.keitaro.client import KeitaroClient
from app.integrations.keitaro.errors import KeitaroAPIError
from app.schemas.campaign import (
    AddOfferRequest,
    CampaignStateResponse,
    CreateCampaignRequest,
    CreateCampaignResponse,
    OfferSearchItem,
)
from app.services.campaign_creator import CampaignCreatorService
from app.services.campaign_editor import CampaignEditorService
from app.services.errors import (
    CampaignNotFoundError,
    CampaignValidationError,
    OfferAlreadyExistsError,
    OfferNotFoundError,
)

router = APIRouter(prefix="/api", tags=["campaigns"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/campaigns", response_model=CreateCampaignResponse, status_code=201)
def create_campaign(
    body: CreateCampaignRequest,
    db: Session = Depends(get_db),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
    settings: Settings = Depends(get_settings),
) -> CreateCampaignResponse:
    service = CampaignCreatorService(db, keitaro, settings)
    try:
        record = service.create(body.name, body.geo, body.offer_id)
    except CampaignValidationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except KeitaroAPIError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc

    if record.offer_stream_id is None:
        raise HTTPException(status_code=500, detail="Offer stream missing")
    return CreateCampaignResponse(
        id=record.id,
        name=record.name,
        keitaro_campaign_id=record.keitaro_campaign_id,
        offer_stream_id=record.offer_stream_id,
        geo_countries=record.geo_countries,
    )


@router.get("/campaigns/{campaign_id}", response_model=CampaignStateResponse)
def get_campaign(
    campaign_id: int,
    db: Session = Depends(get_db),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> CampaignStateResponse:
    service = CampaignEditorService(db, keitaro)
    try:
        state = service.get_state(campaign_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except KeitaroAPIError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    return CampaignStateResponse.model_validate(state)


@router.post("/campaigns/{campaign_id}/offers", response_model=CampaignStateResponse)
def add_offer(
    campaign_id: int,
    body: AddOfferRequest,
    db: Session = Depends(get_db),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> CampaignStateResponse:
    service = CampaignEditorService(db, keitaro)
    try:
        state = service.add_offer(campaign_id, body.offer_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OfferAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except KeitaroAPIError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    return CampaignStateResponse.model_validate(state)


@router.delete(
    "/campaigns/{campaign_id}/offers/{offer_id}",
    response_model=CampaignStateResponse,
)
def remove_offer(
    campaign_id: int,
    offer_id: int,
    db: Session = Depends(get_db),
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> CampaignStateResponse:
    service = CampaignEditorService(db, keitaro)
    try:
        state = service.remove_offer(campaign_id, offer_id)
    except CampaignNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OfferNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except KeitaroAPIError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    return CampaignStateResponse.model_validate(state)


@router.get("/offers", response_model=list[OfferSearchItem])
def search_offers(
    q: str = "",
    keitaro: KeitaroClient = Depends(get_keitaro_client),
) -> list[OfferSearchItem]:
    try:
        offers = keitaro.search_offers(q)
    except KeitaroAPIError as exc:
        raise HTTPException(status_code=502, detail=exc.message) from exc
    return [
        OfferSearchItem(id=int(o["id"]), name=str(o.get("name", ""))) for o in offers
    ]