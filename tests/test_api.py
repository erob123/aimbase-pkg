from fastapi.testclient import TestClient
from .example_app import auto_app

client = TestClient(auto_app)

# Verify app versioning set to /v1
def test_v1_exists():
    response = client.get(
        "/v1/docs"
    )
    assert response.status_code == 200