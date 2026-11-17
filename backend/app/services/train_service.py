from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func
from fastapi import HTTPException, status
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.train import TrainCreate, TrainUpdate

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

def resolve_station_codes(db: Session, text: str) -> List[str]:
    """
    Resolve station codes given user input (could be station code 'BOR' or name 'Boisar').
    """
    txt = text.strip()
    if not txt:
        return []

    codes = set()
    # Check if exact code
    direct = db.query(Station.code).filter(Station.code.ilike(txt)).first()
    if direct:
        codes.add(direct[0].upper())

    # Check station name matching (prefix, full match, or contains)
    name_matches = (
        db.query(Station.code)
        .filter(
            or_(
                Station.code.ilike(txt),
                Station.name.ilike(txt),
                Station.name.ilike(f"{txt}%"),
                Station.name.ilike(f"%{txt}%")
            )
        )
        .limit(10)
        .all()
    )
    for m in name_matches:
        codes.add(m[0].upper())

    return list(codes)

def search_trains(
    db: Session,
    query: Optional[str] = None,
    source: Optional[str] = None,
    destination: Optional[str] = None,
    station: Optional[str] = None,
    train_type: Optional[str] = None,
    category: Optional[str] = None,
    day: Optional[str] = None,
    is_special: Optional[bool] = None,
    limit: int = 50,
    offset: int = 0
) -> Tuple[List[Train], int]:
    q = db.query(Train).options(
        joinedload(Train.source_station),
        joinedload(Train.destination_station)
    )

    # Detect "X to Y" in query if source and destination aren't explicitly passed
    if query and not source and not destination:
        clean_q = query.strip()
        sep = None
        if " to " in clean_q.lower():
            sep = " to "
        elif " - " in clean_q:
            sep = " - "
        
        if sep:
            parts = clean_q.lower().split(sep)
            if len(parts) == 2 and parts[0].strip() and parts[1].strip():
                source = parts[0].strip()
                destination = parts[1].strip()
                query = None  # Clear query so we do a pair search

    if query:
        search = f"%{query.strip()}%"
        # First check if query matches train number or name
        q = q.filter(
            or_(
                Train.train_number.ilike(search),
                Train.train_name.ilike(search)
            )
        )

    # Train Type filter (e.g. Rajdhani, Vande Bharat)
    if train_type:
        q = q.filter(Train.train_type.ilike(f"%{train_type.strip()}%"))

    # Train Category filter (e.g. MEMU, DEMU, EMU, Local, Superfast, Express, Passenger, Mail, Weekly, Special)
    if category:
        cat_lower = category.strip().lower()
        if cat_lower in ["local", "emu"]:
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Local%"),
                    Train.train_category.ilike("%EMU%"),
                    Train.train_type.ilike("%Local%"),
                    Train.train_type.ilike("%EMU%")
                )
            )
        elif cat_lower in ["memu", "demu"]:
            q = q.filter(
                or_(
                    Train.train_category.ilike(f"%{category.strip()}%"),
                    Train.train_type.ilike(f"%{category.strip()}%")
                )
            )
        elif cat_lower in ["special", "festival special", "holiday special"]:
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Special%"),
                    Train.is_special == True,
                    Train.train_name.ilike("%Special%")
                )
            )
        elif cat_lower == "weekly":
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Weekly%"),
                    Train.train_name.ilike("%Weekly%"),
                    Train.running_days.notin_(["1111111", "Daily"])
                )
            )
        else:
            q = q.filter(
                or_(
                    Train.train_category.ilike(f"%{category.strip()}%"),
                    Train.train_type.ilike(f"%{category.strip()}%")
                )
            )

    if is_special is not None:
        q = q.filter(Train.is_special == is_special)

    # Origin & Destination search with station name-to-code resolution
    if source and destination:
        src_codes = resolve_station_codes(db, source)
        dst_codes = resolve_station_codes(db, destination)

        if not src_codes:
            src_codes = [source.strip().upper()]
        if not dst_codes:
            dst_codes = [destination.strip().upper()]

        # Find train IDs where source stop sequence < destination stop sequence
        stop_src = db.query(Stop.train_id, Stop.stop_sequence).filter(Stop.station_code.in_(src_codes)).subquery()
        stop_dst = db.query(Stop.train_id, Stop.stop_sequence).filter(Stop.station_code.in_(dst_codes)).subquery()

        matching_train_ids = (
            db.query(stop_src.c.train_id)
            .join(stop_dst, stop_src.c.train_id == stop_dst.c.train_id)
            .filter(stop_src.c.stop_sequence < stop_dst.c.stop_sequence)
            .all()
        )
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(Train.id.in_(valid_ids))

    elif source:
        src_codes = resolve_station_codes(db, source)
        if not src_codes:
            src_codes = [source.strip().upper()]
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code.in_(src_codes)).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(Train.source_station_code.in_(src_codes), Train.id.in_(valid_ids)))

    elif destination:
        dst_codes = resolve_station_codes(db, destination)
        if not dst_codes:
            dst_codes = [destination.strip().upper()]
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code.in_(dst_codes)).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(Train.destination_station_code.in_(dst_codes), Train.id.in_(valid_ids)))

    elif station:
        st_codes = resolve_station_codes(db, station)
        if not st_codes:
            st_codes = [station.strip().upper()]
        matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code.in_(st_codes)).all()
        valid_ids = [t[0] for t in matching_train_ids]
        q = q.filter(or_(
            Train.source_station_code.in_(st_codes),
            Train.destination_station_code.in_(st_codes),
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
                mask = t.running_days or ""
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
        train_category=data.train_category or data.train_type or "Express",
        source_station_code=src.code,
        destination_station_code=dst.code,
        running_days=data.running_days,
        total_distance_km=data.total_distance_km,
        duration_minutes=data.duration_minutes,
        classes=data.classes or ["1A", "2A", "3A", "SL"],
        pantry_car=data.pantry_car,
        return_train_number=data.return_train_number,
        validity_start=data.validity_start,
        validity_end=data.validity_end,
        is_special=data.is_special or False,
        is_active=data.is_active if data.is_active is not None else True,
        source_of_data=data.source_of_data or "CRIS_OFFICIAL",
        last_verified_date=data.last_verified_date
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
