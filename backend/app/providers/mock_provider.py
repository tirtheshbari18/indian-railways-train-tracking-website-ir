import random
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from backend.app.providers.base import TrainTrackingProvider
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.tracking import LiveStatusResponse, LiveStatusStop
from backend.app.schemas.station import StationLiveBoardItem, StationResponse

class MockDemoProvider(TrainTrackingProvider):
    """
    Simulation Demo Provider for portfolio showcases.
    Emulates National Train Enquiry System (NTES) data feeds with realistic telemetry,
    clearly labelled as DEMO/SIMULATION so as not to mislead users.
    """

    @property
    def provider_id(self) -> str:
        return "mock"

    @property
    def provider_name(self) -> str:
        return "CRIS NTES Emulated Demo Feed"

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

        if not stops:
            return NullProvider().get_live_status(train, stops, journey_date)

        # Deterministic simulation based on train_number so results are consistent for demo
        seed_num = int("".join([c for c in train.train_number if c.isdigit()]) or "12951")
        rng = random.Random(seed_num + int(now.strftime("%Y%m%d%H")))

        total_stops = len(stops)
        # Determine simulated position (e.g., somewhere in the middle of journey)
        if total_stops <= 2:
            current_idx = 0
            progress_pct = 50.0
        else:
            # Select an intermediate stop as last departed
            current_idx = min(max(1, (seed_num % (total_stops - 1))), total_stops - 2)
            progress_pct = round(((current_idx + 0.5) / total_stops) * 100, 1)

        simulated_delay = (seed_num * 7) % 35  # 0 to 34 minutes delay
        if simulated_delay <= 5:
            delay_text = "On Time"
            status_summary = "RUNNING_ON_TIME"
        else:
            delay_text = f"{simulated_delay} min late"
            status_summary = "RUNNING_LATE"

        speed = 85.0 + (seed_num % 35)  # 85 to 120 km/h

        live_stops: List[LiveStatusStop] = []
        for idx, stop in enumerate(stops):
            st_name = stop.station.name if stop.station else stop.station_code
            st_lat = stop.station.latitude if stop.station else 20.0
            st_lng = stop.station.longitude if stop.station else 77.0

            if idx < current_idx:
                stop_status = "PASSED"
                arr_delay = simulated_delay
                dep_delay = simulated_delay
                actual_arr = stop.arrival_time
                actual_dep = stop.departure_time
            elif idx == current_idx:
                stop_status = "CURRENT"
                arr_delay = simulated_delay
                dep_delay = simulated_delay
                actual_arr = stop.arrival_time
                actual_dep = None
            else:
                stop_status = "UPCOMING"
                arr_delay = simulated_delay
                dep_delay = simulated_delay
                actual_arr = None
                actual_dep = None

            # Platform sourcing: verified for current/passed, scheduled for upcoming
            platform_src = "verified_feed" if idx <= current_idx else "scheduled"

            live_stops.append(
                LiveStatusStop(
                    station_code=stop.station_code,
                    station_name=st_name,
                    stop_sequence=stop.stop_sequence,
                    scheduled_arrival=stop.arrival_time,
                    scheduled_departure=stop.departure_time,
                    actual_arrival=actual_arr,
                    actual_departure=actual_dep,
                    delay_arrival_minutes=arr_delay if idx <= current_idx else 0,
                    delay_departure_minutes=dep_delay if idx <= current_idx else 0,
                    halt_minutes=stop.halt_minutes,
                    distance_km=stop.distance_km,
                    day_number=stop.day_number,
                    platform=stop.platform,
                    platform_source=platform_src,
                    status=stop_status,
                    latitude=st_lat,
                    longitude=st_lng,
                )
            )

        last_stop = stops[current_idx]
        next_stop = stops[min(current_idx + 1, total_stops - 1)]

        last_st_name = last_stop.station.name if last_stop.station else last_stop.station_code
        next_st_name = next_stop.station.name if next_stop.station else next_stop.station_code

        # Interpolate coordinates midway between last_stop and next_stop for live train marker
        last_lat = last_stop.station.latitude if last_stop.station else 20.0
        last_lng = last_stop.station.longitude if last_stop.station else 77.0
        next_lat = next_stop.station.latitude if next_stop.station else 20.0
        next_lng = next_stop.station.longitude if next_stop.station else 77.0

        current_lat = round(last_lat + (next_lat - last_lat) * 0.45, 5)
        current_lng = round(last_lng + (next_lng - last_lng) * 0.45, 5)

        status_desc = f"Departed {last_st_name} ({last_stop.station_code}) running {delay_text}. Next stop is {next_st_name} ({next_stop.station_code})."

        return LiveStatusResponse(
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            journey_date=date_str,
            source_station=StationResponse.model_validate(train.source_station),
            destination_station=StationResponse.model_validate(train.destination_station),
            is_live_available=True,
            provider_name="CRIS NTES Emulated Demo Feed",
            data_provenance="demo_simulation",
            status_summary=status_summary,
            current_status_description=status_desc,
            delay_minutes=simulated_delay,
            speed_kmh=speed,
            last_reported_station=f"{last_st_name} ({last_stop.station_code})",
            last_reported_time=last_stop.departure_time or last_stop.arrival_time or "18:40",
            next_station=f"{next_st_name} ({next_stop.station_code})",
            eta_next_station=next_stop.arrival_time,
            current_latitude=current_lat,
            current_longitude=current_lng,
            progress_percentage=progress_pct,
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

            seed_num = int("".join([c for c in train.train_number if c.isdigit()]) or "100")
            delay = (seed_num * 3) % 25

            item = StationLiveBoardItem(
                train_number=train.train_number,
                train_name=train.train_name,
                train_type=train.train_type,
                source_station_code=train.source_station_code,
                destination_station_code=train.destination_station_code,
                scheduled_arrival=stop.arrival_time,
                scheduled_departure=stop.departure_time,
                expected_arrival=self._adjust_time(stop.arrival_time, delay),
                expected_departure=self._adjust_time(stop.departure_time, delay),
                delay_arrival_minutes=delay,
                delay_departure_minutes=delay,
                platform=stop.platform,
                platform_source="verified_feed" if delay < 15 else "estimated",
                status="ON_TIME" if delay == 0 else "LATE",
                direction="ORIGINATING" if stop.stop_sequence == 1 else (
                    "TERMINATING" if stop.arrival_time and not stop.departure_time else "HALTING"
                ),
                data_provenance="Demo Simulation Feed (Emulated Live Telemetry)"
            )

            if stop.arrival_time:
                arrivals.append(item)
            if stop.departure_time:
                departures.append(item)

        return {"arrivals": arrivals, "departures": departures}

    def _adjust_time(self, time_str: Optional[str], delay_mins: int) -> Optional[str]:
        if not time_str or ":" not in time_str:
            return time_str
        try:
            parts = time_str.split(":")
            h, m = int(parts[0]), int(parts[1])
            tot = h * 60 + m + delay_mins
            tot = tot % 1440
            return f"{tot // 60:02d}:{tot % 60:02d}"
        except Exception:
            return time_str
