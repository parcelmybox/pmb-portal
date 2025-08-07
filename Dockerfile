FROM python:3.10-slim

# --- Environment Variables ---
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    DEBIAN_FRONTEND=noninteractive

# --- System Dependencies ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    default-libmysqlclient-dev \
    pkg-config \
    default-mysql-client \
    dos2unix \
    htop \
    && rm -rf /var/lib/apt/lists/*

# --- Working Directory ---
WORKDIR /app

# --- Install Python Dependencies ---
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Copy Application ---
COPY . .

# --- Convert entrypoint.sh to Unix line endings (only this one!) ---
RUN dos2unix /app/entrypoint.sh

# --- Expose only Django (8000) ---
EXPOSE 8000
