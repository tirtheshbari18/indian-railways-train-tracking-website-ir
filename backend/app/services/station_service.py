from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from backend.app.models.station import Station
from backend.app.models.stop import Stop
from backend.app.models.train import Train
from backend.app.schemas.station import StationCreate, StationUpdate
from backend.app.providers.factory import get_tracking_provider

def list_stations(
    db: Session,
    query: Optional[str] = None,
    zone: Optional[str] = None,
    state: Optional[str] = None,
    division: Optional[str] = None,
    category: Optional[str] = None,
    operational_status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> List[Station]:
    q = db.query(Station)
    if query:
        search = f"%{query.strip()}%"
        q = q.filter(
            or_(
                Station.code.ilike(search),
                Station.name.ilike(search),
                Station.district.ilike(search)
            )
        )
    if zone:
        q = q.filter(Station.zone.ilike(zone.strip()))
    if state:
        q = q.filter(Station.state.ilike(state.strip()))
    if division:
        q = q.filter(Station.division.ilike(division.strip()))
    if category:
        q = q.filter(Station.category.ilike(category.strip()))
    if operational_status:
        q = q.filter(Station.operational_status.ilike(operational_status.strip()))

    return q.order_by(Station.code).offset(offset).limit(limit).all()

def get_station_by_code(db: Session, station_code: str) -> Optional[Station]:
    code = station_code.strip().upper()
    return db.query(Station).filter(Station.code == code).first()

def get_station_live_board(
    db: Session,
    station_code: str,
    category: Optional[str] = None,
    provider_override: Optional[str] = None
) -> Dict[str, Any]:
    station = get_station_by_code(db, station_code)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station '{station_code}' not found."
        )

    # Find all stops passing through this station
    q_stops = (
        db.query(Stop)
        .join(Train, Stop.train_id == Train.id)
        .filter(Stop.station_code == station.code)
    )

    if category:
        cat_lower = category.strip().lower()
        if cat_lower in ["local", "emu"]:
            q_stops = q_stops.filter(
                or_(
                    Train.train_category.ilike("%Local%"),
                    Train.train_category.ilike("%EMU%"),
                    Train.train_type.ilike("%Local%"),
                    Train.train_type.ilike("%EMU%")
                )
            )
        elif cat_lower in ["memu", "demu"]:
            q_stops = q_stops.filter(
                or_(
                    Train.train_category.ilike(f"%{category.strip()}%"),
                    Train.train_type.ilike(f"%{category.strip()}%")
                )
            )
        else:
            q_stops = q_stops.filter(
                or_(
                    Train.train_category.ilike(f"%{category.strip()}%"),
                    Train.train_type.ilike(f"%{category.strip()}%")
                )
            )

    stops = q_stops.all()

    provider = get_tracking_provider(provider_override)
    board = provider.get_station_live_board(station, stops)
    return {
        "station": station,
        "arrivals": board.get("arrivals", []),
        "departures": board.get("departures", []),
        "provider": provider.provider_name,
        "is_live_available": provider.provider_id != "null"
    }

def create_station(db: Session, data: StationCreate) -> Station:
    code = data.code.strip().upper()
    existing = get_station_by_code(db, code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Station with code '{code}' already exists."
        )
    station = Station(
        code=code,
        name=data.name.strip(),
        district=data.district,
        division=data.division,
        zone=data.zone,
        state=data.state,
        latitude=data.latitude,
        longitude=data.longitude,
        category=data.category or "Regular",
        facilities=data.facilities,
        operational_status=data.operational_status or "Operational",
        platforms_count=data.platforms_count or 1
    )
    db.add(station)
    db.commit()
    db.refresh(station)
    return station

def update_station(db: Session, station_code: str, data: StationUpdate) -> Station:
    station = get_station_by_code(db, station_code)
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Station '{station_code}' not found."
        )
    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(station, field, val)
    db.commit()
    db.refresh(station)
    return station
