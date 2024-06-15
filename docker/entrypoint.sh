#!/bin/sh

# entrypoint.sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start uWSGI
echo "Starting uWSGI..."
uwsgi --ini /usr/src/app/docker/uwsgi.ini
