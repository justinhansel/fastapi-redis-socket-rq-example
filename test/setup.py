from fastapi.testclient import TestClient
from app.database import Base, engine

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

user_create = {
    "email": "test2@test2.com",
    "username": "test_user",
    "password": "password"
}


def create_test_user(client: TestClient):
    response = client.post("/user", json=user_create)
    assert response.status_code == 200
