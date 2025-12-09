# tests/test_user_roles.py
from fastapi.testclient import TestClient


def test_add_and_get_roles(client: TestClient):
    user_id = "test-user-1"

    # добавляем роль
    resp = client.post(
        f"/api/rbac/users/{user_id}/roles",
        json={"role_name": "admin"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["user_id"] == user_id
    assert "admin" in data["roles"]

    # получаем роли
    resp2 = client.get(f"/api/rbac/users/{user_id}/roles")
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["user_id"] == user_id
    assert "admin" in data2["roles"]
