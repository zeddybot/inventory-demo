from tests.conftest import _create_order


def test_list_orders_empty(client):
    resp = client.get("/orders/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_order(client):
    resp = client.post("/orders/", json={"customer": "Acme Corp"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["customer"] == "Acme Corp"
    assert body["priority"] == 3
    assert body["status"] == "pending"
    assert "created_at" in body
    assert "id" in body


def test_create_order_with_priority(client):
    resp = client.post("/orders/", json={"customer": "Urgent Co", "priority": 1, "status": "confirmed"})
    assert resp.status_code == 201
    body = resp.json()
    assert body["priority"] == 1
    assert body["status"] == "confirmed"


def test_list_orders(client):
    _create_order(client, customer="A")
    _create_order(client, customer="B")
    resp = client.get("/orders/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_order(client):
    order = _create_order(client)
    resp = client.get(f"/orders/{order['id']}")
    assert resp.status_code == 200
    assert resp.json()["customer"] == order["customer"]


def test_get_order_not_found(client):
    assert client.get("/orders/9999").status_code == 404


def test_update_order(client):
    order = _create_order(client)
    resp = client.patch(f"/orders/{order['id']}", json={"status": "shipped", "priority": 1})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "shipped"
    assert body["priority"] == 1


def test_update_order_partial(client):
    order = _create_order(client)
    resp = client.patch(f"/orders/{order['id']}", json={"status": "confirmed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
    assert resp.json()["priority"] == order["priority"]


def test_update_order_not_found(client):
    assert client.patch("/orders/9999", json={"status": "shipped"}).status_code == 404


def test_delete_order(client):
    order = _create_order(client)
    assert client.delete(f"/orders/{order['id']}").status_code == 204
    assert client.get(f"/orders/{order['id']}").status_code == 404


def test_delete_order_not_found(client):
    assert client.delete("/orders/9999").status_code == 404
