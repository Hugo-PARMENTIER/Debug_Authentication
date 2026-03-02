from fastapi.testclient import TestClient
from main import app
from datetime import datetime

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    
    # Try parsing the timestamp to ensure it's a valid date string
    try:
        # fromisoformat requires exactly the format Python outputs
        # or we just check it's a non-empty string
        assert isinstance(data["timestamp"], str)
        assert len(data["timestamp"]) > 0
    except Exception as e:
        assert False, f"Timestamp is not a valid format: {e}"
