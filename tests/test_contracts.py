import pytest
from app.core.config import INTERNAL_API_KEY

def test_healthz(client):
    response = client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_init_user_role(client):
    user_id = 101
    headers = {"X-API-Key": INTERNAL_API_KEY}
    response = client.post(f"/api/rbac/users/{user_id}/role/init", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "guest" in data["roles"]

def test_get_user_roles(client):
    user_id = 102
    headers = {"X-API-Key": INTERNAL_API_KEY}
    # Init first
    client.post(f"/api/rbac/users/{user_id}/role/init", headers=headers)
    
    response = client.get(f"/api/rbac/users/{user_id}/roles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == user_id
    assert "guest" in data["roles"]

def test_change_user_role_boss(boss_client):
    user_id = 103
    # Init first (no auth needed for init)
    boss_client.post(f"/api/rbac/users/{user_id}/role/init")
    
    payload = {"role": "sotto_capo"}
    response = boss_client.put(f"/api/rbac/users/{user_id}/role", json=payload)
    assert response.status_code == 200
    assert "sotto_capo" in response.json()["roles"]

def test_change_user_role_forbidden(client):
    user_id = 104
    payload = {"role": "boss"}
    # No auth header -> 401 (or 403 if it defaults to something)
    response = client.put(f"/api/rbac/users/{user_id}/role", json=payload)
    assert response.status_code in [401, 403]

def test_get_boss_id_internal(client, db_session):
    # Init a boss user
    from app.domains.roles.service import RolesService
    srv = RolesService(db_session)
    # create_default_roles already exists from setup_db
    # We just need to assign boss role to someone
    user_id = 999
    srv.init_user_role(user_id)
    srv.change_user_role(user_id, "boss")
    
    headers = {"X-API-Key": INTERNAL_API_KEY}
    response = client.get("/api/rbac/internal/boss", headers=headers)
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id
