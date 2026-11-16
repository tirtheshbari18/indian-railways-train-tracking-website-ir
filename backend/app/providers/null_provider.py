from typing import List, Dict, Optional
from datetime import datetime
from backend.app.providers.base import TrainTrackingProvider
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.tracking import LiveStatusResponse, LiveStatusStop
from backend.app.schemas.station import StationLiveBoardItem, StationResponse

class NullProvider(TrainTrackingProvider):
    """
    Null / Offline Provider.
    Adheres strictly to the requirement:
    'Never fabricate live positions, platforms, delays, or train services; show live data unavailable when no verified provider exists.'
    """

    @property
    def provider_id(self) -> str:
        return "null"

    @property
    def provider_name(self) -> str:
        return "No Live Feed Configured"

    @property
    def is_verified_feed(self) -> bool:
        return False

    def get_live_status(
        self,
        train: Train,
        stops: List[Stop],
        journey_date: Optional[str] = None
    ) -> LiveStatusResponse:
        now = datetime.utcnow()
        date_str = journey_date or now.strftime("%Y-%m-%d")

        live_stops: List[LiveStatusStop] = []
        for stop in stops:
            live_stops.append(
                LiveStatusStop(
                    station_code=stop.station_code,
                    station_name=stop.station.name if stop.station else stop.station_code,
                    stop_sequence=stop.stop_sequence,
                    scheduled_arrival=stop.arrival_time,
                    scheduled_departure=stop.departure_time,
                    actual_arrival=None,
                    actual_departure=None,
                    delay_arrival_minutes=0,
                    delay_departure_minutes=0,
                    halt_minutes=stop.halt_minutes,
                    distance_km=stop.distance_km,
                    day_number=stop.day_number,
                    platform=stop.platform,
                    platform_source="scheduled",
                    status="UPCOMING",
                    latitude=stop.station.latitude if stop.station else 0.0,
                    longitude=stop.station.longitude if stop.station else 0.0,
                )
            )

        return LiveStatusResponse(
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            journey_date=date_str,
            source_station=StationResponse.model_validate(train.source_station),
            destination_station=StationResponse.model_validate(train.destination_station),
            is_live_available=False,
            provider_name="None (Live Feed Disconnected)",
            data_provenance="unavailable",
            status_summary="UNAVAILABLE",
            current_status_description="Live telemetry feed is currently not connected. Showing official scheduled timetable only.",
            delay_minutes=0,
            speed_kmh=None,
            last_reported_station=None,
            last_reported_time=None,
            next_station=None,
            eta_next_station=None,
            current_latitude=None,
            current_longitude=None,
            progress_percentage=0.0,
            last_updated_timestamp=now,
            stops=live_stops
        )

    def get_station_live_board(
        self,
        station: Station,
        stops: List[Stop]
    ) -> Dict[str, List[StationLiveBoardItem]]:
        arrivals: List[StationLiveBoardItem] = []
        departures: List[StationLiveBoardItem] = []

        for stop in stops:
            train = stop.train
            if not train:
                continue

            item = StationLiveBoardItem(
                train_number=train.train_number,
                train_name=train.train_name,
                train_type=train.train_type,
                source_station_code=train.source_station_code,
                destination_station_code=train.destination_station_code,
                scheduled_arrival=stop.arrival_time,
                scheduled_departure=stop.departure_time,
                expected_arrival=stop.arrival_time,
                expected_departure=stop.departure_time,
                delay_arrival_minutes=0,
                delay_departure_minutes=0,
                platform=stop.platform,
                platform_source="scheduled",
                status="SCHEDULED",
                direction="ORIGINATING" if stop.stop_sequence == 1 else (
                    "TERMINATING" if stop.arrival_time and not stop.departure_time else "HALTING"
                ),
                data_provenance="CRIS/IR Static Timetable (No live telemetry)"
            )

            if stop.arrival_time:
                arrivals.append(item)
            if stop.departure_time:
                departures.append(item)

        return {"arrivals": arrivals, "departures": departures}
