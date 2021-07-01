import os
import sys

from fastapi.testclient import TestClient

from app.api import api
from test.setup import create_test_user, user_create

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir + '/../../')

client = TestClient(api)


class TestLogin:
    def test_login(self):
        create_test_user(client)
        response = client.post("/login", json=user_create)
        assert 'access_token' in response.json()

