from tests.conftest import _create_order, _create_product


def test_list_allocations_empty(client):
    resp = client.get("/allocations/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_allocation(client):
    product = _create_product(client)
    order = _create_order(client)
    resp = client.post("/allocations/", json={
        "order_id": order["id"],
        "product_id": product["id"],
        "allocated_quantity": 25,
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["order_id"] == order["id"]
    assert body["product_id"] == product["id"]
    assert body["allocated_quantity"] == 25
    assert "id" in body


def test_get_allocation(client):
    product = _create_product(client)
    order = _create_order(client)
    alloc = client.post("/allocations/", json={
        "order_id": order["id"], "product_id": product["id"], "allocated_quantity": 10,
    }).json()
    resp = client.get(f"/allocations/{alloc['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == alloc["id"]


def test_get_allocation_not_found(client):
    assert client.get("/allocations/9999").status_code == 404


def test_list_allocations_filter_by_order(client):
    product = _create_product(client)
    order1 = _create_order(client, customer="A")
    order2 = _create_order(client, customer="B")
    client.post("/allocations/", json={"order_id": order1["id"], "product_id": product["id"], "allocated_quantity": 10})
    client.post("/allocations/", json={"order_id": order2["id"], "product_id": product["id"], "allocated_quantity": 5})

    resp = client.get(f"/allocations/?order_id={order1['id']}")
    assert resp.status_code == 200
    allocs = resp.json()
    assert len(allocs) == 1
    assert allocs[0]["order_id"] == order1["id"]


def test_delete_allocation(client):
    product = _create_product(client)
    order = _create_order(client)
    alloc = client.post("/allocations/", json={
        "order_id": order["id"], "product_id": product["id"], "allocated_quantity": 10,
    }).json()
    assert client.delete(f"/allocations/{alloc['id']}").status_code == 204
    assert client.get(f"/allocations/{alloc['id']}").status_code == 404


def test_delete_allocation_not_found(client):
    assert client.delete("/allocations/9999").status_code == 404
