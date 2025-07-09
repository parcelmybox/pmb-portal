#!/bin/sh
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
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DEFAULT_ADMIN_USER', 'admin')
email = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@example.com')
password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    print(f'Creating superuser {username}...')
    User.objects.create_superuser(username, email, password)
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
"

python manage.py load_courier_plans

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
