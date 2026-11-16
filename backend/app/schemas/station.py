from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class StationBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=10, description="Station code e.g. NDLS")
    name: str = Field(..., min_length=2, max_length=100)
    division: Optional[str] = None
    zone: Optional[str] = None
    state: Optional[str] = None
    latitude: float
    longitude: float
    platforms_count: Optional[int] = 1

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    name: Optional[str] = None
    division: Optional[str] = None
    zone: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    platforms_count: Optional[int] = None

class StationResponse(StationBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StationLiveBoardItem(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    source_station_code: str
    destination_station_code: str
    scheduled_arrival: Optional[str] = None
    scheduled_departure: Optional[str] = None
    expected_arrival: Optional[str] = None
    expected_departure: Optional[str] = None
    delay_arrival_minutes: int = 0
    delay_departure_minutes: int = 0
    platform: Optional[str] = None
    platform_source: str = "scheduled" # "scheduled", "verified_feed", "estimated"
    status: str = "ON_TIME" # "ON_TIME", "LATE", "HALTED", "DEPARTED", "CANCELLED"
    direction: str = "THROUGH" # "ORIGINATING", "TERMINATING", "HALTING"
    data_provenance: str = "CRIS/IR Static Timetable"

class StationDetailResponse(StationResponse):
    arrivals: List[StationLiveBoardItem] = []
    departures: List[StationLiveBoardItem] = []
