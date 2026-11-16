from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from backend.app.models.train import Train
from backend.app.models.stop import Stop
from backend.app.models.station import Station
from backend.app.schemas.tracking import LiveStatusResponse
from backend.app.schemas.station import StationLiveBoardItem

class TrainTrackingProvider(ABC):
    """
    Abstract interface for Train Tracking and Live Status data providers.
    Supports pluggable implementations (Live NTES/RailTel API, Demo Simulator, or Null Provider).
    """

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique identifier of the provider."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider label."""
        pass

    @property
    @abstractmethod
    def is_verified_feed(self) -> bool:
        """True if backed by official/licensed CRIS, RailTel, or IRCTC API feed."""
        pass

    @abstractmethod
    def get_live_status(
        self,
        train: Train,
        stops: List[Stop],
        journey_date: Optional[str] = None
    ) -> LiveStatusResponse:
        """Fetch live running status for a train."""
        pass

    @abstractmethod
    def get_station_live_board(
        self,
        station: Station,
        stops: List[Stop]
    ) -> Dict[str, List[StationLiveBoardItem]]:
        """Fetch live arrival/departure board for a station."""
        pass
