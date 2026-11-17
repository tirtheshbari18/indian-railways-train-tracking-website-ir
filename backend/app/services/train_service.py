import re
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, func, cast, String
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
    # Check if exact code matches
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

    clean_q = query.strip() if query else None

    # Step 1: Detect Origin-Destination pairs inside a single search query if not explicitly passed
    if clean_q and not source and not destination:
        # Check standard separators " to ", " - ", " – ", " -> "
        pair_match = re.split(r'\s+(?:to|-|–|->)\s+', clean_q, flags=re.IGNORECASE)
        if len(pair_match) == 2 and pair_match[0].strip() and pair_match[1].strip():
            src_part = pair_match[0].strip()
            dst_part = pair_match[1].strip()
            src_c = resolve_station_codes(db, src_part)
            dst_c = resolve_station_codes(db, dst_part)
            if src_c and dst_c:
                source = src_part
                destination = dst_part
                clean_q = None

        # Check two-token space-separated queries (e.g. "MMCT NZM", "BOR DRD", "ADI MMCT")
        if clean_q:
            tokens = clean_q.split()
            if len(tokens) == 2:
                # Check if this exact phrase is registered as an alias or train name first
                has_alias = db.query(Train.id).filter(
                    or_(
                        Train.train_number.ilike(clean_q),
                        Train.train_name.ilike(f"%{clean_q}%"),
                        Train.short_name.ilike(f"%{clean_q}%"),
                        cast(Train.aliases, String).ilike(f"%{clean_q}%")
                    )
                ).first()
                if not has_alias:
                    c1 = db.query(Station.code).filter(Station.code.ilike(tokens[0])).first()
                    c2 = db.query(Station.code).filter(Station.code.ilike(tokens[1])).first()
                    if c1 and c2:
                        source = tokens[0]
                        destination = tokens[1]
                        clean_q = None

    # Step 2: Query Matching (Train Number, Full Name, Short Name, Aliases, Tags, Category)
    if clean_q:
        search_pattern = f"%{clean_q}%"
        keywords = [k.strip() for k in clean_q.split() if len(k.strip()) >= 2]

        # Multi-keyword condition: all words must match somewhere across the train entity
        kw_conditions = []
        if len(keywords) > 1:
            for kw in keywords:
                kw_pat = f"%{kw}%"
                kw_conditions.append(
                    or_(
                        Train.train_number.ilike(kw_pat),
                        Train.train_name.ilike(kw_pat),
                        Train.short_name.ilike(kw_pat),
                        cast(Train.aliases, String).ilike(kw_pat),
                        cast(Train.tags, String).ilike(kw_pat),
                        Train.train_category.ilike(kw_pat),
                        Train.train_type.ilike(kw_pat)
                    )
                )

        train_match_filter = or_(
            Train.train_number.ilike(search_pattern),
            Train.train_name.ilike(search_pattern),
            Train.short_name.ilike(search_pattern),
            cast(Train.aliases, String).ilike(search_pattern),
            cast(Train.tags, String).ilike(search_pattern),
            Train.train_category.ilike(search_pattern),
            Train.train_type.ilike(search_pattern),
            and_(*kw_conditions) if len(kw_conditions) > 1 else False
        )

        # Check if direct train match exists
        train_matches_count = db.query(Train.id).filter(train_match_filter).count()

        if train_matches_count > 0:
            q = q.filter(train_match_filter)
        else:
            # If no train matches by name/alias/number, check if query matches an intermediate station (e.g. "Boisar", "Vadodara")
            st_codes = resolve_station_codes(db, clean_q)
            if st_codes:
                matching_train_ids = db.query(Stop.train_id).filter(Stop.station_code.in_(st_codes)).all()
                valid_ids = [t[0] for t in matching_train_ids]
                q = q.filter(
                    or_(
                        Train.source_station_code.in_(st_codes),
                        Train.destination_station_code.in_(st_codes),
                        Train.id.in_(valid_ids)
                    )
                )
            else:
                q = q.filter(train_match_filter)

    # Step 3: Train Type filter
    if train_type:
        q = q.filter(Train.train_type.ilike(f"%{train_type.strip()}%"))

    # Step 4: Category filter (covering all 32 Indian Railways categories)
    if category:
        cat_lower = category.strip().lower()
        if cat_lower == "rajdhani":
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Rajdhani%"),
                    Train.train_category.ilike("%Rajdhani%"),
                    cast(Train.tags, String).ilike("%Rajdhani%")
                )
            )
        elif cat_lower in ["vande bharat", "vb"]:
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Vande Bharat%"),
                    Train.train_category.ilike("%Vande Bharat%"),
                    cast(Train.tags, String).ilike("%Vande Bharat%")
                )
            )
        elif cat_lower == "shatabdi":
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Shatabdi%"),
                    Train.train_category.ilike("%Shatabdi%")
                )
            )
        elif cat_lower == "duronto":
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Duronto%"),
                    Train.train_category.ilike("%Duronto%")
                )
            )
        elif cat_lower == "tejas":
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Tejas%"),
                    Train.train_category.ilike("%Tejas%"),
                    cast(Train.tags, String).ilike("%Tejas%")
                )
            )
        elif cat_lower in ["garib rath", "garibrath"]:
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Garib Rath%"),
                    Train.train_category.ilike("%Garib Rath%")
                )
            )
        elif cat_lower in ["sampark kranti", "sampark"]:
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Sampark Kranti%"),
                    Train.train_category.ilike("%Sampark Kranti%")
                )
            )
        elif cat_lower == "humsafar":
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Humsafar%"),
                    Train.train_category.ilike("%Humsafar%")
                )
            )
        elif cat_lower in ["amrit bharat", "amrit"]:
            q = q.filter(
                or_(
                    Train.train_type.ilike("%Amrit Bharat%"),
                    Train.train_category.ilike("%Amrit Bharat%")
                )
            )
        elif cat_lower in ["local", "emu", "mumbai local"]:
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
        elif cat_lower in ["special", "festival special", "summer special", "winter special", "holiday special"]:
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Special%"),
                    Train.is_special == True,
                    Train.train_name.ilike("%Special%")
                )
            )
        elif cat_lower in ["weekly", "biweekly", "triweekly"]:
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Weekly%"),
                    Train.train_name.ilike("%Weekly%"),
                    Train.running_days.notin_(["1111111", "Daily"])
                )
            )
        elif cat_lower == "superfast":
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Superfast%"),
                    Train.train_type.ilike("%Superfast%"),
                    Train.train_type.ilike("%Rajdhani%"),
                    Train.train_type.ilike("%Vande Bharat%"),
                    Train.train_type.ilike("%Shatabdi%"),
                    Train.train_type.ilike("%Tejas%")
                )
            )
        elif cat_lower == "express":
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Express%"),
                    Train.train_type.ilike("%Express%")
                )
            )
        elif cat_lower == "passenger":
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Passenger%"),
                    Train.train_type.ilike("%Passenger%")
                )
            )
        elif cat_lower == "mail":
            q = q.filter(
                or_(
                    Train.train_category.ilike("%Mail%"),
                    Train.train_type.ilike("%Mail%")
                )
            )
        else:
            q = q.filter(
                or_(
                    Train.train_category.ilike(f"%{category.strip()}%"),
                    Train.train_type.ilike(f"%{category.strip()}%"),
                    cast(Train.tags, String).ilike(f"%{category.strip()}%")
                )
            )

    if is_special is not None:
        q = q.filter(Train.is_special == is_special)

    # Step 5: Origin & Destination search with station name-to-code resolution
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
    # Check exact match first
    train = (
        db.query(Train)
        .options(
            joinedload(Train.source_station),
            joinedload(Train.destination_station),
            joinedload(Train.stops).joinedload(Stop.station)
        )
        .filter(Train.train_number == num)
        .first()
    )
    if train:
        return train

    # If not found directly, check if train_number matches an alias or short name
    train_by_alias = (
        db.query(Train)
        .options(
            joinedload(Train.source_station),
            joinedload(Train.destination_station),
            joinedload(Train.stops).joinedload(Stop.station)
        )
        .filter(
            or_(
                Train.short_name.ilike(num),
                cast(Train.aliases, String).ilike(f'%"{num}"%'),
                cast(Train.aliases, String).ilike(f"%{num}%")
            )
        )
        .first()
    )
    return train_by_alias

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
        short_name=data.short_name.strip() if data.short_name else None,
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
        last_verified_date=data.last_verified_date,
        aliases=data.aliases or [],
        tags=data.tags or []
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
                distance_from_prev=s.distance_from_prev,
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
