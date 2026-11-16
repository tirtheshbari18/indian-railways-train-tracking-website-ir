import io

def test_import_stations_validation_success(client, admin_headers):
    csv_content = (
        "code,name,division,zone,state,latitude,longitude,platforms_count\n"
        "TPJ,Tiruchchirappalli,Tiruchchirappalli,SR,Tamil Nadu,10.7937,78.6856,8\n"
    )
    files = {"file": ("test_stations.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post(
        "/api/v1/admin/import/validate",
        data={"entity_type": "stations"},
        files=files,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert data["valid_rows_count"] == 1
    assert data["error_rows_count"] == 0

def test_import_stations_validation_invalid_data(client, admin_headers):
    # Invalid latitude 999.0
    csv_content = (
        "code,name,division,zone,state,latitude,longitude,platforms_count\n"
        "BAD,Bad Station,Test,NR,Delhi,999.0,77.0,2\n"
    )
    files = {"file": ("bad_stations.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post(
        "/api/v1/admin/import/validate",
        data={"entity_type": "stations"},
        files=files,
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert data["error_rows_count"] >= 1
    assert any("latitude" in e["field"] for e in data["errors"])

def test_import_execution_creates_audit_log(client, admin_headers):
    csv_content = (
        "code,name,division,zone,state,latitude,longitude,platforms_count\n"
        "JAT,Jammu Tawi,Firozpur,NR,Jammu and Kashmir,32.7060,74.8800,4\n"
    )
    files = {"file": ("jammu.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    res = client.post(
        "/api/v1/admin/import/execute",
        data={"entity_type": "stations"},
        files=files,
        headers=admin_headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True

    # Check audit log
    audit_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) >= 1
    assert any("IMPORT_STATIONS" in log["action"] for log in logs)
