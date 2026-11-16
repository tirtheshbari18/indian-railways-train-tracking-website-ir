def test_list_stations(client):
    response = client.get("/api/v1/stations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    codes = [s["code"] for s in data]
    assert "NDLS" in codes

def test_get_station_detail(client):
    response = client.get("/api/v1/stations/NDLS")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "NDLS"
    assert data["name"] == "New Delhi"
    assert data["latitude"] > 28.0
    assert data["longitude"] > 77.0

def test_station_live_board(client):
    response = client.get("/api/v1/stations/NDLS/live-board")
    assert response.status_code == 200
    data = response.json()
    assert "station" in data
    assert "arrivals" in data
    assert "departures" in data
