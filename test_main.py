import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from domain.exceptions import RateLimitExceededException
from app.main import app
from app.dependencies import get_notification_service_app

# Fixtures for setting up the test environment
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

class MockNotificationServiceApp:
    def send_notification(self, notification_type, recipient, message):
        if notification_type == "rate_limited":
            raise RateLimitExceededException("Rate limit exceeded")
        return
    
    def clear_all_notifications(self):
        return


# Mock dependency injection
def override_get_notification_service_app():
    return MockNotificationServiceApp()

app.dependency_overrides[get_notification_service_app] = override_get_notification_service_app

# Test cases
def test_get_token(test_client):
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_send_notification(test_client):
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "notification_type": "status",
        "recipient": "user1@example.com",
        "message": "Status update 1"
    }
    response = test_client.post("/send-notification/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Notification sent to user1@example.com"}

def test_rate_limited_notification(test_client):
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "notification_type": "rate_limited",
        "recipient": "user1@example.com",
        "message": "Rate limited notification"
    }
    response = test_client.post("/send-notification/", json=payload, headers=headers)
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded"}

def test_clear_all_notifications(test_client):
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.delete("/notifications/clear", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "All notifications cleared successfully"}