# Backend (Django)

This directory contains the Django backend for the ParcelMyBox Portal.

## Project Structure

```
backend/
├── apps/               # Django applications
│   ├── api/            # API endpoints
│   ├── category/       # Category management
│   ├── shipping/       # Shipping functionality
│   └── customerData/   # Customer data management
├── core/               # Core Django project
│   └── pmb_core/       # Project settings and configurations
├── static/             # Static files (CSS, JS, images)
└── media/              # User-uploaded files
```

## Development Setup

1. **Prerequisites**
   - Python 3.10+
   - pip
   - MySQL/MariaDB

2. **Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables (copy .env.example to .env and configure)
   cp .env.example .env
   ```

3. **Database Setup**
   ```bash
   # Run migrations
   python manage.py migrate

   # Create superuser
   python manage.py createsuperuser
   ```

4. **Running the Server**
   ```bash
   python manage.py runserver
   ```

## API Documentation

API documentation is available at `/api/docs/` when running the development server.

## Testing

```bash
# Run tests
python manage.py test
```

## Deployment

For production deployment, ensure:
- `DEBUG=False` in settings
- Proper database configuration
- Static files collected (`python manage.py collectstatic`)
- Gunicorn or similar WSGI server configured
