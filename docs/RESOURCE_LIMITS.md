# Docker Compose Resource Limits

This document outlines the resource limits and reservations configured in the `docker-compose.yml` file for the ParcelMyBox application.

## Database Service (`db`)

- **CPU Limit**: 1 core
- **Memory Limit**: 1GB
- **Memory Reservation**: 512MB
- **Health Check**: Configured to check database availability with a 10-second timeout, 10 retries, and 10-second intervals.

## Web Service (`web`)

- **CPU Limit**: 1 core
- **Memory Limit**: 2GB
- **Memory Reservation**: 1GB
- **Depends On**: Database service must be healthy before starting
- **Ports**:
  - 8000: Django development server
  - 8501: Streamlit (if applicable)

## Frontend Service (`frontend`)

- No explicit resource limits are set, allowing it to use host resources as needed.
- Runs on port 3000
- Depends on the web service

## Volumes

- `mysql_data`: Persistent storage for MariaDB data
- `static_volume`: Persistent storage for Django static files
- `media_volume`: Persistent storage for user-uploaded media files

## Network

- A custom bridge network `pmb_network` is created for container communication.

## Notes

- These limits are suitable for development and testing environments.
- For production, consider adjusting these values based on your workload requirements.
- The database service has a health check to ensure it's ready before the web service starts.
- The web service has higher memory allocation to handle both Django and any background tasks.

## Adjusting Resource Limits

To adjust these limits, modify the `deploy.resources` section in the respective service in `docker-compose.yml`. For example:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'      # Increase CPU cores
      memory: 4096M   # Increase memory to 4GB
    reservations:
      memory: 2048M   # Increase reserved memory to 2GB
```

Remember to run `docker-compose up -d` after making changes to apply the new resource limits.
