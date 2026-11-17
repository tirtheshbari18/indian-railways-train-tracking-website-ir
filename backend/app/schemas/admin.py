from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class ValidationErrorDetail(BaseModel):
    row_index: int
    field: str
    message: str
    raw_data: Optional[Dict[str, Any]] = None

class ImportValidationResult(BaseModel):
    is_valid: bool
    total_rows: int
    valid_rows_count: int
    error_rows_count: int
    entity_type: str # "stations", "trains", "timetables"
    errors: List[ValidationErrorDetail] = []
    preview: List[Dict[str, Any]] = []

class ImportResult(BaseModel):
    success: bool
    imported_count: int
    updated_count: int
    errors_count: int
    message: str

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AdminCompletenessStats(BaseModel):
    stations_count: int
    trains_count: int
    stops_count: int
    alerts_count: int
    users_count: int
    audit_logs_count: int
    # Category counts
    memu_count: int
    demu_count: int
    emu_count: int
    local_count: int
    express_count: int
    superfast_count: int
    passenger_count: int
    mail_count: int
    weekly_count: int
    special_count: int
    # Breakdown dictionaries
    trains_by_category: Dict[str, int]
    stations_by_zone: Dict[str, int]
    stations_by_division: Dict[str, int]
    missing_route_trains_count: int
    duplicate_records_checked: bool = True
    records_requiring_verification: int = 0
