from typing import Optional
from backend.app.config import settings
from backend.app.providers.base import TrainTrackingProvider
from backend.app.providers.mock_provider import MockDemoProvider
from backend.app.providers.api_provider import ExternalApiProvider
from backend.app.providers.null_provider import NullProvider

_mock_instance = MockDemoProvider()
_api_instance = ExternalApiProvider()
_null_instance = NullProvider()

def get_tracking_provider(provider_override: Optional[str] = None) -> TrainTrackingProvider:
    provider_name = (provider_override or settings.TRACKING_PROVIDER or "mock").lower()

    if provider_name == "api":
        return _api_instance
    elif provider_name == "null" or provider_name == "offline" or provider_name == "unavailable":
        return _null_instance
    else:
        return _mock_instance

def get_available_providers() -> list:
    return ["mock", "api", "null"]
