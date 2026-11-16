import csv
import io
import json
import re
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from backend.app.models.station import Station
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.audit import AuditLog
from backend.app.schemas.admin import ImportValidationResult, ValidationErrorDetail, ImportResult

TIME_REGEX = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")

def parse_raw_data(file_content: str, filename: str) -> List[Dict[str, Any]]:
    file_content = file_content.strip()
    if filename.lower().endswith(".json") or file_content.startswith("["):
        try:
            data = json.loads(file_content)
            if not isinstance(data, list):
                raise ValueError("JSON content must be a list of records.")
            return data
        except Exception as e:
            raise ValueError(f"Invalid JSON format: {str(e)}")
    else:
        # Parse CSV
        try:
            reader = csv.DictReader(io.StringIO(file_content))
            return [dict(row) for row in reader]
        except Exception as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

def validate_stations_data(db: Session, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[ValidationErrorDetail]]:
    valid_records = []
    errors = []

    for idx, row in enumerate(records, start=1):
        code = str(row.get("code", "")).strip().upper()
        name = str(row.get("name", "")).strip()
        lat_raw = row.get("latitude")
        lng_raw = row.get("longitude")

        if not code or len(code) < 2 or len(code) > 10:
            errors.append(ValidationErrorDetail(row_index=idx, field="code", message="Station code must be between 2 and 10 alphanumeric characters.", raw_data=row))
            continue

        if not name:
            errors.append(ValidationErrorDetail(row_index=idx, field="name", message="Station name is required.", raw_data=row))
            continue

        try:
            lat = float(lat_raw)
            if not (-90.0 <= lat <= 90.0):
                raise ValueError()
        except Exception:
            errors.append(ValidationErrorDetail(row_index=idx, field="latitude", message="Latitude must be a valid float between -90 and 90.", raw_data=row))
            continue

        try:
            lng = float(lng_raw)
            if not (-180.0 <= lng <= 180.0):
                raise ValueError()
        except Exception:
            errors.append(ValidationErrorDetail(row_index=idx, field="longitude", message="Longitude must be a valid float between -180 and 180.", raw_data=row))
            continue

        platforms = 1
        if row.get("platforms_count"):
            try:
                platforms = int(row.get("platforms_count"))
            except Exception:
                platforms = 1

        valid_records.append({
            "code": code,
            "name": name,
            "division": row.get("division"),
            "zone": row.get("zone"),
            "state": row.get("state"),
            "latitude": lat,
            "longitude": lng,
            "platforms_count": platforms
        })

    return valid_records, errors

def validate_trains_data(db: Session, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[ValidationErrorDetail]]:
    valid_records = []
    errors = []
    existing_stations = {s.code for s in db.query(Station.code).all()}

    for idx, row in enumerate(records, start=1):
        train_num = str(row.get("train_number", "")).strip().upper()
        train_name = str(row.get("train_name", "")).strip()
        src_code = str(row.get("source_station_code", "")).strip().upper()
        dst_code = str(row.get("destination_station_code", "")).strip().upper()

        if not train_num or len(train_num) < 4:
            errors.append(ValidationErrorDetail(row_index=idx, field="train_number", message="Train number must be at least 4 digits/characters.", raw_data=row))
            continue

        if not train_name:
            errors.append(ValidationErrorDetail(row_index=idx, field="train_name", message="Train name is required.", raw_data=row))
            continue

        if src_code not in existing_stations:
            errors.append(ValidationErrorDetail(row_index=idx, field="source_station_code", message=f"Source station code '{src_code}' does not exist in the database.", raw_data=row))
            continue

        if dst_code not in existing_stations:
            errors.append(ValidationErrorDetail(row_index=idx, field="destination_station_code", message=f"Destination station code '{dst_code}' does not exist in the database.", raw_data=row))
            continue

        if src_code == dst_code:
            errors.append(ValidationErrorDetail(row_index=idx, field="destination_station_code", message="Source and Destination station cannot be the same.", raw_data=row))
            continue

        dist = 0.0
        try:
            if row.get("total_distance_km"):
                dist = float(row.get("total_distance_km"))
        except Exception:
            dist = 0.0

        dur = 0
        try:
            if row.get("duration_minutes"):
                dur = int(row.get("duration_minutes"))
        except Exception:
            dur = 0

        # Classes
        raw_classes = row.get("classes", ["1A", "2A", "3A", "SL"])
        if isinstance(raw_classes, str):
            classes = [c.strip() for c in raw_classes.split(",") if c.strip()]
        elif isinstance(raw_classes, list):
            classes = raw_classes
        else:
            classes = ["1A", "2A", "3A", "SL"]

        pantry = True
        if str(row.get("pantry_car", "")).lower() in ["false", "0", "no"]:
            pantry = False

        valid_records.append({
            "train_number": train_num,
            "train_name": train_name,
            "train_type": row.get("train_type") or "Superfast",
            "source_station_code": src_code,
            "destination_station_code": dst_code,
            "running_days": str(row.get("running_days") or "1111111"),
            "total_distance_km": dist,
            "duration_minutes": dur,
            "classes": classes,
            "pantry_car": pantry,
            "return_train_number": row.get("return_train_number")
        })

    return valid_records, errors

