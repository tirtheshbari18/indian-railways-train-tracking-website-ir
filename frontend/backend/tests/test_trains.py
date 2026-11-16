def test_get_trains_list(client):
    response = client.get("/api/v1/trains")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert len(data["items"]) >= 1

def test_search_train_by_number(client):
    response = client.get("/api/v1/trains?query=12951")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["train_number"] == "12951"
    assert "Rajdhani" in data["items"][0]["train_name"]

def test_search_train_by_route(client):
    response = client.get("/api/v1/trains?source=MMCT&destination=NDLS")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    train_nums = [t["train_number"] for t in data["items"]]
    assert "12951" in train_nums

def test_get_train_detail_with_stops(client):
    response = client.get("/api/v1/trains/12951")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "12951"
    assert len(data["stops"]) >= 5
    # Verify sequence order
    seqs = [s["stop_sequence"] for s in data["stops"]]
    assert seqs == sorted(seqs)

def test_get_nonexistent_train(client):
    response = client.get("/api/v1/trains/99999")
    assert response.status_code == 404

def test_vande_bharat_22961_route_and_stops(client):
    response = client.get("/api/v1/trains/22961")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "22961"
    assert "Vande Bharat" in data["train_name"]
    assert data["source_station_code"] == "MMCT"
    assert data["destination_station_code"] == "ADI"
    assert len(data["stops"]) == 6
    stop_codes = [s["station_code"] for s in data["stops"]]
    assert stop_codes == ["MMCT", "BVI", "VAPI", "ST", "BRC", "ADI"]

def test_gujarat_sf_express_22954_route_and_stops(client):
    response = client.get("/api/v1/trains/22954")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "22954"
    assert "Gujarat" in data["train_name"]
    assert data["source_station_code"] == "ADI"
    assert data["destination_station_code"] == "MMCT"
    assert len(data["stops"]) == 26
    # Source is ADI, destination is MMCT
    assert data["stops"][0]["station_code"] == "ADI"
    assert data["stops"][-1]["station_code"] == "MMCT"

