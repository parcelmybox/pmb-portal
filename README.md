# Parcel My Box Portal
## "Tech that ships, and code that clicks!"

## Project Structure

```
pmb-portal/
├── backend/                 # Backend Django application
│   ├── apps/               # Django apps (api, shipping, category, etc.)
│   │   ├── api/           # API endpoints
│   │   ├── category/      # Category management
│   │   ├── shipping/      # Shipping functionality
│   │   └── customerData/  # Customer data management
│   ├── core/               # Core Django project
│   │   └── pmb_core/      # Project settings and configurations
│   ├── static/             # Static files (CSS, JS, images)
│   └── media/              # User-uploaded files
└── frontend/               # Frontend React app
    ├── public/            # Static files
    ├── src/               # Source code
    │   ├── components/    # Reusable UI components
    │   ├── pages/         # Page components
    │   ├── services/      # API services
    │   ├── utils/         # Utility functions
    │   ├── App.js         # Main App component
    │   └── index.js       # Entry point
    └── package.json       # Dependencies and scripts
```

## Prerequisites

- **Docker & Docker Compose**
  - Windows/macOS: [Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/) & [Docker Compose](https://docs.docker.com/compose/install/)
- **Node.js** 16+ (for frontend development)
- **Python** 3.10+ (for backend development)
- **MySQL/MariaDB** (or use Docker container)

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/parcelmybox/pmb-portal.git
cd pmb-portal
```

### 2. Setup Development Environment

#### Option A: Using Docker (Recommended)

1. Start all services:
   ```bash
   docker compose up -d
   ```
   This will start:
   - Django backend (port 8000)
   - React frontend (port 3000)
   - MariaDB database (port 3306)

2. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin interface: http://localhost:8000/admin

#### Option B: Manual Setup

1. **Backend Setup**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

- Main application: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

### 4. Create Superuser (Optional)

If you need to create a superuser for the admin interface:

```bash
docker compose exec web python create_superuser.py
```

Default credentials:
- Username: admin
- Password: admin123

### 5. Initialize Data

To initialize sample categories and shipping rates:

```bash
docker compose exec web python manage.py init_categories
```

## Development

### Stopping the Application

```bash
docker compose down
```

### Rebuilding Containers

If you make changes to the Docker configuration or dependencies:

```bash
docker compose up -d --build
```

### Accessing the Shell

To access the web container shell:

```bash
docker compose exec web bash
```