def validate_timetables_data(db: Session, records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[ValidationErrorDetail]]:
    valid_records = []
    errors = []
    existing_stations = {s.code for s in db.query(Station.code).all()}
    existing_trains = {t.train_number: t.id for t in db.query(Train.train_number, Train.id).all()}

    for idx, row in enumerate(records, start=1):
        train_num = str(row.get("train_number", "")).strip().upper()
        station_code = str(row.get("station_code", "")).strip().upper()
        seq_raw = row.get("stop_sequence")

        if train_num not in existing_trains:
            errors.append(ValidationErrorDetail(row_index=idx, field="train_number", message=f"Train '{train_num}' does not exist in database.", raw_data=row))
            continue

        if station_code not in existing_stations:
            errors.append(ValidationErrorDetail(row_index=idx, field="station_code", message=f"Station '{station_code}' does not exist in database.", raw_data=row))
            continue

        try:
            seq = int(seq_raw)
            if seq < 1:
                raise ValueError()
        except Exception:
            errors.append(ValidationErrorDetail(row_index=idx, field="stop_sequence", message="Stop sequence must be a positive integer >= 1.", raw_data=row))
            continue

        arr = row.get("arrival_time")
        if arr and not TIME_REGEX.match(arr.strip()):
            errors.append(ValidationErrorDetail(row_index=idx, field="arrival_time", message="Arrival time must be in HH:MM (24-hour) format.", raw_data=row))
            continue

        dep = row.get("departure_time")
        if dep and not TIME_REGEX.match(dep.strip()):
            errors.append(ValidationErrorDetail(row_index=idx, field="departure_time", message="Departure time must be in HH:MM (24-hour) format.", raw_data=row))
            continue

        halt = 0
        try:
            if row.get("halt_minutes"):
                halt = int(row.get("halt_minutes"))
        except Exception:
            halt = 0

        dist = 0.0
        try:
            if row.get("distance_km"):
                dist = float(row.get("distance_km"))
        except Exception:
            dist = 0.0

        day = 1
        try:
            if row.get("day_number"):
                day = int(row.get("day_number"))
        except Exception:
            day = 1

        valid_records.append({
            "train_id": existing_trains[train_num],
            "train_number": train_num,
            "station_code": station_code,
            "stop_sequence": seq,
            "arrival_time": arr.strip() if arr else None,
            "departure_time": dep.strip() if dep else None,
            "halt_minutes": halt,
            "distance_km": dist,
            "day_number": day,
            "platform": str(row.get("platform")).strip() if row.get("platform") else None
        })

    return valid_records, errors

def validate_import_data(
    db: Session,
    entity_type: str,
    file_content: str,
    filename: str
) -> ImportValidationResult:
    records = parse_raw_data(file_content, filename)
    total_rows = len(records)
    entity_type = entity_type.lower()

    if entity_type == "stations":
        valid_records, errors = validate_stations_data(db, records)
    elif entity_type == "trains":
        valid_records, errors = validate_trains_data(db, records)
    elif entity_type in ["timetables", "stops"]:
        valid_records, errors = validate_timetables_data(db, records)
    else:
        raise ValueError(f"Unknown entity type: {entity_type}. Expected 'stations', 'trains', or 'timetables'.")

    return ImportValidationResult(
        is_valid=len(errors) == 0,
        total_rows=total_rows,
        valid_rows_count=len(valid_records),
        error_rows_count=len(errors),
        entity_type=entity_type,
        errors=errors[:50],  # Return up to first 50 errors
        preview=valid_records[:5]
    )

def execute_import_data(
    db: Session,
    entity_type: str,
    file_content: str,
    filename: str,
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    ip_address: Optional[str] = None
) -> ImportResult:
    records = parse_raw_data(file_content, filename)
    entity_type = entity_type.lower()
    imported_count = 0
    updated_count = 0

    if entity_type == "stations":
        valid_records, errors = validate_stations_data(db, records)
        if not valid_records:
            return ImportResult(success=False, imported_count=0, updated_count=0, errors_count=len(errors), message="No valid station rows to import.")

        for item in valid_records:
            station = db.query(Station).filter(Station.code == item["code"]).first()
            if station:
                for k, v in item.items():
                    setattr(station, k, v)
                updated_count += 1
            else:
                st = Station(**item)
                db.add(st)
                imported_count += 1

    elif entity_type == "trains":
        valid_records, errors = validate_trains_data(db, records)
        if not valid_records:
            return ImportResult(success=False, imported_count=0, updated_count=0, errors_count=len(errors), message="No valid train rows to import.")

        for item in valid_records:
            train = db.query(Train).filter(Train.train_number == item["train_number"]).first()
            if train:
                for k, v in item.items():
                    setattr(train, k, v)
                updated_count += 1
            else:
                tr = Train(**item)
                db.add(tr)
                imported_count += 1

    elif entity_type in ["timetables", "stops"]:
        valid_records, errors = validate_timetables_data(db, records)
        if not valid_records:
            return ImportResult(success=False, imported_count=0, updated_count=0, errors_count=len(errors), message="No valid timetable rows to import.")

        for item in valid_records:
            # Delete train_number before feeding to model Stop
            t_id = item["train_id"]
            seq = item["stop_sequence"]
            existing_stop = db.query(Stop).filter(Stop.train_id == t_id, Stop.stop_sequence == seq).first()
            item_model = {k: v for k, v in item.items() if k != "train_number"}
            if existing_stop:
                for k, v in item_model.items():
                    setattr(existing_stop, k, v)
                updated_count += 1
            else:
                stop = Stop(**item_model)
                db.add(stop)
                imported_count += 1

    # Record Audit Log
    audit = AuditLog(
        user_id=user_id,
        username=username or "admin",
        action=f"IMPORT_{entity_type.upper()}",
        entity_type=entity_type,
        entity_id=None,
        details={
            "filename": filename,
            "imported_count": imported_count,
            "updated_count": updated_count,
            "errors_count": len(errors)
        },
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    return ImportResult(
        success=True,
        imported_count=imported_count,
        updated_count=updated_count,
        errors_count=len(errors),
        message=f"Successfully imported {imported_count} new and updated {updated_count} existing {entity_type} records."
    )
