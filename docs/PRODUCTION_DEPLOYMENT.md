# Production Deployment Guide

This document outlines the steps to deploy the ParcelMyBox application in a production environment.

## Prerequisites

- Docker and Docker Compose installed on the production server
- Domain name pointing to your server's IP address
- SSL certificates (or use Let's Encrypt)
- Email service credentials (for sending emails)

## 1. Server Setup

1. **Update the system**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install Docker and Docker Compose** (if not already installed)
   ```bash
   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   
   # Install Docker Compose
   sudo apt install docker-compose-plugin
   
   # Add your user to the docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

## 2. Application Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pmb-portal.git
   cd pmb-portal
   ```

2. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Generate secure secrets
   bash scripts/generate_secrets.sh
   
   # Edit the .env file with your production settings
   nano .env
   ```

3. **Update the following settings in .env**:
   - `ALLOWED_HOSTS`: Add your domain name
   - `CSRF_TRUSTED_ORIGINS`: Add your domain with https://
   - Email settings
   - Database credentials (should match those in docker-compose.prod.yml)
   - Any other environment-specific settings

## 3. SSL Certificates (Let's Encrypt)

1. **Install Certbot**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   ```

2. **Obtain certificates**
   ```bash
   sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   ```

3. **Update Nginx configuration** with the correct certificate paths
   ```bash
   # In nginx/nginx.conf, update these lines:
   ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
   ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
   ```

## 4. Start the Application

1. **Build and start the containers**
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```

2. **Run database migrations**
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```

3. **Collect static files**
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
   ```

4. **Create a superuser**
   ```bash
   docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
   ```

## 5. Regular Maintenance

1. **Backup the database**
   ```bash
   # Create a daily backup script at /usr/local/bin/backup_db.sh
   # Add to crontab: 0 3 * * * /usr/local/bin/backup_db.sh
   ```

2. **Update the application**
   ```bash
   git pull origin main
   docker compose -f docker-compose.prod.yml up -d --build
   docker compose -f docker-compose.prod.yml exec web python manage.py migrate
   docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
   ```

3. **Monitor logs**
   ```bash
   # View logs
   docker compose -f docker-compose.prod.yml logs -f
   
   # View specific service logs
   docker compose -f docker-compose.prod.yml logs -f web
   docker compose -f docker-compose.prod.yml logs -f db
   docker compose -f docker-compose.prod.yml logs -f nginx
   ```

## 6. Security Hardening

1. **Firewall configuration** (UFW)
   ```bash
   sudo ufw allow ssh
   sudo ufw allow http
   sudo ufw allow https
   sudo ufw enable
   ```

2. **Automatic security updates**
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Database backup**
   Set up regular database backups using a cron job or your preferred backup solution.

## 7. Scaling

For higher traffic, consider:

1. **Horizontal scaling**: Add more application servers behind a load balancer
2. **Database**: Use a managed database service or set up database replication
3. **Caching**: Implement Redis for caching
4. **CDN**: Use a CDN for static and media files

## 8. Monitoring

1. **Container health**
   ```bash
   docker ps --format "table {{.Names}}\t{{.Status}}"
   ```

2. **Resource usage**
   ```bash
   docker stats
   ```

3. **Application monitoring**
   Consider using tools like:
   - Prometheus + Grafana
   - Sentry for error tracking
   - ELK stack for logging

## 9. Troubleshooting

Common issues and solutions:

1. **Port already in use**
   ```bash
   sudo lsof -i :80
   sudo kill <PID>
   ```

2. **Database connection issues**
   ```bash
   docker compose -f docker-compose.prod.yml exec db mysql -u root -p
   ```

3. **View application logs**
   ```bash
   docker compose -f docker-compose.prod.yml logs -f web
   ```

## 10. Updating the Application

1. Pull the latest changes
2. Rebuild the containers
3. Run migrations
4. Collect static files
5. Restart the services

```bash
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input
docker compose -f docker-compose.prod.yml restart
```

For zero-downtime deployments, consider using a blue-green deployment strategy.
