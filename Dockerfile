FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH="/app/backend:/app/backend/core:/app/backend/apps:/app/backend/customers"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    default-mysql-client \
    mariadb-client \
    dos2unix \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /etc/mysql/conf.d/ \
    && echo '[client]\nprotocol=tcp' > /etc/mysql/conf.d/force-tcp.cnf

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the rest of the backend
COPY backend/ ./backend/

# Set the working directory to backend
WORKDIR /app/backend

# Expose the ports the app runs on
EXPOSE 8000 8501
