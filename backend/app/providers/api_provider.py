import logging
from typing import List, Dict, Optional
from datetime import datetime
import httpx
from backend.app.config import settings
from backend.app.providers.base import TrainTrackingProvider
from backend.app.providers.null_provider import NullProvider
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.tracking import LiveStatusResponse, LiveStatusStop
from backend.app.schemas.station import StationLiveBoardItem, StationResponse

logger = logging.getLogger(__name__)

class ExternalApiProvider(TrainTrackingProvider):
    """
    Adapter for connecting official or licensed Indian Railways APIs
    (such as CRIS NTES, RailTel Open Data, or RapidAPI IRCTC Live Status endpoints).
    """

    def __init__(self, api_url: Optional[str] = None, api_key: Optional[str] = None):
        self.api_url = api_url or settings.EXTERNAL_API_URL
        self.api_key = api_key or settings.EXTERNAL_API_KEY
        self.fallback = NullProvider()

    @property
    def provider_id(self) -> str:
        return "api"

    @property
    def provider_name(self) -> str:
        return "Indian Railways NTES / RailTel Live API Gateway"

    @property
    def is_verified_feed(self) -> bool:
        return True

    def get_live_status(
        self,
        train: Train,
        stops: List[Stop],
        journey_date: Optional[str] = None
    ) -> LiveStatusResponse:
        now = datetime.utcnow()
        date_str = journey_date or now.strftime("%Y-%m-%d")

        if not self.api_url:
            # Fall back safely if no endpoint is configured
            resp = self.fallback.get_live_status(train, stops, journey_date)
            resp.current_status_description = "External API Gateway URL is not configured. Live feed unavailable."
            return resp

        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            params = {"train_no": train.train_number, "start_date": date_str}
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.api_url}/train/live-status", headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    # Parse data from external API schema
                    return self._map_external_payload(data, train, stops, date_str)
                else:
                    logger.warning(f"Live API returned status {res.status_code}")
        except Exception as e:
            logger.error(f"Live API request error: {e}")

        # When external API is unreachable or fails, never fabricate data
        fallback_resp = self.fallback.get_live_status(train, stops, journey_date)
        fallback_resp.current_status_description = "Live tracking service temporarily unreachable. Showing scheduled timetable."
        return fallback_resp

    def get_station_live_board(
        self,
        station: Station,
        stops: List[Stop]
    ) -> Dict[str, List[StationLiveBoardItem]]:
        if not self.api_url:
            return self.fallback.get_station_live_board(station, stops)
        
        # When live endpoint configured, request live station board
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.api_url}/station/{station.code}/live-board", headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    # Return parsed live items
                    return data
        except Exception as e:
            logger.error(f"Station live board API error: {e}")

        return self.fallback.get_station_live_board(station, stops)

    def _map_external_payload(
        self,
        payload: Dict,
        train: Train,
        stops: List[Stop],
        date_str: str
    ) -> LiveStatusResponse:
        # Standardized normalization from real external provider payload
        now = datetime.utcnow()
        live_stops: List[LiveStatusStop] = []
        for stop in stops:
            live_stops.append(
                LiveStatusStop(
                    station_code=stop.station_code,
                    station_name=stop.station.name if stop.station else stop.station_code,
                    stop_sequence=stop.stop_sequence,
                    scheduled_arrival=stop.arrival_time,
                    scheduled_departure=stop.departure_time,
                    actual_arrival=payload.get("actual_arrival"),
                    actual_departure=payload.get("actual_departure"),
                    delay_arrival_minutes=payload.get("delay_minutes", 0),
                    delay_departure_minutes=payload.get("delay_minutes", 0),
                    halt_minutes=stop.halt_minutes,
                    distance_km=stop.distance_km,
                    day_number=stop.day_number,
                    platform=payload.get("platform", stop.platform),
                    platform_source="verified_feed",
                    status=payload.get("status", "UPCOMING"),
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
            is_live_available=True,
            provider_name=self.provider_name,
            data_provenance="verified_live_feed",
            status_summary=payload.get("status_summary", "RUNNING_ON_TIME"),
            current_status_description=payload.get("current_status_description", "Running as per schedule"),
            delay_minutes=payload.get("delay_minutes", 0),
            speed_kmh=payload.get("speed_kmh"),
            last_reported_station=payload.get("last_reported_station"),
            last_reported_time=payload.get("last_reported_time"),
            next_station=payload.get("next_station"),
            eta_next_station=payload.get("eta_next_station"),
            current_latitude=payload.get("latitude"),
            current_longitude=payload.get("longitude"),
            progress_percentage=payload.get("progress_percentage", 0.0),
            last_updated_timestamp=now,
            stops=live_stops
        )
