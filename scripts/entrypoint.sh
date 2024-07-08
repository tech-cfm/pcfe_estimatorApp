#!/bin/sh

# entrypoint.sh
# Check if user exists, if not create the user
# Wait for PostgreSQL to start
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_ADMIN" -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up - executing command"

# Check if the user exists, create if not
PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_ADMIN" -tAc "SELECT 1 FROM pg_roles WHERE rolname='$POSTGRES_USER'" | grep -q 1 || \
PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_ADMIN" -c "CREATE USER $POSTGRES_USER WITH PASSWORD '$POSTGRES_PASSWORD';"

# Grant privileges
PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_ADMIN" -c "GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "db" -U "$POSTGRES_ADMIN" -d "$POSTGRES_DB" -c "GRANT ALL ON SCHEMA public TO $POSTGRES_USER; ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $POSTGRES_USER;"
# Run database migrations
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start uWSGI
echo "Starting uWSGI..."
uwsgi --ini /usr/src/app/uwsgi.ini

# Run the rest of your commands
exec "$@"