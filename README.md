# Workout Application Backend

## About the Project

This is a Flask API for managing exercises and workouts. I built it using Flask, SQLAlchemy, and SQLite to practise creating APIs, working with databases, and validating data.

The application allows users to create exercises, organise workouts, and add exercises to specific workouts.

## Features

- Create, view, and delete exercises.
- Create, view, and delete workouts.
- Add exercises to a workout.
- Store exercise names, categories, and equipment requirements.
- Record workout dates and durations.
- Validate input and handle errors.
- Prevent duplicate exercises in the same workout.
- Use database constraints to maintain valid data.

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Marshmallow
- Flask-Migrate
- Pytest

## Setup and Installation

### 1. Install dependencies

Make sure Python and Pipenv are installed, then run:

    pipenv install --dev

### 2. Set up the database

From the project root, run:

    cd server
    pipenv run flask --app app db upgrade

The migration files are stored in the project-root migrations directory.
Flask-Migrate is configured to find them when commands are run from server.

### 3. Add sample data

From the project root, run:

    cd server
    pipenv run python seed.py

This adds sample exercises and workouts to the database. The seed script
clears existing exercise and workout records before inserting its sample data,
so do not run it if you need to preserve existing records.

Return to the project root before running the tests:

    cd ..

### 4. Start the application

Run:

    cd server
    pipenv run flask --app app run

Open http://127.0.0.1:5000 in your browser to access the API.

## Running Tests

I used Pytest to check the API endpoints, model validation, and database constraints.

Run the tests with:

    pipenv run pytest -v

The project currently has 55 passing tests.

## What I Learned

Working on this project helped me understand how to build a REST API using Flask, connect an application to a database, create relationships between models, validate data, and write automated tests. I also gained more experience handling errors and maintaining data consistency.
