import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


def _create_product(client, **overrides):
    data = {"name": "Widget", "sku": "WDG-001", "available_quantity": 100}
    data.update(overrides)
    resp = client.post("/products/", json=data)
    assert resp.status_code == 201
    return resp.json()


def _create_order(client, **overrides):
    data = {"customer": "Acme Corp"}
    data.update(overrides)
    resp = client.post("/orders/", json=data)
    assert resp.status_code == 201
    return resp.json()
