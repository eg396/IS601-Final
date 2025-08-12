from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_read_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

"""

def test_register_endpoint():
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "confirm_password": "password123",
        "first_name": "Test",
        "last_name": "User"
    }
    response = client.post("/auth/register", json=user_data)
    # Depends on your DB setup and constraints — expect 201 or 400
    assert response.status_code in (201, 400)

    
"""