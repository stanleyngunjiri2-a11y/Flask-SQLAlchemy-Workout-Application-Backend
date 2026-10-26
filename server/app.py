from flask import Flask, jsonify, request
from flask_migrate import Migrate
from pathlib import Path
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI="sqlite:///workout.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    Migrate(app, db, directory=str(Path(__file__).resolve().parent.parent / "migrations"))

    # Import models so Flask-Migrate can discover every table.
    from models import Exercise, Workout, WorkoutExercise  # noqa: F401

    exercise_schema = ExerciseSchema()
    workout_schema = WorkoutSchema()
    workout_exercise_schema = WorkoutExerciseSchema()

    exercises_schema = ExerciseSchema(many=True)
    workouts_schema = WorkoutSchema(many=True)

    @app.get("/")
    def index():
        return jsonify({
            "message": "Workout Application API",
            "status": "running",
        })

    # ---------------------------------------------------------
    # WORKOUT ENDPOINTS
    # ---------------------------------------------------------

    @app.get("/workouts")
    def get_workouts():
        workouts = Workout.query.order_by(Workout.id).all()
        return jsonify(workouts_schema.dump(workouts)), 200

    @app.get("/workouts/<int:workout_id>")
    def get_workout(workout_id):
        workout = db.session.get(Workout, workout_id)

        if workout is None:
            return jsonify({"error": "Workout not found."}), 404

        return jsonify(workout_schema.dump(workout)), 200

    @app.post("/workouts")
    def create_workout():
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Request body must be a valid JSON object."
            }), 400

        try:
            data = workout_schema.load(payload)
            workout = Workout(**data)

            db.session.add(workout)
            db.session.commit()

            return jsonify(workout_schema.dump(workout)), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400

        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": "Workout could not be saved because of a database constraint."
            }), 400

    @app.delete("/workouts/<int:workout_id>")
    def delete_workout(workout_id):
        workout = db.session.get(Workout, workout_id)

        if workout is None:
            return jsonify({"error": "Workout not found."}), 404

        db.session.delete(workout)
        db.session.commit()

        return "", 204

    # ---------------------------------------------------------
    # EXERCISE ENDPOINTS
    # ---------------------------------------------------------

    @app.get("/exercises")
    def get_exercises():
        exercises = Exercise.query.order_by(Exercise.id).all()
        return jsonify(exercises_schema.dump(exercises)), 200

    @app.get("/exercises/<int:exercise_id>")
    def get_exercise(exercise_id):
        exercise = db.session.get(Exercise, exercise_id)

        if exercise is None:
            return jsonify({"error": "Exercise not found."}), 404

        return jsonify(exercise_schema.dump(exercise)), 200

    @app.post("/exercises")
    def create_exercise():
        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Request body must be a valid JSON object."
            }), 400

        try:
            data = exercise_schema.load(payload)
            exercise = Exercise(**data)

            db.session.add(exercise)
            db.session.commit()

            return jsonify(exercise_schema.dump(exercise)), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400

        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": "Exercise could not be saved because of a database constraint."
            }), 400

    @app.delete("/exercises/<int:exercise_id>")
    def delete_exercise(exercise_id):
        exercise = db.session.get(Exercise, exercise_id)

        if exercise is None:
            return jsonify({"error": "Exercise not found."}), 404

        db.session.delete(exercise)
        db.session.commit()

        return "", 204

    # ---------------------------------------------------------
    # WORKOUT-EXERCISE ASSOCIATION ENDPOINT
    # ---------------------------------------------------------

    @app.post(
        "/workouts/<int:workout_id>/exercises/"
        "<int:exercise_id>/workout_exercises"
    )
    def add_exercise_to_workout(workout_id, exercise_id):
        workout = db.session.get(Workout, workout_id)

        if workout is None:
            return jsonify({"error": "Workout not found."}), 404

        exercise = db.session.get(Exercise, exercise_id)

        if exercise is None:
            return jsonify({"error": "Exercise not found."}), 404

        payload = request.get_json(silent=True)

        if not isinstance(payload, dict):
            return jsonify({
                "error": "Request body must be a valid JSON object."
            }), 400

        try:
            data = workout_exercise_schema.load(payload)

            association = WorkoutExercise(
                workout=workout,
                exercise=exercise,
                **data,
            )

            db.session.add(association)
            db.session.commit()

            return jsonify(
                workout_exercise_schema.dump(association)
            ), 201

        except ValidationError as error:
            db.session.rollback()
            return jsonify({"errors": error.messages}), 400

        except ValueError as error:
            db.session.rollback()
            return jsonify({"error": str(error)}), 400

        except IntegrityError:
            db.session.rollback()
            return jsonify({
                "error": (
                    "The association could not be saved. "
                    "Check the supplied values and whether this exercise "
                    "is already associated with the workout."
                )
            }), 400

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
