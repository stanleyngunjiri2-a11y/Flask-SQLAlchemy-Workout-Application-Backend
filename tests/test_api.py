# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "Workout Application API",
        "status": "running",
    }


# ---------------------------------------------------------
# EXERCISE ENDPOINTS
# ---------------------------------------------------------

def test_list_exercises_returns_empty_list(client):
    response = client.get("/exercises")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_exercise(client, exercise_data):
    response = client.post("/exercises", json=exercise_data)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["name"] == "Push-ups"
    assert data["category"] == "Strength"
    assert data["equipment_needed"] is False


def test_get_exercise(client, create_exercise):
    exercise = create_exercise()

    response = client.get(f"/exercises/{exercise['id']}")

    assert response.status_code == 200
    assert response.get_json()["name"] == "Push-ups"


def test_missing_exercise_returns_404(client):
    response = client.get("/exercises/99999")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_delete_exercise(client, create_exercise):
    exercise = create_exercise()

    response = client.delete(f"/exercises/{exercise['id']}")

    assert response.status_code == 204
    assert response.data == b""

    response = client.get(f"/exercises/{exercise['id']}")

    assert response.status_code == 404


def test_delete_missing_exercise_returns_404(client):
    response = client.delete("/exercises/99999")

    assert response.status_code == 404


def test_blank_exercise_name_is_rejected(client, exercise_data):
    payload = {**exercise_data, "name": "   "}

    response = client.post("/exercises", json=payload)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_blank_exercise_category_is_rejected(client, exercise_data):
    payload = {**exercise_data, "category": "   "}

    response = client.post("/exercises", json=payload)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_missing_required_exercise_field_is_rejected(client):
    response = client.post("/exercises", json={
        "name": "Push-ups",
        "category": "Strength",
    })

    assert response.status_code == 400


def test_exercise_name_too_long_is_rejected(client, exercise_data):
    payload = {**exercise_data, "name": "x" * 121}

    response = client.post("/exercises", json=payload)

    assert response.status_code == 400


# ---------------------------------------------------------
# WORKOUT ENDPOINTS
# ---------------------------------------------------------

def test_list_workouts_returns_empty_list(client):
    response = client.get("/workouts")

    assert response.status_code == 200
    assert response.get_json() == []


def test_create_workout(client, workout_data):
    response = client.post("/workouts", json=workout_data)

    assert response.status_code == 201

    data = response.get_json()

    assert data["id"] is not None
    assert data["duration_minutes"] == 45
    assert data["notes"] == "Upper body workout"
    assert data["exercises"] == []


def test_get_workout(client, create_workout):
    workout = create_workout()

    response = client.get(f"/workouts/{workout['id']}")

    assert response.status_code == 200
    assert response.get_json()["duration_minutes"] == 45


def test_missing_workout_returns_404(client):
    response = client.get("/workouts/99999")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_delete_workout(client, create_workout):
    workout = create_workout()

    response = client.delete(f"/workouts/{workout['id']}")

    assert response.status_code == 204
    assert response.data == b""

    response = client.get(f"/workouts/{workout['id']}")

    assert response.status_code == 404


def test_delete_missing_workout_returns_404(client):
    response = client.delete("/workouts/99999")

    assert response.status_code == 404


def test_zero_workout_duration_is_rejected(client, workout_data):
    payload = {**workout_data, "duration_minutes": 0}

    response = client.post("/workouts", json=payload)

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_negative_workout_duration_is_rejected(client, workout_data):
    payload = {**workout_data, "duration_minutes": -10}

    response = client.post("/workouts", json=payload)

    assert response.status_code == 400


def test_workout_duration_over_24_hours_is_rejected(
    client,
    workout_data,
):
    payload = {**workout_data, "duration_minutes": 1441}

    response = client.post("/workouts", json=payload)

    assert response.status_code == 400


def test_missing_required_workout_field_is_rejected(client):
    response = client.post("/workouts", json={
        "duration_minutes": 45,
    })

    assert response.status_code == 400


# ---------------------------------------------------------
# WORKOUT-EXERCISE ASSOCIATION
# ---------------------------------------------------------

def test_add_exercise_to_workout(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 12, "sets": 3},
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["workout_id"] == workout["id"]
    assert data["exercise_id"] == exercise["id"]
    assert data["reps"] == 12
    assert data["sets"] == 3


def test_add_timed_exercise_to_workout(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"duration_seconds": 60},
    )

    assert response.status_code == 201
    assert response.get_json()["duration_seconds"] == 60


def test_workout_response_contains_associated_exercises(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 12, "sets": 3},
    )

    assert response.status_code == 201

    response = client.get(f"/workouts/{workout['id']}")

    assert response.status_code == 200

    data = response.get_json()

    assert len(data["exercises"]) == 1
    assert data["exercises"][0]["id"] == exercise["id"]
    assert data["exercises"][0]["name"] == "Push-ups"


def test_association_without_reps_or_duration_is_rejected(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"sets": 3},
    )

    assert response.status_code == 400
    assert "errors" in response.get_json()


def test_association_with_zero_reps_is_rejected(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 0},
    )

    assert response.status_code == 400


def test_association_with_zero_sets_is_rejected(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 12, "sets": 0},
    )

    assert response.status_code == 400


def test_association_with_zero_duration_is_rejected(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"duration_seconds": 0},
    )

    assert response.status_code == 400


def test_duplicate_association_is_rejected(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    endpoint = (
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises"
    )

    first_response = client.post(
        endpoint,
        json={"reps": 12, "sets": 3},
    )

    assert first_response.status_code == 201

    second_response = client.post(
        endpoint,
        json={"reps": 15, "sets": 2},
    )

    assert second_response.status_code == 400


def test_missing_workout_when_associating_returns_404(
    client,
    create_exercise,
):
    exercise = create_exercise()

    response = client.post(
        f"/workouts/99999/exercises/"
        f"{exercise['id']}/workout_exercises",
        json={"reps": 12},
    )

    assert response.status_code == 404


def test_missing_exercise_when_associating_returns_404(
    client,
    create_workout,
):
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        "99999/workout_exercises",
        json={"reps": 12},
    )

    assert response.status_code == 404


# ---------------------------------------------------------
# REQUEST BODY VALIDATION
# ---------------------------------------------------------

def test_exercise_rejects_non_object_json(client):
    response = client.post("/exercises", json=["not", "an", "object"])

    assert response.status_code == 400


def test_workout_rejects_non_object_json(client):
    response = client.post("/workouts", json=["not", "an", "object"])

    assert response.status_code == 400


def test_association_rejects_non_object_json(
    client,
    create_exercise,
    create_workout,
):
    exercise = create_exercise()
    workout = create_workout()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/"
        f"{exercise['id']}/workout_exercises",
        json=["not", "an", "object"],
    )

    assert response.status_code == 400
