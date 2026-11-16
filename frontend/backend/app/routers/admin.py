from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query, Request, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.auth import require_admin_user
from backend.app.models.user import User
from backend.app.models.station import Station
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.alert import ServiceAlert
from backend.app.models.audit import AuditLog
from backend.app.schemas.admin import ImportValidationResult, ImportResult, AuditLogResponse
from backend.app.services.import_service import validate_import_data, execute_import_data

router = APIRouter(prefix="/admin", tags=["Admin Console"])

SAMPLE_TEMPLATES = {
    "stations_csv": "code,name,division,zone,state,latitude,longitude,platforms_count\nNDLS,New Delhi,Delhi,NR,Delhi,28.6429,77.2195,16\nMMCT,Mumbai Central,Mumbai,WR,Maharashtra,18.9696,72.8194,5\nCSMT,Chhatrapati Shivaji Maharaj Terminus,Mumbai,CR,Maharashtra,18.9402,72.8358,18\nHWH,Howrah Junction,Howrah,ER,West Bengal,22.5839,88.3426,23\nMAS,MGR Chennai Central,Chennai,SR,Tamil Nadu,13.0827,80.2754,17\n",
    "stations_json": """[
  {"code": "NDLS", "name": "New Delhi", "division": "Delhi", "zone": "NR", "state": "Delhi", "latitude": 28.6429, "longitude": 77.2195, "platforms_count": 16},
  {"code": "MMCT", "name": "Mumbai Central", "division": "Mumbai", "zone": "WR", "state": "Maharashtra", "latitude": 18.9696, "longitude": 72.8194, "platforms_count": 5}
]""",
    "trains_csv": "train_number,train_name,train_type,source_station_code,destination_station_code,running_days,total_distance_km,duration_minutes,classes,pantry_car,return_train_number\n12951,Mumbai Tejas Rajdhani,Rajdhani,MMCT,NDLS,1111111,1384,932,\"1A,2A,3A\",true,12952\n22436,Vande Bharat Express,Vande Bharat,NDLS,BSB,1101111,759,480,\"EC,CC\",true,22435\n",
    "trains_json": """[
  {"train_number": "12951", "train_name": "Mumbai Tejas Rajdhani", "train_type": "Rajdhani", "source_station_code": "MMCT", "destination_station_code": "NDLS", "running_days": "1111111", "total_distance_km": 1384, "duration_minutes": 932, "classes": ["1A", "2A", "3A"], "pantry_car": true, "return_train_number": "12952"}
]""",
    "timetables_csv": "train_number,station_code,stop_sequence,arrival_time,departure_time,halt_minutes,distance_km,day_number,platform\n12951,MMCT,1,,17:00,0,0,1,1\n12951,ST,2,19:43,19:48,5,263,1,1\n12951,BRC,3,21:06,21:16,10,392,1,2\n12951,RTM,4,00:25,00:28,3,653,2,5\n12951,KOTA,5,03:15,03:20,5,920,2,1\n12951,NDLS,6,08:32,,0,1384,2,1\n",
    "timetables_json": """[
  {"train_number": "12951", "station_code": "MMCT", "stop_sequence": 1, "arrival_time": null, "departure_time": "17:00", "halt_minutes": 0, "distance_km": 0, "day_number": 1, "platform": "1"},
  {"train_number": "12951", "station_code": "ST", "stop_sequence": 2, "arrival_time": "19:43", "departure_time": "19:48", "halt_minutes": 5, "distance_km": 263, "day_number": 1, "platform": "1"},
  {"train_number": "12951", "station_code": "NDLS", "stop_sequence": 3, "arrival_time": "08:32", "departure_time": null, "halt_minutes": 0, "distance_km": 1384, "day_number": 2, "platform": "1"}
]"""
}

@router.get("/stats")
def get_admin_stats(db: Session = Depends(get_db), admin: User = Depends(require_admin_user)):
    return {
        "stations_count": db.query(Station).count(),
        "trains_count": db.query(Train).count(),
        "stops_count": db.query(Stop).count(),
        "alerts_count": db.query(ServiceAlert).filter(ServiceAlert.is_active == True).count(),
        "users_count": db.query(User).count(),
        "audit_logs_count": db.query(AuditLog).count()
    }

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
