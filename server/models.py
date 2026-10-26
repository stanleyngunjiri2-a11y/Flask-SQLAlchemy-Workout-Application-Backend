from datetime import date, datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates


db = SQLAlchemy()


class Exercise(db.Model):
    """A reusable exercise that can belong to multiple workouts."""

    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="ck_exercises_name_not_empty",
        ),
        CheckConstraint(
            "length(trim(category)) > 0",
            name="ck_exercises_category_not_empty",
        ),
    )

    @validates("name")
    def validate_name(self, key, value):
        """Require a non-empty exercise name."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise name cannot be empty.")

        value = value.strip()

        if len(value) > 120:
            raise ValueError("Exercise name cannot exceed 120 characters.")

        return value

    @validates("category")
    def validate_category(self, key, value):
        """Require a non-empty exercise category."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Exercise category cannot be empty.")

        value = value.strip()

        if len(value) > 80:
            raise ValueError("Exercise category cannot exceed 80 characters.")

        return value

    @validates("equipment_needed")
    def validate_equipment_needed(self, key, value):
        """Require a Boolean equipment flag."""
        if not isinstance(value, bool):
            raise ValueError("equipment_needed must be a Boolean.")

        return value

    def __repr__(self):
        return f"<Exercise id={self.id} name={self.name!r}>"


class Workout(db.Model):
    """A workout session that can contain multiple exercises."""

    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint(
            "duration_minutes > 0",
            name="ck_workouts_duration_positive",
        ),
        CheckConstraint(
            "duration_minutes <= 1440",
            name="ck_workouts_duration_max_24_hours",
        ),
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, key, value):
        """Require a positive workout duration of at most 24 hours."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("Workout duration must be an integer.")

        if not 1 <= value <= 1440:
            raise ValueError(
                "Workout duration must be between 1 and 1440 minutes."
            )

        return value

    @validates("date")
    def validate_date(self, key, value):
        """Require a valid Python date, excluding datetime objects."""
        if not isinstance(value, date) or isinstance(value, datetime):
            raise ValueError("Workout date must be a valid date.")

        return value

    def __repr__(self):
        return f"<Workout id={self.id} date={self.date}>"


class WorkoutExercise(db.Model):
    """Association between a workout and an exercise."""

    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)

    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )

    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )

    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    workout = db.relationship(
        "Workout",
        back_populates="workout_exercises",
    )

    exercise = db.relationship(
        "Exercise",
        back_populates="workout_exercises",
    )

    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "exercise_id",
            name="uq_workout_exercise_pair",
        ),
        CheckConstraint(
            "reps IS NULL OR reps > 0",
            name="ck_workout_exercises_reps_positive",
        ),
        CheckConstraint(
            "sets IS NULL OR sets > 0",
            name="ck_workout_exercises_sets_positive",
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercises_duration_positive",
        ),
        CheckConstraint(
            "reps IS NOT NULL OR duration_seconds IS NOT NULL",
            name="ck_workout_exercises_reps_or_duration",
        ),
    )

    @validates("reps")
    def validate_reps(self, key, value):
        """Allow omitted repetitions or require a positive integer."""
        if value is None:
            return value

        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Repetitions must be a positive integer.")

        return value

    @validates("sets")
    def validate_sets(self, key, value):
        """Allow omitted sets or require a positive integer."""
        if value is None:
            return value

        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("Sets must be a positive integer.")

        return value

    @validates("duration_seconds")
    def validate_duration_seconds(self, key, value):
        """Allow omitted duration or require a positive integer."""
        if value is None:
            return value

        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or value <= 0
        ):
            raise ValueError("Exercise duration must be a positive integer.")

        return value

    def __repr__(self):
        return (
            f"<WorkoutExercise workout_id={self.workout_id} "
            f"exercise_id={self.exercise_id}>"
        )
