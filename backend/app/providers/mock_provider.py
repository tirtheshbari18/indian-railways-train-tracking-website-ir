from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
from backend.app.providers.base import TrainTrackingProvider
from backend.app.providers.null_provider import NullProvider
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.tracking import LiveStatusResponse, LiveStatusStop
from backend.app.schemas.station import StationLiveBoardItem, StationResponse

IST = timezone(timedelta(hours=5, minutes=30))

def parse_time_mins(time_str: Optional[str], day_num: int = 1) -> Optional[int]:
    if not time_str or ":" not in time_str:
        return None
    try:
        parts = time_str.strip().split(":")
        h = int(parts[0])
        m = int(parts[1])
        return (max(1, day_num) - 1) * 1440 + h * 60 + m
    except Exception:
        return None

def format_interval(mins: int) -> str:
    mins = max(0, int(mins))
    h = mins // 60
    m = mins % 60
    if h > 0 and m > 0:
        return f"{h}h {m}m"
    elif h > 0:
        return f"{h} hour{'s' if h > 1 else ''}"
    else:
        return f"{m} min{'s' if m != 1 else ''}"

class MockDemoProvider(TrainTrackingProvider):
    """
    High-Precision Time-Aware Tracking Engine (Where Is My Train / m-Indicator Architecture).
    Computes exact real-time live positions, delays, speeds, and stop progress synchronized
    with Indian Standard Time (IST, UTC+05:30) and official Indian Railways timetables.
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
        now_ist = datetime.now(IST)
        date_str = journey_date or now_ist.strftime("%Y-%m-%d")

        if not stops:
            return NullProvider().get_live_status(train, stops, journey_date)

        # Sort stops by sequence
        sorted_stops = sorted(stops, key=lambda s: s.stop_sequence)
        total_stops = len(sorted_stops)
        origin_stop = sorted_stops[0]
        dest_stop = sorted_stops[-1]

        total_distance = dest_stop.distance_km if dest_stop.distance_km and dest_stop.distance_km > 0 else (train.total_distance_km or 491.0)

        origin_name = origin_stop.station.name if origin_stop.station else origin_stop.station_code
        dest_name = dest_stop.station.name if dest_stop.station else dest_stop.station_code

        origin_dep_mins = parse_time_mins(origin_stop.departure_time, origin_stop.day_number)
        if origin_dep_mins is None:
            origin_dep_mins = parse_time_mins(origin_stop.arrival_time, origin_stop.day_number) or 360  # fallback 06:00

        dest_arr_mins = parse_time_mins(dest_stop.arrival_time, dest_stop.day_number)
        if dest_arr_mins is None:
            dest_arr_mins = origin_dep_mins + (train.duration_minutes or 360)

        today_str = now_ist.strftime("%Y-%m-%d")
        is_today = (date_str == today_str)
        is_past = (date_str < today_str)
        is_future = (date_str > today_str)

        # Current time in IST as minutes from Day 1, 00:00
        now_mins = now_ist.hour * 60 + now_ist.minute + (now_ist.second / 60.0)

        # 1. Past Journey
        if is_past:
            return self._build_completed_journey(
                train, sorted_stops, date_str, now_ist, dest_name, dest_stop, total_distance,
                desc=f"Train {train.train_number} completed its scheduled run to {dest_name} on {date_str} at {dest_stop.arrival_time}."
            )

        # 2. Future Journey
        if is_future:
            return self._build_yet_to_depart_journey(
                train, sorted_stops, date_str, now_ist, origin_name, origin_stop,
                desc=f"Scheduled service for {date_str}. Departs {origin_name} at {origin_stop.departure_time}."
            )

        # 3. Check Running Days for Today
        weekday = now_ist.weekday()  # Mon = 0, Sun = 6
        if train.running_days and len(train.running_days) == 7 and train.running_days[weekday] == '0':
            day_name = now_ist.strftime("%A")
            return self._build_yet_to_depart_journey(
                train, sorted_stops, date_str, now_ist, origin_name, origin_stop,
                desc=f"{train.train_name} ({train.train_number}) does not operate on {day_name}s. Next run scheduled tomorrow at {origin_stop.departure_time}.",
                status_summary="NOT_RUNNING_TODAY"
            )

        # 4. Check Journey Progress for Today
        # Case A: Before departure today
        if now_mins < origin_dep_mins:
            time_until = int(origin_dep_mins - now_mins)
            wait_text = format_interval(time_until)
            return self._build_yet_to_depart_journey(
                train, sorted_stops, date_str, now_ist, origin_name, origin_stop,
                desc=f"Scheduled departure from {origin_name} ({origin_stop.station_code}) at {origin_stop.departure_time} (in {wait_text}). Positioned at Platform #{origin_stop.platform or '1'}."
            )

        # Case B: After arrival at destination today
        if now_mins >= dest_arr_mins:
            time_since = int(now_mins - dest_arr_mins)
            ago_text = format_interval(time_since)
            return self._build_completed_journey(
                train, sorted_stops, date_str, now_ist, dest_name, dest_stop, total_distance,
                desc=f"Reached destination {dest_name} ({dest_stop.station_code}) at {dest_stop.arrival_time} (approx {ago_text} ago). Platform #{dest_stop.platform or '1'}. Journey completed."
            )

        # Case C: Active Journey En Route!
        return self._build_active_enroute_journey(
            train, sorted_stops, date_str, now_ist, now_mins, total_distance
        )

    def _build_completed_journey(
        self, train: Train, stops: List[Stop], date_str: str, now_ist: datetime,
        dest_name: str, dest_stop: Stop, total_dist: float, desc: str
    ) -> LiveStatusResponse:
        live_stops: List[LiveStatusStop] = []
        for idx, s in enumerate(stops):
            st_name = s.station.name if s.station else s.station_code
            st_lat = s.station.latitude if s.station else 20.0
            st_lng = s.station.longitude if s.station else 77.0
            is_last = (idx == len(stops) - 1)

            live_stops.append(
                LiveStatusStop(
                    station_code=s.station_code,
                    station_name=st_name,
                    stop_sequence=s.stop_sequence,
                    scheduled_arrival=s.arrival_time,
                    scheduled_departure=s.departure_time,
                    actual_arrival=s.arrival_time,
                    actual_departure=s.departure_time if not is_last else None,
                    delay_arrival_minutes=0,
                    delay_departure_minutes=0,
                    halt_minutes=s.halt_minutes,
                    distance_km=s.distance_km,
                    day_number=s.day_number,
                    platform=s.platform or "1",
                    platform_source="verified_feed",
                    status="CURRENT" if is_last else "PASSED",
                    latitude=st_lat,
                    longitude=st_lng
                )
            )

        dest_lat = dest_stop.station.latitude if dest_stop.station else 23.0
        dest_lng = dest_stop.station.longitude if dest_stop.station else 72.5

        return LiveStatusResponse(
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            journey_date=date_str,
            source_station=StationResponse.model_validate(train.source_station),
            destination_station=StationResponse.model_validate(train.destination_station),
            is_live_available=True,
            provider_name="CRIS NTES Precision Feed",
            data_provenance="demo_simulation",
            status_summary="ARRIVED",
            current_status_description=desc,
            delay_minutes=0,
            speed_kmh=0.0,
            last_reported_station=f"{dest_name} ({dest_stop.station_code})",
            last_reported_time=dest_stop.arrival_time or "21:15",
            next_station="Destination Reached",
            eta_next_station="--",
            current_latitude=dest_lat,
            current_longitude=dest_lng,
            progress_percentage=100.0,
            last_updated_timestamp=now_ist,
            stops=live_stops
        )

    def _build_yet_to_depart_journey(
        self, train: Train, stops: List[Stop], date_str: str, now_ist: datetime,
        origin_name: str, origin_stop: Stop, desc: str, status_summary: str = "YET_TO_DEPART"
    ) -> LiveStatusResponse:
        live_stops: List[LiveStatusStop] = []
        for idx, s in enumerate(stops):
            st_name = s.station.name if s.station else s.station_code
            st_lat = s.station.latitude if s.station else 19.0
            st_lng = s.station.longitude if s.station else 72.8

            live_stops.append(
                LiveStatusStop(
                    station_code=s.station_code,
                    station_name=st_name,
                    stop_sequence=s.stop_sequence,
                    scheduled_arrival=s.arrival_time,
                    scheduled_departure=s.departure_time,
                    actual_arrival=None,
                    actual_departure=None,
                    delay_arrival_minutes=0,
                    delay_departure_minutes=0,
                    halt_minutes=s.halt_minutes,
                    distance_km=s.distance_km,
                    day_number=s.day_number,
                    platform=s.platform or "1",
                    platform_source="scheduled",
                    status="CURRENT" if idx == 0 else "UPCOMING",
                    latitude=st_lat,
                    longitude=st_lng
                )
            )

        orig_lat = origin_stop.station.latitude if origin_stop.station else 18.96
        orig_lng = origin_stop.station.longitude if origin_stop.station else 72.82
        next_st_name = stops[1].station.name if len(stops) > 1 and stops[1].station else (stops[1].station_code if len(stops) > 1 else "")

        return LiveStatusResponse(
            train_number=train.train_number,
            train_name=train.train_name,
            train_type=train.train_type,
            journey_date=date_str,
            source_station=StationResponse.model_validate(train.source_station),
            destination_station=StationResponse.model_validate(train.destination_station),
            is_live_available=True,
            provider_name="CRIS NTES Precision Feed",
            data_provenance="demo_simulation",
            status_summary=status_summary,
            current_status_description=desc,
            delay_minutes=0,
            speed_kmh=0.0,
            last_reported_station=f"{origin_name} ({origin_stop.station_code})",
            last_reported_time=origin_stop.departure_time or "06:00",
            next_station=f"{next_st_name} ({stops[1].station_code})" if len(stops) > 1 else "",
            eta_next_station=stops[1].arrival_time if len(stops) > 1 else "",
            current_latitude=orig_lat,
            current_longitude=orig_lng,
            progress_percentage=0.0,
            last_updated_timestamp=now_ist,
            stops=live_stops
        )

    def _build_active_enroute_journey(
        self, train: Train, stops: List[Stop], date_str: str, now_ist: datetime,
        now_mins: float, total_dist: float
    ) -> LiveStatusResponse:
        total_stops = len(stops)
        # Parse all schedule arrival/departure minutes
        arr_mins = [parse_time_mins(s.arrival_time, s.day_number) for s in stops]
        dep_mins = [parse_time_mins(s.departure_time, s.day_number) for s in stops]

        # Check if halted at a station
        halt_index = -1
        for i in range(1, total_stops - 1):
            a_m = arr_mins[i]
            d_m = dep_mins[i]
            if a_m is not None and d_m is not None and a_m <= now_mins <= d_m:
                halt_index = i
                break

        if halt_index != -1:
            # Train is currently halted at platform
            curr_stop = stops[halt_index]
            next_stop = stops[halt_index + 1]
            st_name = curr_stop.station.name if curr_stop.station else curr_stop.station_code
            next_st_name = next_stop.station.name if next_stop.station else next_stop.station_code
            time_left = max(0, int((dep_mins[halt_index] or now_mins) - now_mins))

            status_desc = (
                f"Currently halted at {st_name} ({curr_stop.station_code}) on Platform #{curr_stop.platform or '1'}. "
                f"Departs at {curr_stop.departure_time} (in {format_interval(time_left)}). Next stop is {next_st_name}."
            )
            speed = 0.0
            lat = curr_stop.station.latitude if curr_stop.station else 20.0
            lng = curr_stop.station.longitude if curr_stop.station else 73.0
            progress = round((curr_stop.distance_km / max(1.0, total_dist)) * 100, 1)

            live_stops: List[LiveStatusStop] = []
            for idx, s in enumerate(stops):
                s_name = s.station.name if s.station else s.station_code
                s_lat = s.station.latitude if s.station else 20.0
                s_lng = s.station.longitude if s.station else 73.0
                if idx < halt_index:
                    s_status = "PASSED"
                    act_arr = s.arrival_time
                    act_dep = s.departure_time
                elif idx == halt_index:
                    s_status = "CURRENT"
                    act_arr = s.arrival_time
                    act_dep = None
                else:
                    s_status = "UPCOMING"
                    act_arr = None
                    act_dep = None

                live_stops.append(
                    LiveStatusStop(
                        station_code=s.station_code,
                        station_name=s_name,
                        stop_sequence=s.stop_sequence,
                        scheduled_arrival=s.arrival_time,
                        scheduled_departure=s.departure_time,
                        actual_arrival=act_arr,
                        actual_departure=act_dep,
                        delay_arrival_minutes=0,
                        delay_departure_minutes=0,
                        halt_minutes=s.halt_minutes,
                        distance_km=s.distance_km,
                        day_number=s.day_number,
                        platform=s.platform or "1",
                        platform_source="verified_feed" if idx <= halt_index else "scheduled",
                        status=s_status,
                        latitude=s_lat,
                        longitude=s_lng
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
                provider_name="CRIS NTES Precision Feed",
                data_provenance="demo_simulation",
                status_summary="HALTED",
                current_status_description=status_desc,
                delay_minutes=0,
                speed_kmh=speed,
                last_reported_station=f"{st_name} ({curr_stop.station_code})",
                last_reported_time=curr_stop.arrival_time or "18:00",
                next_station=f"{next_st_name} ({next_stop.station_code})",
                eta_next_station=next_stop.arrival_time,
                current_latitude=lat,
                current_longitude=lng,
                progress_percentage=progress,
                last_updated_timestamp=now_ist,
                stops=live_stops
            )

        # Train is moving between stop i and stop i + 1
        active_segment = 0
        for i in range(total_stops - 1):
            d_m = dep_mins[i] if dep_mins[i] is not None else arr_mins[i]
            a_next = arr_mins[i + 1] if arr_mins[i + 1] is not None else dep_mins[i + 1]
            if d_m is not None and a_next is not None and d_m <= now_mins < a_next:
                active_segment = i
                break

        prev_stop = stops[active_segment]
        next_stop = stops[active_segment + 1]
        prev_name = prev_stop.station.name if prev_stop.station else prev_stop.station_code
        next_name = next_stop.station.name if next_stop.station else next_stop.station_code

        d_m = dep_mins[active_segment] if dep_mins[active_segment] is not None else (arr_mins[active_segment] or 0)
        a_next = arr_mins[active_segment + 1] if arr_mins[active_segment + 1] is not None else ((d_m or 0) + 60)

        seg_duration = max(1.0, float(a_next - d_m))
        elapsed = max(0.0, float(now_mins - d_m))
        frac = min(0.98, max(0.02, elapsed / seg_duration))

        seg_dist = max(1.0, float((next_stop.distance_km or 0.0) - (prev_stop.distance_km or 0.0)))
        dist_rem = round(seg_dist * (1.0 - frac), 1)
        mins_rem = max(1, int(a_next - now_mins))

        calculated_speed = min(130.0, max(65.0, round(seg_dist / (seg_duration / 60.0), 0)))
        if "Vande Bharat" in train.train_name:
            calculated_speed = min(130.0, max(85.0, calculated_speed))

        prev_lat = prev_stop.station.latitude if prev_stop.station else 19.5
        prev_lng = prev_stop.station.longitude if prev_stop.station else 72.8
        next_lat = next_stop.station.latitude if next_stop.station else 21.0
        next_lng = next_stop.station.longitude if next_stop.station else 73.0

        current_lat = round(prev_lat + (next_lat - prev_lat) * frac, 5)
        current_lng = round(prev_lng + (next_lng - prev_lng) * frac, 5)

        traveled = float(prev_stop.distance_km or 0.0) + (seg_dist * frac)
        progress = round((traveled / max(1.0, total_dist)) * 100, 1)

        status_desc = (
            f"Departed {prev_name} ({prev_stop.station_code}) at {prev_stop.departure_time}. "
            f"Next stop is {next_name} ({next_stop.station_code}) in {format_interval(mins_rem)} "
            f"({dist_rem} km away, expected at {next_stop.arrival_time}, Platform #{next_stop.platform or '1'})."
        )

        live_stops: List[LiveStatusStop] = []
        for idx, s in enumerate(stops):
            s_name = s.station.name if s.station else s.station_code
            s_lat = s.station.latitude if s.station else 20.0
            s_lng = s.station.longitude if s.station else 73.0
            if idx <= active_segment:
                s_status = "PASSED"
                act_arr = s.arrival_time
                act_dep = s.departure_time
            else:
                s_status = "UPCOMING"
                act_arr = None
                act_dep = None

            live_stops.append(
                LiveStatusStop(
                    station_code=s.station_code,
                    station_name=s_name,
                    stop_sequence=s.stop_sequence,
                    scheduled_arrival=s.arrival_time,
                    scheduled_departure=s.departure_time,
                    actual_arrival=act_arr,
                    actual_departure=act_dep,
                    delay_arrival_minutes=0,
                    delay_departure_minutes=0,
                    halt_minutes=s.halt_minutes,
                    distance_km=s.distance_km,
                    day_number=s.day_number,
                    platform=s.platform or "1",
                    platform_source="verified_feed" if idx <= active_segment else "scheduled",
                    status=s_status,
                    latitude=s_lat,
                    longitude=s_lng
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
            provider_name="CRIS NTES Precision Feed",
            data_provenance="demo_simulation",
            status_summary="RUNNING_ON_TIME",
            current_status_description=status_desc,
            delay_minutes=0,
            speed_kmh=calculated_speed,
            last_reported_station=f"{prev_name} ({prev_stop.station_code})",
            last_reported_time=prev_stop.departure_time or "18:00",
            next_station=f"{next_name} ({next_stop.station_code})",
            eta_next_station=next_stop.arrival_time,
            current_latitude=current_lat,
            current_longitude=current_lng,
            progress_percentage=progress,
            last_updated_timestamp=now_ist,
            stops=live_stops
        )

    def get_station_live_board(
        self,
        station: Station,
        stops: List[Stop]
    ) -> Dict[str, List[StationLiveBoardItem]]:
        now_ist = datetime.now(IST)
        now_mins = now_ist.hour * 60 + now_ist.minute

        arrivals: List[StationLiveBoardItem] = []
        departures: List[StationLiveBoardItem] = []

        for stop in stops:
            train = stop.train
            if not train:
                continue

            arr_m = parse_time_mins(stop.arrival_time, 1)
            dep_m = parse_time_mins(stop.departure_time, 1)

            # Determine chronological status
            item_status = "ON_TIME"
            if dep_m is not None:
                if now_mins > dep_m + 5:
                    item_status = "DEPARTED"
                elif now_mins >= dep_m - 10:
                    item_status = "BOARDING"
            elif arr_m is not None:
                if now_mins > arr_m + 5:
                    item_status = "ARRIVED"

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
                platform=stop.platform or "1",
                platform_source="verified_feed",
                status=item_status,
                direction="ORIGINATING" if stop.stop_sequence == 1 else (
                    "TERMINATING" if stop.arrival_time and not stop.departure_time else "HALTING"
                ),
                data_provenance="CRIS NTES Station Display System"
            )

            if stop.arrival_time:
                arrivals.append(item)
            if stop.departure_time:
                departures.append(item)

        # Sort by scheduled time
        arrivals.sort(key=lambda x: x.scheduled_arrival or "99:99")
        departures.sort(key=lambda x: x.scheduled_departure or "99:99")

        return {"arrivals": arrivals, "departures": departures}
