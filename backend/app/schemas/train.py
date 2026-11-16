from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from backend.app.schemas.station import StationResponse

class StopBase(BaseModel):
    station_code: str
    stop_sequence: int
    arrival_time: Optional[str] = None
    departure_time: Optional[str] = None
    halt_minutes: int = 0
    distance_km: float = 0.0
    day_number: int = 1
    platform: Optional[str] = None

class StopCreate(StopBase):
    pass

class StopResponse(StopBase):
    id: int
    station: Optional[StationResponse] = None
    model_config = ConfigDict(from_attributes=True)

class TrainBase(BaseModel):
    train_number: str = Field(..., min_length=4, max_length=10)
    train_name: str = Field(..., min_length=2, max_length=150)
    train_type: str = "Superfast"
    source_station_code: str
    destination_station_code: str
    running_days: str = "1111111"  # Mon-Sun mask or days
    total_distance_km: float = 0.0
    duration_minutes: int = 0
    classes: List[str] = ["1A", "2A", "3A", "SL"]
    pantry_car: bool = True
    return_train_number: Optional[str] = None

class TrainCreate(TrainBase):
    stops: Optional[List[StopCreate]] = None

class TrainUpdate(BaseModel):
    train_name: Optional[str] = None
    train_type: Optional[str] = None
    source_station_code: Optional[str] = None
    destination_station_code: Optional[str] = None
    running_days: Optional[str] = None
    total_distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    classes: Optional[List[str]] = None
    pantry_car: Optional[bool] = None
    return_train_number: Optional[str] = None

class TrainResponse(TrainBase):
    id: int
    created_at: datetime
    source_station: Optional[StationResponse] = None
    destination_station: Optional[StationResponse] = None
    model_config = ConfigDict(from_attributes=True)

class TrainDetailResponse(TrainResponse):
    stops: List[StopResponse] = []

class TrainSearchQuery(BaseModel):
    query: Optional[str] = None # train number or name
    source: Optional[str] = None
    destination: Optional[str] = None
    station: Optional[str] = None
    train_type: Optional[str] = None
    day: Optional[str] = None
