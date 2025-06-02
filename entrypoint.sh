#!/bin/bash
set -e

# Wait for database to be ready
echo "Waiting for database..."
until mysqladmin ping -h$DB_HOST -u$DB_USER -p$DB_PASSWORD --silent; do
    echo "Waiting for database..."
    sleep 2
done

echo "Database is ready!"

# Run migrations
echo "Running migrations..."
python manage.py makemigrations
python manage.py migrate

# Initialize city codes
echo "Initializing city codes..."
python manage.py init_city_codes

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Start Streamlit in the background
echo "Starting Streamlit..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true &

# Start Django
echo "Starting Django..."
python manage.py runserver 0.0.0.0:8000

# Keep the container running
wait
