#!/bin/bash
set -e

# Set the correct Python path
export PYTHONPATH=/app:/app/pmb_core:$PYTHONPATH

# Function to log messages with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Wait for database to be ready
log "Waiting for database to be ready..."
max_retries=30
retry_count=0

until mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        log "Error: Could not connect to database after $max_retries attempts. Exiting."
        exit 1
    fi
    log "Waiting for database... (Attempt $retry_count/$max_retries)"
    sleep 2
done

log "Database is ready!"

# Run migrations
log "Running migrations..."
python manage.py makemigrations --noinput || {
    log "Error: Failed to make migrations"
    exit 1
}

python manage.py migrate --noinput || {
    log "Error: Failed to apply migrations"
    exit 1
}

# Create superuser if it doesn't exist
log "Creating superuser if needed..."
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

# Load initial data
log "Loading initial data..."
python manage.py load_courier_plans || {
    log "Warning: Failed to load courier plans (this might be expected if already loaded)"
}

# Initialize city codes
log "Initializing city codes..."
python manage.py init_city_codes || {
    log "Warning: Failed to initialize city codes (this might be expected if already initialized)"
}

# Collect static files
log "Collecting static files..."
python manage.py collectstatic --noinput --clear || {
    log "Error: Failed to collect static files"
    exit 1
}

# Start Streamlit in the background
log "Starting Streamlit..."
nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > /var/log/streamlit.log 2>&1 &

# Start Django
log "Starting Django development server..."
exec python manage.py runserver 0.0.0.0:8000