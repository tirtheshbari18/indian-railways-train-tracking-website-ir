from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.schemas.station import StationResponse, StationDetailResponse, StationCreate, StationUpdate
from backend.app.services.station_service import (
    list_stations,
    get_station_by_code,
    get_station_live_board,
    create_station,
    update_station
)
from backend.app.services.auth import require_admin_user
from backend.app.models.user import User

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("", response_model=List[StationResponse])
def get_stations(
    query: Optional[str] = Query(None, description="Search by station code, name, or district"),
    zone: Optional[str] = Query(None, description="Filter by railway zone e.g. NR, WR, CR"),
    division: Optional[str] = Query(None, description="Filter by railway division e.g. Mumbai, Delhi"),
    state: Optional[str] = Query(None, description="Filter by Indian State"),
    category: Optional[str] = Query(None, description="Filter by station category e.g. Junction, Terminal, Suburban, Regular, Halt"),
    operational_status: Optional[str] = Query(None, description="Operational status"),
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return list_stations(
        db,
        query=query,
        zone=zone,
        state=state,
        division=division,
        category=category,
        operational_status=operational_status,
        limit=limit,
        offset=offset
    )

@router.get("/{station_code}", response_model=StationResponse)
def get_station_detail(station_code: str, db: Session = Depends(get_db)):
    st = get_station_by_code(db, station_code)
    if not st:
        raise HTTPException(status_code=404, detail=f"Station '{station_code}' not found")
    return st

@router.get("/{station_code}/live-board")
def get_station_board(
    station_code: str,
    category: Optional[str] = Query(None, description="Filter passing trains by category (MEMU, DEMU, Local, Express, etc.)"),
    provider: Optional[str] = Query(None, description="Provider override: 'mock', 'api', or 'null'"),
    db: Session = Depends(get_db)
):
    return get_station_live_board(db, station_code, category=category, provider_override=provider)

@router.post("", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
def add_station(
    station_in: StationCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return create_station(db, station_in)

@router.put("/{station_code}", response_model=StationResponse)
def modify_station(
    station_code: str,
    station_in: StationUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    return update_station(db, station_code, station_in)
