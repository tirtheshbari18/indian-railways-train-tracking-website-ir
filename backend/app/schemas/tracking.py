from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from backend.app.schemas.station import StationResponse

class LiveStatusStop(BaseModel):
    station_code: str
    station_name: str
    stop_sequence: int
    scheduled_arrival: Optional[str] = None
    scheduled_departure: Optional[str] = None
    actual_arrival: Optional[str] = None
    actual_departure: Optional[str] = None
    delay_arrival_minutes: int = 0
    delay_departure_minutes: int = 0
    halt_minutes: int = 0
    distance_km: float = 0.0
    day_number: int = 1
    platform: Optional[str] = None
    platform_source: str = "scheduled" # "scheduled", "verified_feed", "estimated"
    status: str = "UPCOMING" # "PASSED", "CURRENT", "UPCOMING", "CANCELLED"
    latitude: float
    longitude: float

class LiveStatusResponse(BaseModel):
    train_number: str
    train_name: str
    train_type: str
    journey_date: str
    source_station: StationResponse
    destination_station: StationResponse
    
    # Live progress
    is_live_available: bool = True
    provider_name: str # e.g. "Simulated Demo Feed (CRIS NTES Emulated)", "Verified IR NTES Feed", or "None"
    data_provenance: str # "demo_simulation", "verified_live_feed", "scheduled_timetable_only", "unavailable"
    status_summary: str # "RUNNING_ON_TIME", "RUNNING_LATE", "HALTED", "NOT_STARTED", "ARRIVED", "UNAVAILABLE"
    current_status_description: str # "Train departed Gwalior 12m late. Next stop: Jhansi"
    delay_minutes: int = 0
    speed_kmh: Optional[float] = None
    last_reported_station: Optional[str] = None
    last_reported_time: Optional[str] = None
    next_station: Optional[str] = None
    eta_next_station: Optional[str] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    progress_percentage: float = 0.0
    
    last_updated_timestamp: datetime
    stops: List[LiveStatusStop] = []

class TrackingProviderInfo(BaseModel):
    active_provider: str
    description: str
    available_providers: List[str]
    is_live_available: bool
