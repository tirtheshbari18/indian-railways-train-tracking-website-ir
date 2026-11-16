from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.train_service import get_train_by_number
from backend.app.providers.factory import get_tracking_provider, get_available_providers
from backend.app.schemas.tracking import LiveStatusResponse, TrackingProviderInfo

router = APIRouter(prefix="/tracking", tags=["Live Tracking & Telemetry"])

@router.get("/provider-info", response_model=TrackingProviderInfo)
def get_provider_info(provider: Optional[str] = Query(None)):
    active = get_tracking_provider(provider)
    return TrackingProviderInfo(
        active_provider=active.provider_id,
        description=f"{active.provider_name} (Verified: {active.is_verified_feed})",
        available_providers=get_available_providers(),
        is_live_available=active.provider_id != "null"
    )

@router.get("/train/{train_number}/live", response_model=LiveStatusResponse)
def get_live_train_status(
    train_number: str,
    date: Optional[str] = Query(None, description="Journey date YYYY-MM-DD"),
    provider: Optional[str] = Query(None, description="Provider override: 'mock', 'api', or 'null'"),
    db: Session = Depends(get_db)
):
    train = get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Train '{train_number}' not found."
        )

    tracking_provider = get_tracking_provider(provider)
    return tracking_provider.get_live_status(train, train.stops, date)
