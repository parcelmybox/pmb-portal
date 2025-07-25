FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/pmb_core:$PYTHONPATH \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies with cleanup in a single layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    default-mysql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies with cache cleanup
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create a new entrypoint script with proper line endings
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'set -e' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Set the correct Python path' >> /docker-entrypoint.sh && \
    echo 'export PYTHONPATH=/app:/app/pmb_core:$PYTHONPATH' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Function to log messages with timestamp' >> /docker-entrypoint.sh && \
    echo 'log() {' >> /docker-entrypoint.sh && \
    echo '    echo "[$(date "+%Y-%m-%d %H:%M:%S")] $1"' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Wait for database to be ready' >> /docker-entrypoint.sh && \
    echo 'log "Waiting for database to be ready..."' >> /docker-entrypoint.sh && \
    echo 'max_retries=30' >> /docker-entrypoint.sh && \
    echo 'retry_count=0' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'until mysqladmin ping -h"$DB_HOST" -u"$DB_USER" -p"$DB_PASSWORD" --silent; do' >> /docker-entrypoint.sh && \
    echo '    retry_count=$((retry_count + 1))' >> /docker-entrypoint.sh && \
    echo '    if [ $retry_count -ge $max_retries ]; then' >> /docker-entrypoint.sh && \
    echo '        log "Error: Could not connect to database after $max_retries attempts. Exiting."' >> /docker-entrypoint.sh && \
    echo '        exit 1' >> /docker-entrypoint.sh && \
    echo '    fi' >> /docker-entrypoint.sh && \
    echo '    log "Waiting for database... (Attempt $retry_count/$max_retries)"' >> /docker-entrypoint.sh && \
    echo '    sleep 2' >> /docker-entrypoint.sh && \
    echo 'done' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'log "Database is ready!"' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Run migrations' >> /docker-entrypoint.sh && \
    echo 'log "Running migrations..."' >> /docker-entrypoint.sh && \
    echo 'python manage.py makemigrations --noinput || {' >> /docker-entrypoint.sh && \
    echo '    log "Error: Failed to make migrations"' >> /docker-entrypoint.sh && \
    echo '    exit 1' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo 'python manage.py migrate --noinput || {' >> /docker-entrypoint.sh && \
    echo '    log "Error: Failed to apply migrations"' >> /docker-entrypoint.sh && \
    echo '    exit 1' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Load initial data' >> /docker-entrypoint.sh && \
    echo 'log "Loading initial data..."' >> /docker-entrypoint.sh && \
    echo 'python manage.py load_courier_plans || {' >> /docker-entrypoint.sh && \
    echo '    log "Warning: Failed to load courier plans (this might be expected if already loaded)"' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Initialize city codes' >> /docker-entrypoint.sh && \
    echo 'log "Initializing city codes..."' >> /docker-entrypoint.sh && \
    echo 'python manage.py init_city_codes || {' >> /docker-entrypoint.sh && \
    echo '    log "Warning: Failed to initialize city codes (this might be expected if already initialized)"' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Collect static files' >> /docker-entrypoint.sh && \
    echo 'log "Collecting static files..."' >> /docker-entrypoint.sh && \
    echo 'python manage.py collectstatic --noinput --clear || {' >> /docker-entrypoint.sh && \
    echo '    log "Error: Failed to collect static files"' >> /docker-entrypoint.sh && \
    echo '    exit 1' >> /docker-entrypoint.sh && \
    echo '}' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Start Streamlit in the background' >> /docker-entrypoint.sh && \
    echo 'log "Starting Streamlit..."' >> /docker-entrypoint.sh && \
    echo 'nohup streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true > /var/log/streamlit.log 2>&1 &' >> /docker-entrypoint.sh && \
    echo '' >> /docker-entrypoint.sh && \
    echo '# Start Django' >> /docker-entrypoint.sh && \
    echo 'log "Starting Django development server..."' >> /docker-entrypoint.sh && \
    echo 'exec python manage.py runserver 0.0.0.0:8000' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh && \
    sed -i 's/\r$//' /docker-entrypoint.sh

# Expose the ports the app runs on
EXPOSE 8000 8501

# Set the entrypoint script as the default command
CMD ["/docker-entrypoint.sh"]
