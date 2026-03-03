from fastapi.testclient import TestClient
from app.core.config import INTERNAL_API_KEY
from app.domains.roles.service import RolesService

def test_guest_scopes(client: TestClient, db_session):
    user_id = 1001
    headers = {"X-API-Key": INTERNAL_API_KEY}
    
    # Init as guest
    client.post(f"/api/rbac/users/{user_id}/role/init", headers=headers)
    
    # Get permissions (guest always gets limited_access regardless of verified flag in IDP)
    resp = client.get(f"/api/rbac/users/{user_id}/permissions?is_verified=false", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "limited_access" in data["scopes"]
    assert "guest" in data["roles"]

def test_promotion_to_soldier_scopes(client: TestClient, db_session):
    user_id = 1002
    headers = {"X-API-Key": INTERNAL_API_KEY}
    
    # 1. Init as guest
    client.post(f"/api/rbac/users/{user_id}/role/init", headers=headers)
    
    # 2. Promote to soldier (Boss/Internal action)
    promote_payload = {"role": "soldier"}
    client.put(f"/api/rbac/users/{user_id}/role", json=promote_payload, headers=headers)
    
    # 3. Get permissions
    resp = client.get(f"/api/rbac/users/{user_id}/permissions", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "local_cabinet" in data["scopes"]
    assert "use_chat" in data["scopes"]
    assert "soldier" in data["roles"]
    assert "limited_access" not in data["scopes"]

def test_boss_scopes_regardless_of_sync(client: TestClient, db_session):
    user_id = 1003
    headers = {"X-API-Key": INTERNAL_API_KEY}
    
    # Manually set boss role
    srv = RolesService(db_session)
    srv.init_user_role(user_id)
    srv.change_user_role(user_id, "boss")
    
    # Check boss
    resp = client.get(f"/api/rbac/users/{user_id}/permissions", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["scopes"] == ["all"]
    assert "boss" in resp.json()["roles"]

def test_blocking_disabled_elevation(client: TestClient, db_session):
    user_id = 1004
    headers = {"X-API-Key": INTERNAL_API_KEY}
    srv = RolesService(db_session)
    
    # 1. Ensure blocking is disabled
    srv.set_setting("blockUnverifiedUsers", "false")
    
    # 2. Init as guest
    client.post(f"/api/rbac/users/{user_id}/role/init", headers=headers)
    
    # 3. Get permissions
    resp = client.get(f"/api/rbac/users/{user_id}/permissions", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    
    # 4. Verify elevation
    assert "soldier" in data["roles"]
    assert "guest" not in data["roles"]
    assert "local_cabinet" in data["scopes"]
    assert "limited_access" not in data["scopes"]
    
    # 5. Restore default blocking and verify it works again
    srv.set_setting("blockUnverifiedUsers", "true")
    resp = client.get(f"/api/rbac/users/{user_id}/permissions", headers=headers)
    data = resp.json()
    assert "guest" in data["roles"]
    assert "limited_access" in data["scopes"]
