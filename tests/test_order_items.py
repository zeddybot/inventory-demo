from tests.conftest import _create_order, _create_product


def test_list_order_items_empty(client):
    resp = client.get("/order-items/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_order_item(client):
    product = _create_product(client)
    order = _create_order(client)
    resp = client.post("/order-items/", json={
        "order_id": order["id"],
        "product_id": product["id"],
        "requested_quantity": 10,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["order_id"] == order["id"]
    assert body["product_id"] == product["id"]
    assert body["requested_quantity"] == 10
    assert "id" in body


def test_get_order_item(client):
    product = _create_product(client)
    order = _create_order(client)
    item = client.post("/order-items/", json={
        "order_id": order["id"], "product_id": product["id"], "requested_quantity": 5,
    }).json()
    resp = client.get(f"/order-items/{item['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item["id"]


def test_get_order_item_not_found(client):
    assert client.get("/order-items/9999").status_code == 404


def test_list_order_items_filter_by_order(client):
    product = _create_product(client)
    order1 = _create_order(client, customer="A")
    order2 = _create_order(client, customer="B")
    client.post("/order-items/", json={"order_id": order1["id"], "product_id": product["id"], "requested_quantity": 5})
    client.post("/order-items/", json={"order_id": order2["id"], "product_id": product["id"], "requested_quantity": 3})

    resp = client.get(f"/order-items/?order_id={order1['id']}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["order_id"] == order1["id"]


def test_delete_order_item(client):
    product = _create_product(client)
    order = _create_order(client)
    item = client.post("/order-items/", json={
        "order_id": order["id"], "product_id": product["id"], "requested_quantity": 5,
    }).json()
    assert client.delete(f"/order-items/{item['id']}").status_code == 204
    assert client.get(f"/order-items/{item['id']}").status_code == 404


def test_delete_order_item_not_found(client):
    assert client.delete("/order-items/9999").status_code == 404
