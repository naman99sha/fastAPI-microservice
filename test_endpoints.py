from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_getHome():
    response = client.get("/")
    assert response.status_code == 200
    assert 'text/html' in response.headers["content-type"]
