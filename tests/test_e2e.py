import pytest
from fastapi.testclient import TestClient
from app.main import app

# Fixtures for setting up the test environment
@pytest.fixture(scope="module")
def test_client():
    with TestClient(app) as client:
        yield client

# E2E Test cases
def test_e2e_notification_flow(test_client):
    # Step 1: Get Token
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Clear All Notifications
    response = test_client.delete("/notifications/", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "All notifications cleared successfully"}

    # Step 3: Send Notification
    payload = {
        "notification_type": "news",
        "recipient": "user1@example.com",
        "message": "News update 1"
    }
    response = test_client.post("/send-notification/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Notification sent to user1@example.com"}

    # Step 4: Send Rate Limited Notification
    payload = {
        "notification_type": "news",
        "recipient": "user1@example.com",
        "message": "Rate limited notification"
    }
    response = test_client.post("/send-notification/", json=payload, headers=headers)
    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded for news to user1@example.com"}


def test_e2e_update_rate_limits(test_client):
    # Step 1: Get Token
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Clear All Notifications
    response = test_client.delete("/notifications", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "All notifications cleared successfully"}


    # Step 3: Update Rate Limits
    payload = {
        "status_count": 5,
        "status_period": 120,
        "news_count": 2,
        "news_period": 86400,
        "marketing_count": 5,
        "marketing_period": 7200
    }
    response = test_client.put("/rate-limits/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Rate limits updated successfully"}

    # Step 4: Send Notification with New Rate Limits
    payload = {
        "notification_type": "status",
        "recipient": "user2@example.com",
        "message": "Status update 2"
    }
    response = test_client.post("/send-notification/", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Notification sent to user2@example.com"}

def test_e2e_clear_rate_limits(test_client):
    # Step 1: Get Token
    response = test_client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Step 2: Clear Rate Limits
    response = test_client.delete("/notifications", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "All notifications cleared successfully"}
