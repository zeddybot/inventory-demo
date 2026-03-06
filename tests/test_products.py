from tests.conftest import _create_product


def test_list_products_empty(client):
    resp = client.get("/products/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_product(client):
    resp = client.post("/products/", json={"name": "Motor", "sku": "MTR-001", "available_quantity": 50})
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Motor"
    assert body["sku"] == "MTR-001"
    assert body["available_quantity"] == 50
    assert "id" in body


def test_create_product_default_quantity(client):
    resp = client.post("/products/", json={"name": "Sensor", "sku": "SNS-001"})
    assert resp.status_code == 201
    assert resp.json()["available_quantity"] == 0


def test_list_products(client):
    _create_product(client, sku="A-001")
    _create_product(client, sku="A-002")
    resp = client.get("/products/")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_get_product(client):
    product = _create_product(client)
    resp = client.get(f"/products/{product['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == product["id"]


def test_get_product_not_found(client):
    assert client.get("/products/9999").status_code == 404


def test_update_product(client):
    product = _create_product(client)
    resp = client.patch(f"/products/{product['id']}", json={"name": "Updated", "available_quantity": 999})
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Updated"
    assert body["available_quantity"] == 999
    assert body["sku"] == product["sku"]


def test_update_product_partial(client):
    product = _create_product(client)
    resp = client.patch(f"/products/{product['id']}", json={"name": "Renamed"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"
    assert resp.json()["available_quantity"] == product["available_quantity"]


def test_update_product_not_found(client):
    assert client.patch("/products/9999", json={"name": "X"}).status_code == 404


def test_delete_product(client):
    product = _create_product(client)
    assert client.delete(f"/products/{product['id']}").status_code == 204
    assert client.get(f"/products/{product['id']}").status_code == 404


def test_delete_product_not_found(client):
    assert client.delete("/products/9999").status_code == 404
