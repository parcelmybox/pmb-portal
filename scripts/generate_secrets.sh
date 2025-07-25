#!/bin/bash

# Generate a secure random secret key for Django
DJANGO_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")

# Generate a secure random password for the database
DB_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Generate a secure random root password for MySQL
MYSQL_ROOT_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Generate a secure salt for hashing
SECURE_HASHING_SALT=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# Create .env file with the generated secrets
cat > .env << EOL
# Django Settings
DEBUG=0
SECRET_KEY=${DJANGO_SECRET_KEY}
ALLOWED_HOSTS=.localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com

# Database Settings
DB_NAME=pmb_db
DB_USER=pmb_app
DB_PASSWORD=${DB_PASSWORD}
DB_HOST=db
DB_PORT=3306
MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}

# Security Settings
SECURE_HASHING_SALT=${SECURE_HASHING_SALT}

# Email Settings (update these with your actual email settings)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Frontend Settings
FRONTEND_URL=https://yourdomain.com
API_URL=https://api.yourdomain.com

# Logging Level
LOG_LEVEL=INFO
EOL

echo "Generated .env file with secure secrets. Please review and update any placeholder values."
echo "IMPORTANT: Keep this file secure and never commit it to version control!"

# Set appropriate permissions
chmod 600 .env
