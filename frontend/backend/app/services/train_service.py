from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from fastapi import HTTPException, status
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.train import TrainCreate, TrainUpdate

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def search_trains(
    db: Session,
    query: Optional[str] = None,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    station: Optional[str] = None,
    train_type: Optional[str] = None,
    day: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Train], int]:
    q = db.query(Train).options(
        joinedload(Train.source_station),
        joinedload(Train.destination_station)
    )

    if query:
        search = f"%{query.strip()}%"
        q = q.filter(
            or_(
                Train.train_number.ilike(search),
                Train.train_name.ilike(search)
            )
        )

    if train_type:
        q = q.filter(Train.train_type.ilike(f"%{train_type.strip()}%"))

    # Origin & Destination search
    if source and destination:
        src_code = source.strip().upper()
        dst_code = destination.strip().upper()
        # Direct origin/destination match OR sub-route stops match
        # Let's find train IDs where src stop sequence < dst stop sequence
        stop_src = db.query(Stop.train_id, Stop.stop_sequence).filter(Stop.station_code == src_code).subquery()
        stop_dst = db.query(Stop.train_id, Stop.stop_sequence).filter(Stop.station_code == dst_code).subquery()

        matching_train_ids = (
            db.query(stop_src.c.train_id)
            .join(stop_dst, stop_src.c.train_id == stop_dst.c.train_id)
            .filter(stop_src.c.stop_sequence < stop_dst.c.stop_sequence)
            .all()
        )
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(Train.id.in_(valid_ids))

    elif source:
        src_code = source.strip().upper()
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code == src_code).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(Train.source_station_code == src_code, Train.id.in_(valid_ids)))

    elif destination:
        dst_code = destination.strip().upper()
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code == dst_code).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(Train.destination_station_code == dst_code, Train.id.in_(valid_ids)))

    elif station:
        st_code = station.strip().upper()
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code == st_code).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(
            Train.source_station_code == st_code,
            Train.destination_station_code == st_code,
            Train.id.in_(valid_ids)
        ))

    total = q.count()
    trains = q.order_by(Train.train_number).offset(offset).limit(limit).all()

    # Optional day filter in python (since running_days can be mask like "1111111" or names)
    if day:
        day_str = day.strip().capitalize()[:3]
        if day_str in DAY_NAMES:
            day_idx = DAY_NAMES.index(day_str)
            filtered = []
            for t in trains:
                mask = t.running_days
                if len(mask) == 7 and mask[day_idx] == '1':
                    filtered.append(t)
                elif day_str.lower() in mask.lower() or "daily" in mask.lower():
                    filtered.append(t)
            return filtered, len(filtered)

    return trains, total

def get_train_by_number(db: Session, train_number: str) -> Optional[Train]:
    num = train_number.strip().upper()
    return (
        db.query(Train)
        .options(
            joinedload(Train.source_station),
            joinedload(Train.destination_station),
            joinedload(Train.stops).joinedload(Stop.station)
        )
        .filter(Train.train_number == num)
        .first()
    )

def get_train_by_id(db: Session, train_id: int) -> Optional[Train]:
    return (
        db.query(Train)
        .options(
            joinedload(Train.source_station),
            joinedload(Train.destination_station),
            joinedload(Train.stops).joinedload(Stop.station)
        )
        .filter(Train.id == train_id)
        .first()
    )

def create_train(db: Session, data: TrainCreate) -> Train:
    num = data.train_number.strip().upper()
    existing = get_train_by_number(db, num)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Train with number '{num}' already exists."
        )

    # Validate source and destination stations exist
    src = db.query(Station).filter(Station.code == data.source_station_code.strip().upper()).first()
    if not src:
        raise HTTPException(status_code=400, detail=f"Source station '{data.source_station_code}' does not exist.")
    dst = db.query(Station).filter(Station.code == data.destination_station_code.strip().upper()).first()
    if not dst:
        raise HTTPException(status_code=400, detail=f"Destination station '{data.destination_station_code}' does not exist.")

    train = Train(
        train_number=num,
        train_name=data.train_name.strip(),
        train_type=data.train_type,
        source_station_code=src.code,
        destination_station_code=dst.code,
        running_days=data.running_days,
        total_distance_km=data.total_distance_km,
        duration_minutes=data.duration_minutes,
        classes=data.classes or ["1A", "2A", "3A", "SL"],
        pantry_car=data.pantry_car,
        return_train_number=data.return_train_number
    )
    db.add(train)
    db.flush()

    if data.stops:
        for s in data.stops:
            stop = Stop(
                train_id=train.id,
                station_code=s.station_code.strip().upper(),
                stop_sequence=s.stop_sequence,
                arrival_time=s.arrival_time,
                departure_time=s.departure_time,
                halt_minutes=s.halt_minutes,
                distance_km=s.distance_km,
                day_number=s.day_number,
                platform=s.platform
            )
            db.add(stop)

    db.commit()
    return get_train_by_id(db, train.id)

def update_train(db: Session, train_number: str, data: TrainUpdate) -> Train:
    train = get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train '{train_number}' not found.")

    update_dict = data.model_dump(exclude_unset=True)
    for field, val in update_dict.items():
        setattr(train, field, val)

    db.commit()
    return get_train_by_id(db, train.id)

def delete_train(db: Session, train_number: str) -> bool:
    train = get_train_by_number(db, train_number)
    if not train:
        raise HTTPException(status_code=404, detail=f"Train '{train_number}' not found.")
    db.delete(train)
    db.commit()
    return True
