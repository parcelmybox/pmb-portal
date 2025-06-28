#!/bin/bash
set -e

echo "=== Starting ParcelMyBox Backend ==="

# Set Python path
export PYTHONPATH="/app/backend:/app/backend/core:/app/backend/apps"

# Change to the project directory
cd /app/backend

echo "PYTHONPATH set to: $PYTHONPATH"

# Wait for database to be ready
echo "Waiting for database ($DB_HOST:$DB_PORT)..."
max_retries=30
counter=0

until mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
    counter=$((counter+1))
    if [ $counter -ge $max_retries ]; then
        echo "ERROR: Could not connect to database after $max_retries attempts"
        exit 1
    fi
    echo "Waiting for database to be ready... (attempt $counter/$max_retries)"
    sleep 2
done

echo "✓ Database is ready!"

# Verify the database exists, create if it doesn't
echo "Verifying database $DB_NAME exists..."
if ! mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "USE $DB_NAME" >/dev/null 2>&1; then
    echo "Database $DB_NAME not found, creating..."
    mysql -h"$DB_HOST" -P"$DB_PORT" -u"$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo "✓ Database $DB_NAME created"
else
    echo "✓ Database $DB_NAME exists"
fi

# Run database migrations
echo -e "\n=== Running Database Migrations ==="
python manage.py check --database default || exit 1
python manage.py makemigrations --noinput
python manage.py migrate --noinput

if python manage.py help | grep -q '^\s*init_city_codes\s'; then
    echo "\n=== Initializing City Codes ==="
    python manage.py init_city_codes
fi

# Create superuser if not exists
echo "\n=== Setting Up Admin User ==="
if [ -z "$(python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())" 2>/dev/null | grep 'True')" ]; then
    echo "Creating admin user..."
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
else
    echo "Admin user already exists"
fi

# Collect static files
echo "\n=== Collecting Static Files ==="
python manage.py collectstatic --noinput --clear

# Start Streamlit in the background if the file exists
if [ -f "streamlit_app.py" ]; then
    echo "\n=== Starting Streamlit ==="
    nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > /var/log/streamlit.log 2>&1 &
    echo "Streamlit is running on http://localhost:8501"
fi

# Start Django development server
echo "\n=== Starting Django Development Server ==="
echo "Django is running on http://localhost:8000"
exec python manage.py runserver 0.0.0.0:8000

echo "\n=== Application Started Successfully ==="

# Keep the container running
tail -f /dev/null
wait
