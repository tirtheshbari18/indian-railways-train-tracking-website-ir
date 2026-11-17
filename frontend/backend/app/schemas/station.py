from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class StationBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=10, description="Station code e.g. NDLS, BOR, DRD")
    name: str = Field(..., min_length=2, max_length=100)
    state: Optional[str] = None
    district: Optional[str] = None
    division: Optional[str] = None
    zone: Optional[str] = None
    latitude: float
    longitude: float
    category: Optional[str] = "Regular" # "Junction", "Terminal", "Suburban", "Regular", "Halt"
    platforms_count: Optional[int] = 1
    facilities: Optional[List[str]] = []
    operational_status: Optional[str] = "Operational"

class StationCreate(StationBase):
    pass

class StationUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    division: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    category: Optional[str] = None
    platforms_count: Optional[int] = None
    facilities: Optional[List[str]] = None
    operational_status: Optional[str] = None

class StationResponse(StationBase):
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class StationLiveBoardItem(BaseModel):
    train_number: str
    train_name: str
    train_category: str = "Superfast" # "MEMU", "DEMU", "Local", "Superfast", etc.
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
    total_trains_count: int = 0
