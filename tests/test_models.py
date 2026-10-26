from datetime import date, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise



# Model validation tests


def test_exercise_name_is_trimmed(app):
    with app.app_context():
        exercise = Exercise(
            name="  Push-ups  ",
            category="Strength",
            equipment_needed=False,
        )

        assert exercise.name == "Push-ups"


@pytest.mark.parametrize(
    "name",
    ["", " ", "   "],
)
def test_exercise_rejects_blank_name(app, name):
    with app.app_context():
        with pytest.raises(ValueError):
            Exercise(
                name=name,
                category="Strength",
                equipment_needed=False,
            )


def test_exercise_rejects_blank_category(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Exercise(
                name="Push-ups",
                category=" ",
                equipment_needed=False,
            )


def test_exercise_rejects_non_boolean_equipment_flag(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Exercise(
                name="Push-ups",
                category="Strength",
                equipment_needed="no",
            )


@pytest.mark.parametrize(
    "duration",
    [0, -1, 1441, 1.5, True],
)
def test_workout_rejects_invalid_duration(app, duration):
    with app.app_context():
        with pytest.raises(ValueError):
            Workout(
                date=date(2026, 10, 26),
                duration_minutes=duration,
            )


def test_workout_rejects_datetime_as_date(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Workout(
                date=datetime(2026, 10, 26, 12, 0),
                duration_minutes=45,
            )


def test_association_rejects_non_positive_repetitions(app):
    with app.app_context():
        with pytest.raises(ValueError):
            WorkoutExercise(reps=0)


def test_association_rejects_non_positive_sets(app):
    with app.app_context():
        with pytest.raises(ValueError):
            WorkoutExercise(sets=-1)


def test_association_rejects_non_positive_duration(app):
    with app.app_context():
        with pytest.raises(ValueError):
            WorkoutExercise(duration_seconds=0)


# ---------------------------------------------------------
# DATABASE CONSTRAINTS
# ---------------------------------------------------------

def test_database_rejects_blank_exercise_name(app):
    with app.app_context():
        # Execute direct SQL to bypass SQLAlchemy attribute validators.
        with pytest.raises(IntegrityError):
            db.session.execute(
                text(
                    """
                    INSERT INTO exercises
                        (name, category, equipment_needed)
                    VALUES ('   ', 'Strength', 0)
                    """
                )
            )
            db.session.commit()

        db.session.rollback()


def test_database_rejects_non_positive_workout_duration(app):
    with app.app_context():
        with pytest.raises(IntegrityError):
            db.session.execute(
                text(
                    """
                    INSERT INTO workouts
                        (date, duration_minutes, notes)
                    VALUES ('2026-10-26', 0, NULL)
                    """
                )
            )
            db.session.commit()

        db.session.rollback()


def test_database_rejects_association_without_reps_or_duration(app):
    with app.app_context():
        exercise = Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False,
        )

        workout = Workout(
            date=date(2026, 10, 26),
            duration_minutes=45,
        )

        db.session.add_all([exercise, workout])
        db.session.commit()

        with pytest.raises(IntegrityError):
            db.session.execute(
                text(
                    """
                    INSERT INTO workout_exercises
                        (workout_id, exercise_id, reps, sets, duration_seconds)
                    VALUES (:workout_id, :exercise_id, NULL, 3, NULL)
                    """
                ),
                {
                    "workout_id": workout.id,
                    "exercise_id": exercise.id,
                },
            )
            db.session.commit()

        db.session.rollback()


def test_database_rejects_duplicate_workout_exercise_pair(app):
    with app.app_context():
        exercise = Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False,
        )

        workout = Workout(
            date=date(2026, 10, 26),
            duration_minutes=45,
        )

        db.session.add_all([exercise, workout])
        db.session.commit()

        db.session.add(
            WorkoutExercise(
                workout_id=workout.id,
                exercise_id=exercise.id,
                reps=12,
            )
        )
        db.session.commit()

        with pytest.raises(IntegrityError):
            db.session.execute(
                text(
                    """
                    INSERT INTO workout_exercises
                        (workout_id, exercise_id, reps, sets, duration_seconds)
                    VALUES (:workout_id, :exercise_id, 15, 3, NULL)
                    """
                ),
                {
                    "workout_id": workout.id,
                    "exercise_id": exercise.id,
                },
            )
            db.session.commit()

        db.session.rollback()


# ---------------------------------------------------------
# RELATIONSHIPS AND DELETION
# ---------------------------------------------------------

def test_deleting_workout_removes_associations(app):
    with app.app_context():
        exercise = Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False,
        )

        workout = Workout(
            date=date(2026, 10, 26),
            duration_minutes=45,
        )

        db.session.add_all([exercise, workout])
        db.session.flush()

        association = WorkoutExercise(
            workout=workout,
            exercise=exercise,
            reps=12,
        )

        db.session.add(association)
        db.session.commit()

        workout_id = workout.id

        db.session.delete(workout)
        db.session.commit()

        assert db.session.get(Workout, workout_id) is None
        assert WorkoutExercise.query.count() == 0
        assert Exercise.query.count() == 1


def test_deleting_exercise_removes_associations(app):
    with app.app_context():
        exercise = Exercise(
            name="Push-ups",
            category="Strength",
            equipment_needed=False,
        )

        workout = Workout(
            date=date(2026, 10, 26),
            duration_minutes=45,
        )

        db.session.add_all([exercise, workout])
        db.session.flush()

        db.session.add(
            WorkoutExercise(
                workout=workout,
                exercise=exercise,
                reps=12,
            )
        )
        db.session.commit()

        exercise_id = exercise.id

        db.session.delete(exercise)
        db.session.commit()

        assert db.session.get(Exercise, exercise_id) is None
        assert WorkoutExercise.query.count() == 0
        assert Workout.query.count() == 1
