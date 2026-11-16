from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class ServiceAlertBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    alert_type: str = "delay" # "delay", "cancellation", "diversion", "special", "weather", "maintenance"
    severity: str = "warning" # "info", "warning", "critical"
    description: str = Field(..., min_length=5)
    affected_train_numbers: List[str] = []
    affected_station_codes: List[str] = []
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None
    is_active: bool = True

class ServiceAlertCreate(ServiceAlertBase):
    pass

class ServiceAlertUpdate(BaseModel):
    title: Optional[str] = None
    alert_type: Optional[str] = None
    severity: Optional[str] = None
    description: Optional[str] = None
    affected_train_numbers: Optional[List[str]] = None
    affected_station_codes: Optional[List[str]] = None
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None
    is_active: Optional[bool] = None

class ServiceAlertResponse(ServiceAlertBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
