FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Create directories
RUN mkdir -p /app/staticfiles /app/media
RUN chown -R www-data:www-data /app
RUN chmod -R 755 /app

# Copy application code
COPY pmb_hello/ .

# Set proper permissions
RUN chmod +x manage.py
RUN chmod -R 755 /app

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
