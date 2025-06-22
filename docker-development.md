# Development Workflow with Docker

## Getting Started
```bash
# Start containers in detached mode
docker compose up -d

# View logs to monitor the application
docker compose logs -f

# Stop containers when done
docker compose down
```

## Common Development Tasks
```bash
# Run Django management commands
docker compose exec web python manage.py shell
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Restart the web container after changes
docker compose restart web

# Check PostgreSQL database
docker compose exec db psql -U postgres -d sistemas_evaluacion

# Rebuild containers (after changes to Dockerfile or requirements)
docker compose build
docker compose up -d
```

## Database Management
```bash
# Backup database
docker compose exec db pg_dump -U postgres sistemas_evaluacion > backup.sql

# Restore database
cat backup.sql | docker compose exec -T db psql -U postgres sistemas_evaluacion

# Connect to database via psql
docker compose exec db psql -U postgres -d sistemas_evaluacion
```

## Cleaning Up
```bash
# Stop and remove containers but preserve volume data
docker compose down

# Stop and remove containers, networks, images and volumes (CAUTION: Deletes data)
docker compose down -v --rmi all
```

## Production Deployment
For production, consider:
1. Setting DEBUG=False and updating ALLOWED_HOSTS in .env
2. Using a production-ready web server like Nginx
3. Setting proper security headers
4. Using environment-specific settings
