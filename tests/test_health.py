from fastapi.testclient import TestClient
from main import app
from datetime import datetime
import os
from unittest.mock import patch

client = TestClient(app)

def test_health_no_gemini_key():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["gemini_quotas"]["status"] == "Not available via API"

@patch('google.generativeai.GenerativeModel.count_tokens_async')
def test_health_with_gemini_key(mock_count_tokens):
    # Set the environment variable for the test
    os.environ["GEMINI_API_KEY"] = "test_key"
    
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["gemini_quotas"]["status"] == "Accessible"
    
    # Clean up the environment variable
    del os.environ["GEMINI_API_KEY"]
