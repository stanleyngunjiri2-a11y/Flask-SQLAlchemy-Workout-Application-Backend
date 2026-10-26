from marshmallow import Schema, ValidationError, fields, validates, validates_schema


class ExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    category = fields.String(required=True)
    equipment_needed = fields.Boolean(required=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Exercise name cannot be empty.")

        if len(value.strip()) > 120:
            raise ValidationError(
                "Exercise name cannot exceed 120 characters."
            )

    @validates("category")
    def validate_category(self, value, **kwargs):
        if not value.strip():
            raise ValidationError("Exercise category cannot be empty.")

        if len(value.strip()) > 80:
            raise ValidationError(
                "Exercise category cannot exceed 80 characters."
            )


class WorkoutSchema(Schema):
    id = fields.Integer(dump_only=True)
    date = fields.Date(required=True)
    duration_minutes = fields.Integer(required=True)
    notes = fields.String(allow_none=True, load_default=None)
    exercises = fields.Nested(
        ExerciseSchema,
        many=True,
        dump_only=True,
    )

    @validates("duration_minutes")
    def validate_duration_minutes(self, value, **kwargs):
        if not 1 <= value <= 1440:
            raise ValidationError(
                "Workout duration must be between 1 and 1440 minutes."
            )


class WorkoutExerciseSchema(Schema):
    id = fields.Integer(dump_only=True)
    workout_id = fields.Integer(dump_only=True)
    exercise_id = fields.Integer(dump_only=True)
    reps = fields.Integer(allow_none=True, load_default=None)
    sets = fields.Integer(allow_none=True, load_default=None)
    duration_seconds = fields.Integer(
        allow_none=True,
        load_default=None,
    )

    @validates("reps")
    def validate_reps(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("Repetitions must be positive.")

    @validates("sets")
    def validate_sets(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("Sets must be positive.")

    @validates("duration_seconds")
    def validate_duration_seconds(self, value, **kwargs):
        if value is not None and value <= 0:
            raise ValidationError("Exercise duration must be positive.")

    @validates_schema
    def validate_reps_or_duration(self, data, **kwargs):
        if data.get("reps") is None and data.get("duration_seconds") is None:
            raise ValidationError(
                "Provide repetitions or duration_seconds."
            )
