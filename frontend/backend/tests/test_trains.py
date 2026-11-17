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

def test_tejas_12951_vadodara_schedule(client):
    response = client.get("/api/v1/trains/12951")
    assert response.status_code == 200
    data = response.json()
    brc_stops = [s for s in data["stops"] if s["station_code"] == "BRC"]
    assert len(brc_stops) == 1
    assert brc_stops[0]["arrival_time"] == "21:14"
    assert brc_stops[0]["departure_time"] == "21:27"
    assert brc_stops[0]["halt_minutes"] == 13

def test_search_by_category_memu(client):
    response = client.get("/api/v1/trains?category=MEMU")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    train_nums = [t["train_number"] for t in data["items"]]
    assert "09159" in train_nums

def test_search_by_station_name_resolution(client):
    # Searching human station name "Boisar" to "Dahanu Road"
    response = client.get("/api/v1/trains?source=Boisar&destination=Dahanu Road")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    train_nums = [t["train_number"] for t in data["items"]]
    # Should include 93005 (Churchgate - Dahanu Road Local) or 09159
    assert any(n in ["93005", "09159", "22953", "19015"] for n in train_nums)

def test_train_12953_august_kranti_details_and_stops(client):
    response = client.get("/api/v1/trains/12953")
    assert response.status_code == 200
    data = response.json()
    assert data["train_number"] == "12953"
    assert "August Kranti" in data["train_name"]
    assert data["short_name"] == "AK Tejas Raj Ex"
    assert data["train_category"] == "Rajdhani Express"
    assert data["source_station_code"] == "MMCT"
    assert data["destination_station_code"] == "NZM"
    assert len(data["stops"]) == 12

    # Verify stops sequence, stations, and distance_from_prev
    expected_stops = ["MMCT", "BVI", "VAPI", "BL", "ST", "BH", "BRC", "RTM", "KOTA", "SWM", "MTJ", "NZM"]
    stop_codes = [s["station_code"] for s in data["stops"]]
    assert stop_codes == expected_stops

    seqs = [s["stop_sequence"] for s in data["stops"]]
    assert seqs == list(range(1, 13))

    # Verify distance_from_prev calculation
    first_stop = data["stops"][0]
    assert first_stop["distance_km"] == 0.0
    assert first_stop["distance_from_prev"] == 0.0

    second_stop = data["stops"][1]
    assert second_stop["station_code"] == "BVI"
    assert second_stop["distance_km"] == 30.0
    assert second_stop["distance_from_prev"] == 30.0

    last_stop = data["stops"][-1]
    assert last_stop["station_code"] == "NZM"
    assert last_stop["distance_km"] == 1377.0
    assert last_stop["distance_from_prev"] == 134.0

def test_train_12953_aliases_search(client):
    queries = [
        "12953",
        "AK Tejas Raj Ex",
        "AK Tejas Raj",
        "August Kranti",
        "August Kranti Tejas Rajdhani",
        "August Kranti Rajdhani",
        "Mumbai Central Nizamuddin Rajdhani",
        "MMCT NZM",
        "MMCT to NZM"
    ]
    for q in queries:
        resp = client.get(f"/api/v1/trains?query={q}")
        assert resp.status_code == 200, f"Query failed: {q}"
        data = resp.json()
        assert data["total"] >= 1, f"No results for query '{q}'"
        train_nums = [t["train_number"] for t in data["items"]]
        assert "12953" in train_nums, f"Train 12953 not found in results for query '{q}'"

def test_category_rajdhani_search(client):
    resp = client.get("/api/v1/trains?category=Rajdhani")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    train_nums = [t["train_number"] for t in data["items"]]
    assert "12953" in train_nums
    assert "12951" in train_nums

def test_intermediate_station_search_boisar(client):
    resp = client.get("/api/v1/trains?query=Boisar")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    # Train 09159 (Bandra - Vapi MEMU) or 93005 calls at Boisar
    train_nums = [t["train_number"] for t in data["items"]]
    assert any(n in ["09159", "09160", "93005", "93006", "93025", "93026"] for n in train_nums)




