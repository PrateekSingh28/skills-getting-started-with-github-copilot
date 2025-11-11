import pytest
from fastapi.testclient import TestClient

# Import your FastAPI app instance from app.py (root of project)
from app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    response = client.get("/", allow_redirects=False)
    assert response.status_code in (301, 302, 303, 307, 308)
    assert response.headers.get("location") == "/static/index.html"


def test_get_activities_structure_and_examples():
    response = client.get("/activities")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)

    # Base activities from your app.py
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data

    # Structure sanity
    chess = data["Chess Club"]
    for key in ("description", "schedule", "max_participants", "participants"):
        assert key in chess
    assert isinstance(chess["participants"], list)


def test_signup_success_then_duplicate():
    activity_name = "Gym Class"
    new_email = "newstudent@mergington.edu"

    # First signup succeeds
    r1 = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    assert r1.status_code == 200
    assert "message" in r1.json()

    # Verify participant appears
    participants = client.get("/activities").json()[activity_name]["participants"]
    assert new_email in participants

    # Second signup fails (duplicate)
    r2 = client.post(f"/activities/{activity_name}/signup", params={"email": new_email})
    assert r2.status_code == 400
    assert r2.json().get("detail") == "Student already signed up for this activity"


def test_signup_nonexistent_activity():
    r = client.post("/activities/UnknownClub/signup", params={"email": "someone@mergington.edu"})
    assert r.status_code == 404
    assert r.json().get("detail") == "Activity not found"