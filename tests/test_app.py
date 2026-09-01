import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


def setup_function():
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_root_redirects_to_static_index():
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = set(ORIGINAL_ACTIVITIES.keys())

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert set(payload.keys()) == expected_activity_names

    for activity_name, expected_activity in ORIGINAL_ACTIVITIES.items():
        assert payload[activity_name]["description"] == expected_activity["description"]
        assert payload[activity_name]["schedule"] == expected_activity["schedule"]
        assert payload[activity_name]["max_participants"] == expected_activity["max_participants"]
        assert payload[activity_name]["participants"] == expected_activity["participants"]


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_for_missing_activity_returns_404():
    # Arrange
    activity_name = "Missing Club"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_email_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_email_from_activity():
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email.replace('@', '%40')}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"

    activities_response = client.get("/activities").json()
    assert email not in activities_response[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    email = "ghost@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email.replace('@', '%40')}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
