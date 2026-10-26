import sys
from pathlib import Path

import pytest

# Add the server directory so app.py, models.py and schemas.py
# can be imported when pytest runs from the project root.
SERVER_DIR = Path(__file__).resolve().parents[1] / "server"

if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app import create_app
from models import db


@pytest.fixture
def app():
    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def exercise_data():
    return {
        "name": "Push-ups",
        "category": "Strength",
        "equipment_needed": False,
    }


@pytest.fixture
def workout_data():
    return {
        "date": "2026-10-26",
        "duration_minutes": 45,
        "notes": "Upper body workout",
    }


@pytest.fixture
def create_exercise(client, exercise_data):
    def _create_exercise(**overrides):
        payload = {**exercise_data, **overrides}
        response = client.post("/exercises", json=payload)

        assert response.status_code == 201, response.get_json()

        return response.get_json()

    return _create_exercise


@pytest.fixture
def create_workout(client, workout_data):
    def _create_workout(**overrides):
        payload = {**workout_data, **overrides}
        response = client.post("/workouts", json=payload)

        assert response.status_code == 201, response.get_json()

        return response.get_json()

    return _create_workout
