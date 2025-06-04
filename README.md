# Parcel My Box Portal
## “Tech that ships, and code that clicks!”
## Prerequisites

- Docker
  - Windows: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
  - macOS: [Download Docker Desktop](https://www.docker.com/products/docker-desktop)
  - Linux: [Install Docker Engine](https://docs.docker.com/engine/install/)
- Docker Compose
  - Included with Docker Desktop for Windows and macOS
  - Linux: [Install Docker Compose](https://docs.docker.com/compose/install/)


## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/parcelmybox/pmb-portal.git
cd pmb-portal
```

### 2. Start the Application with Docker

The application uses Docker Compose for easy setup. All services (web application and database) are configured in `docker-compose.yml`.

To start the application:

```bash
docker compose up -d
```

This will:
1. Build the Docker containers
2. Start the MariaDB database
3. Start the Django application

### 3. Access the Application

Once the containers are running, you can access:

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
