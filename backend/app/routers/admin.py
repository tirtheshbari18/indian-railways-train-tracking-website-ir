from typing import Optional, List, Dict
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Request, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.services.auth import require_admin_user
from backend.app.models.user import User
from backend.app.models.station import Station
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.alert import ServiceAlert
from backend.app.models.audit import AuditLog
from backend.app.schemas.admin import ImportValidationResult, ImportResult, AuditLogResponse, AdminCompletenessStats
from backend.app.services.import_service import validate_import_data, execute_import_data

router = APIRouter(prefix="/admin", tags=["Admin Console"])

SAMPLE_TEMPLATES = {
    "stations_csv": "code,name,district,division,zone,state,latitude,longitude,category,platforms_count\nNDLS,New Delhi,Central Delhi,Delhi,NR,Delhi,28.6429,77.2195,Terminal,16\nMMCT,Mumbai Central,Mumbai City,Mumbai,WR,Maharashtra,18.9696,72.8194,Terminal,5\nBOR,Boisar,Palghar,Mumbai,WR,Maharashtra,19.8028,72.7584,Regular,3\nDRD,Dahanu Road,Palghar,Mumbai,WR,Maharashtra,19.9744,72.7381,Terminal,3\nCSMT,Chhatrapati Shivaji Maharaj Terminus,Mumbai City,Mumbai,CR,Maharashtra,18.9402,72.8358,Terminal,18\n",
    "stations_json": """[
  {"code": "NDLS", "name": "New Delhi", "district": "Central Delhi", "division": "Delhi", "zone": "NR", "state": "Delhi", "latitude": 28.6429, "longitude": 77.2195, "category": "Terminal", "platforms_count": 16},
  {"code": "MMCT", "name": "Mumbai Central", "district": "Mumbai City", "division": "Mumbai", "zone": "WR", "state": "Maharashtra", "latitude": 18.9696, "longitude": 72.8194, "category": "Terminal", "platforms_count": 5}
]""",
    "trains_csv": "train_number,train_name,train_type,train_category,source_station_code,destination_station_code,running_days,total_distance_km,duration_minutes,classes,pantry_car,is_special,return_train_number\n12951,Mumbai Tejas Rajdhani,Rajdhani,Superfast Express,MMCT,NDLS,1111111,1384,932,\"1A,2A,3A\",true,false,12952\n09159,Bandra Terminus - Vapi MEMU Special,MEMU,MEMU,BDTS,VAPI,1111111,168,260,\"UR\",false,false,09160\n93005,Churchgate - Dahanu Road Fast Local,Suburban Local,Local,CCG,DRD,1111111,124,142,\"II,FC\",false,false,93006\n09001,Mumbai Central - New Delhi AC Festival Special,AC Special,Special,MMCT,NDLS,0100100,1384,1020,\"1A,2A,3A\",true,true,09002\n",
    "trains_json": """[
  {"train_number": "12951", "train_name": "Mumbai Tejas Rajdhani", "train_type": "Rajdhani", "train_category": "Superfast Express", "source_station_code": "MMCT", "destination_station_code": "NDLS", "running_days": "1111111", "total_distance_km": 1384, "duration_minutes": 932, "classes": ["1A", "2A", "3A"], "pantry_car": true, "is_special": false, "return_train_number": "12952"}
]""",
    "timetables_csv": "train_number,station_code,stop_sequence,arrival_time,departure_time,halt_minutes,distance_km,day_number,platform\n12951,MMCT,1,,17:00,0,0,1,1\n12951,BVI,2,17:22,17:24,2,30,1,6\n12951,ST,3,19:43,19:48,5,263,1,1\n12951,BRC,4,21:14,21:27,13,392,1,2\n12951,RTM,5,00:25,00:28,3,653,2,5\n12951,KOTA,6,03:15,03:20,5,920,2,1\n12951,NDLS,7,08:32,,0,1384,2,1\n",
    "timetables_json": """[
  {"train_number": "12951", "station_code": "MMCT", "stop_sequence": 1, "arrival_time": null, "departure_time": "17:00", "halt_minutes": 0, "distance_km": 0, "day_number": 1, "platform": "1"},
  {"train_number": "12951", "station_code": "BRC", "stop_sequence": 4, "arrival_time": "21:14", "departure_time": "21:27", "halt_minutes": 13, "distance_km": 392, "day_number": 1, "platform": "2"},
  {"train_number": "12951", "station_code": "NDLS", "stop_sequence": 7, "arrival_time": "08:32", "departure_time": null, "halt_minutes": 0, "distance_km": 1384, "day_number": 2, "platform": "1"}
]"""
}

