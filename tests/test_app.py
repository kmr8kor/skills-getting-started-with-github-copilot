"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to original state before each test."""
    original = {name: {**data, "participants": list(data["participants"])}
                for name, data in activities.items()}
    yield
    activities.clear()
    activities.update(original)


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_for_activity():
    response = client.post("/activities/Chess Club/signup?email=test@mergington.edu")
    assert response.status_code == 200
    assert "test@mergington.edu" in response.json()["message"]


def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404


def test_signup_duplicate_prevention():
    """Students should not be able to sign up twice for the same activity."""
    email = "duplicate@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_from_activity():
    email = "michael@mergington.edu"
    response = client.delete(f"/activities/Chess Club/signup?email={email}")
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_activity_not_found():
    response = client.delete("/activities/Nonexistent/signup?email=test@mergington.edu")
    assert response.status_code == 404


def test_unregister_not_signed_up():
    response = client.delete("/activities/Chess Club/signup?email=notregistered@mergington.edu")
    assert response.status_code == 400


def test_activities_have_descriptions():
    response = client.get("/activities")
    data = response.json()
    assert len(data) >= 4
    for name, details in data.items():
        assert "description" in details
