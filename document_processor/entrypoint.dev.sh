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

# Start debug server
# echo "Starting development server..."
# exec python manage.py runserver 0.0.0.0:8000

# Start with gunicorn
exec gunicorn document_processor.wsgi:application --config config/dev/gunicorn.py --reload