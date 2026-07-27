from starlette import status

from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (
        status.HTTP_307_TEMPORARY_REDIRECT,
        status.HTTP_308_PERMANENT_REDIRECT,
    )
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities_returns_activity_list(client):
    # Arrange
    expected_activity = "Chess Club"

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, dict)
    assert expected_activity in data
    assert "description" in data[expected_activity]
    assert "participants" in data[expected_activity]


def test_signup_for_activity_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "test.student@mergington.edu"
    assert new_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": new_email},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_participant_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_unregisters_existing_participant(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = activities[activity_name]["participants"][0]
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Removed {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_nonexistent_participant_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing.student@mergington.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Participant not found"
