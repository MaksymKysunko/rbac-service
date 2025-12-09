# tests/test_user_roles.py
from fastapi.testclient import TestClient

def test_init_and_get_roles(client: TestClient):
    # тепер user_id у нас int, а не довільний string
    user_id = 123

    # 1. Ініціалізуємо роль користувача (має стати 'soldier')
    resp_init = client.post(f"/api/rbac/users/{user_id}/role/init")
    assert resp_init.status_code == 200

    data_init = resp_init.json()
    assert data_init["user_id"] == user_id
    assert data_init["roles"] == ["soldier"]

    # 2. Перевіряємо через GET, що роль зчитується коректно
    resp_get = client.get(f"/api/rbac/users/{user_id}/roles")
    assert resp_get.status_code == 200

    data_get = resp_get.json()
    assert data_get["user_id"] == user_id
    assert data_get["roles"] == ["soldier"]