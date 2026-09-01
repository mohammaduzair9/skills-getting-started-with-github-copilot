import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_unregister_participant_removes_email_from_activity():
    response = client.delete("/activities/Chess%20Club/participants/michael%40mergington.edu")

    assert response.status_code == 200
    assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

    activities_response = client.get("/activities").json()
    assert "michael@mergington.edu" not in activities_response["Chess Club"]["participants"]


def test_unregister_missing_participant_returns_404():
    response = client.delete("/activities/Chess%20Club/participants/ghost%40mergington.edu")

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
