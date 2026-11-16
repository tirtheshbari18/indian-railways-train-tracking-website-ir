def test_register_and_login_flow(client):
    # Register new user
    reg_payload = {
        "username": "rajesh_kumar",
        "email": "rajesh.kumar@example.com",
        "password": "SecretPassword123"
    }
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert reg_data["username"] == "rajesh_kumar"
    assert reg_data["role"] == "passenger"

    # Login
    login_res = client.post(
        "/api/v1/auth/login/json",
        json={"username": "rajesh_kumar", "password": "SecretPassword123"}
    )
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

def test_admin_rbac_permission_denied(client, passenger_headers):
    # Attempting to access admin stats as passenger
    res = client.get("/api/v1/admin/stats", headers=passenger_headers)
    assert res.status_code == 403
    assert "Administrative privileges required" in res.json()["detail"]

def test_admin_rbac_permission_granted(client, admin_headers):
    # Admin access granted
    res = client.get("/api/v1/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "stations_count" in data
    assert "trains_count" in data
