from datetime import date, timedelta

from app import create_app
from models import db, Exercise, Workout, WorkoutExercise


def seed_database():
    app = create_app()

    with app.app_context():
        try:
            # Clear existing data in dependency order.
            WorkoutExercise.query.delete(synchronize_session=False)
            Workout.query.delete(synchronize_session=False)
            Exercise.query.delete(synchronize_session=False)

            db.session.commit()

            # Create reusable exercises.
            push_ups = Exercise(
                name="Push-ups",
                category="Strength",
                equipment_needed=False,
            )

            squats = Exercise(
                name="Squats",
                category="Strength",
                equipment_needed=False,
            )

            running = Exercise(
                name="Running",
                category="Cardio",
                equipment_needed=True,
            )

            plank = Exercise(
                name="Plank",
                category="Core",
                equipment_needed=False,
            )

            db.session.add_all([
                push_ups,
                squats,
                running,
                plank,
            ])
            db.session.flush()

            # Create workout sessions.
            workout_one = Workout(
                date=date.today(),
                duration_minutes=45,
                notes="Full-body strength training",
            )

            workout_two = Workout(
                date=date.today() - timedelta(days=1),
                duration_minutes=30,
                notes="Cardio and core training",
            )

            db.session.add_all([workout_one, workout_two])
            db.session.flush()

            # Connect exercises to workouts.
            associations = [
                WorkoutExercise(
                    workout=workout_one,
                    exercise=push_ups,
                    reps=12,
                    sets=3,
                ),
                WorkoutExercise(
                    workout=workout_one,
                    exercise=squats,
                    reps=15,
                    sets=3,
                ),
                WorkoutExercise(
                    workout=workout_two,
                    exercise=running,
                    duration_seconds=1200,
                ),
                WorkoutExercise(
                    workout=workout_two,
                    exercise=plank,
                    duration_seconds=60,
                    sets=3,
                ),
            ]

            db.session.add_all(associations)
            db.session.commit()

            print("Database seeded successfully.")
            print(f"Exercises: {Exercise.query.count()}")
            print(f"Workouts: {Workout.query.count()}")
            print(f"Workout-exercise associations: {WorkoutExercise.query.count()}")

        except Exception:
            db.session.rollback()
            raise

        finally:
            db.session.remove()


if __name__ == "__main__":
    seed_database()
