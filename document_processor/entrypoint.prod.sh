#!/bin/bash

# Wait for database
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start production server
echo "Starting production server..."
gunicorn document_processor.wsgi:application --bind 0.0.0.0:8000 --config config/prod/gunicorn.py 