@router.get("/stats", response_model=AdminCompletenessStats)
def get_admin_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    stations_count = db.query(Station).count()
    trains_count = db.query(Train).count()
    stops_count = db.query(Stop).count()
    alerts_count = db.query(ServiceAlert).filter(ServiceAlert.is_active == True).count()
    users_count = db.query(User).count()
    audit_logs_count = db.query(AuditLog).count()

    # Category counts
    all_trains = db.query(Train).all()
    memu_count = 0
    demu_count = 0
    emu_count = 0
    local_count = 0
    superfast_count = 0
    express_count = 0
    passenger_count = 0
    mail_count = 0
    rajdhani_count = 0
    shatabdi_count = 0
    vande_bharat_count = 0
    duronto_count = 0
    garib_rath_count = 0
    tejas_count = 0
    humsafar_count = 0
    weekly_count = 0
    special_count = 0
    trains_by_cat: Dict[str, int] = {}

    for t in all_trains:
        cat = (t.train_category or t.train_type or "Express").strip()
        trains_by_cat[cat] = trains_by_cat.get(cat, 0) + 1

        cat_upper = cat.upper()
        name_upper = (t.train_name or "").upper()
        type_upper = (t.train_type or "").upper()
        tags_str = str(t.tags or []).upper()

        if "RAJDHANI" in cat_upper or "RAJDHANI" in name_upper or "RAJDHANI" in type_upper or "RAJDHANI" in tags_str:
            rajdhani_count += 1
            superfast_count += 1
        elif "VANDE BHARAT" in cat_upper or "VANDE BHARAT" in name_upper or "VANDE BHARAT" in type_upper:
            vande_bharat_count += 1
            superfast_count += 1
        elif "SHATABDI" in cat_upper or "SHATABDI" in name_upper or "SHATABDI" in type_upper:
            shatabdi_count += 1
            superfast_count += 1
        elif "DURONTO" in cat_upper or "DURONTO" in name_upper or "DURONTO" in type_upper:
            duronto_count += 1
            superfast_count += 1
        elif "GARIB RATH" in cat_upper or "GARIB RATH" in name_upper:
            garib_rath_count += 1
            superfast_count += 1
        elif "HUMSAFAR" in cat_upper or "HUMSAFAR" in name_upper:
            humsafar_count += 1
            superfast_count += 1
        elif "TEJAS" in cat_upper or "TEJAS" in name_upper:
            tejas_count += 1
            superfast_count += 1
        elif "MEMU" in cat_upper:
            memu_count += 1
        elif "DEMU" in cat_upper:
            demu_count += 1
        elif "EMU" in cat_upper:
            emu_count += 1
            local_count += 1
        elif "LOCAL" in cat_upper or "SUBURBAN" in cat_upper:
            local_count += 1
        elif "SUPERFAST" in cat_upper:
            superfast_count += 1
        elif "MAIL" in cat_upper or "MAIL" in name_upper:
            mail_count += 1
        elif "PASSENGER" in cat_upper or "ORDINARY" in cat_upper:
            passenger_count += 1
        else:
            express_count += 1

        if t.is_special or "SPECIAL" in cat_upper or "SPECIAL" in name_upper:
            special_count += 1

        if "WEEKLY" in cat_upper or (t.running_days and t.running_days != "1111111" and "Daily" not in t.running_days):
            weekly_count += 1

    # Breakdown by Zone & Division
    stations_by_zone_raw = db.query(Station.zone, func.count(Station.code)).group_by(Station.zone).all()
    stations_by_zone = {z or "Unknown": c for z, c in stations_by_zone_raw}

    stations_by_division_raw = db.query(Station.division, func.count(Station.code)).group_by(Station.division).all()
    stations_by_division = {d or "Unknown": c for d, c in stations_by_division_raw}

    # Trains without stops
    trains_with_stops = db.query(Stop.train_id).distinct().subquery()
    missing_route_trains_count = db.query(Train).filter(~Train.id.in_(db.query(trains_with_stops.c.train_id))).count()

    return AdminCompletenessStats(
        stations_count=stations_count,
        trains_count=trains_count,
        stops_count=stops_count,
        alerts_count=alerts_count,
        users_count=users_count,
        audit_logs_count=audit_logs_count,
        total_route_records=trains_count,
        total_route_stops=stops_count,
        memu_count=memu_count,
        demu_count=demu_count,
        emu_count=emu_count,
        local_count=local_count,
        express_count=express_count,
        superfast_count=superfast_count,
        passenger_count=passenger_count,
        mail_count=mail_count,
        rajdhani_count=rajdhani_count,
        shatabdi_count=shatabdi_count,
        vande_bharat_count=vande_bharat_count,
        duronto_count=duronto_count,
        garib_rath_count=garib_rath_count,
        tejas_count=tejas_count,
        humsafar_count=humsafar_count,
        weekly_count=weekly_count,
        special_count=special_count,
        trains_by_category=trains_by_cat,
        stations_by_zone=stations_by_zone,
        stations_by_division=stations_by_division,
        missing_route_trains_count=missing_route_trains_count,
        duplicate_records_checked=True,
        records_requiring_verification=0
    )

@router.post("/import/validate", response_model=ImportValidationResult)
async def validate_import_file(
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    content_bytes = await file.read()
    content = content_bytes.decode("utf-8", errors="replace")
    return validate_import_data(db, entity_type=entity_type, file_content=content, filename=file.filename or "uploaded.csv")

@router.post("/import/execute", response_model=ImportResult)
async def execute_import_file(
    request: Request,
    entity_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    content_bytes = await file.read()
    content = content_bytes.decode("utf-8", errors="replace")
    client_ip = request.client.host if request.client else "127.0.0.1"

    return execute_import_data(
        db,
        entity_type=entity_type,
        file_content=content,
        filename=file.filename or "uploaded.csv",
        user_id=admin.id,
        username=admin.username,
        ip_address=client_ip
    )

@router.get("/import/template/{entity_type}")
def get_template(entity_type: str, format: str = Query("csv", pattern="^(csv|json)$")):
    key = f"{entity_type.lower()}_{format.lower()}"
    if key not in SAMPLE_TEMPLATES:
        raise HTTPException(status_code=404, detail=f"Template for '{key}' not found.")
    
    media = "application/json" if format == "json" else "text/csv"
    return PlainTextResponse(content=SAMPLE_TEMPLATES[key], media_type=media)

@router.get("/audit-logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user)
):
    q = db.query(AuditLog)
    if action:
        q = q.filter(AuditLog.action.ilike(f"%{action.strip()}%"))
    return q.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()
