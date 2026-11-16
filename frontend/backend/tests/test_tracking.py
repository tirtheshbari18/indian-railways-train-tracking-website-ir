def test_live_tracking_mock_provider(client):
    response = client.get("/api/v1/tracking/train/12951/live?provider=mock")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "12951"
    assert data["is_live_available"] is True
    assert data["data_provenance"] == "demo_simulation"
    assert data["current_latitude"] is not None
    assert data["current_longitude"] is not None
    assert len(data["stops"]) > 0

def test_live_tracking_null_provider_unavailable(client):
    # Verify strict requirement: when no verified feed is available, status is explicitly unavailable
    response = client.get("/api/v1/tracking/train/12951/live?provider=null")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "12951"
    assert data["is_live_available"] is False
    assert data["data_provenance"] == "unavailable"
    assert data["status_summary"] == "UNAVAILABLE"
    assert data["current_latitude"] is None
    assert data["current_longitude"] is None

def test_provider_info_endpoint(client):
    response = client.get("/api/v1/tracking/provider-info")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data
    assert "mock" in data["available_providers"]
    assert "null" in data["available_providers"]
