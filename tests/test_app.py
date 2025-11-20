"""Tests for the Mergington High School FastAPI app."""
from fastapi.testclient import TestClient
from src.app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # spot check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    test_email = "testuser+pytest@example.com"

    # Get initial participants
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    initial_participants = list(activities[activity]["participants"]) if activity in activities else []

    # Ensure test email is not present
    assert test_email not in initial_participants

    # Sign up the test user
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    assert f"Signed up {test_email}" in resp.json().get("message", "")

    # Verify the participant now appears
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert test_email in activities[activity]["participants"]

    # Duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 400

    # Unregister the test user
    resp = client.delete(f"/activities/{activity}/unregister?email={test_email}")
    assert resp.status_code == 200
    assert f"Unregistered {test_email}" in resp.json().get("message", "")

    # Verify cleanup: email no longer present
    resp = client.get("/activities")
    assert resp.status_code == 200
    activities = resp.json()
    assert test_email not in activities[activity]["participants"]
import uuid
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic sanity check for a known activity
    assert "Chess Club" in data


def test_signup_and_unregister_flow():
    # Use a unique test email so tests are idempotent across runs
    test_email = f"test-{uuid.uuid4().hex}@example.com"
    activity_name = "Chess Club"

    # Ensure email not present; if it is, remove it first
    if test_email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(test_email)

    # Signup
    signup_resp = client.post(f"/activities/{activity_name}/signup?email={test_email}")
    assert signup_resp.status_code == 200
    signup_json = signup_resp.json()
    assert "Signed up" in signup_json.get("message", "")

    # Verify participant appears in activities
    get_resp = client.get("/activities")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert test_email in data[activity_name]["participants"]

    # Unregister
    unregister_resp = client.delete(f"/activities/{activity_name}/unregister?email={test_email}")
    assert unregister_resp.status_code == 200
    unregister_json = unregister_resp.json()
    assert "Unregistered" in unregister_json.get("message", "")

    # Verify participant removed
    get_resp2 = client.get("/activities")
    assert get_resp2.status_code == 200
    data2 = get_resp2.json()
    assert test_email not in data2[activity_name]["participants"]
