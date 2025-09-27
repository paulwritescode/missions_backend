# GIK Missions Backend

GIK missions related backend functionalities and apis.

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

1. **Clone the repository**
   ```bash
   git clone git@github.com:godinkenyadev-ops/missions_backend.git
   cd missions_backend
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and configure your database settings:
   ```env
   DATABASE_NAME=missions_db
   DATABASE_USER=missions_user
   DATABASE_PASSWORD=your_secure_password
   DATABASE_HOST=missions_postgres
   DATABASE_PORT=5432
   DJANGO_SUPERUSER_USERNAME=admin
   DJANGO_SUPERUSER_EMAIL=admin@gmail.com
   DJANGO_SUPERUSER_PASSWORD=testpassword
   ```

3. **Build and run the application**
   ```bash
   docker compose up --build
   ```

4. **Access the application**
   - API: http://127.0.0.1:9050
   - Documentation: http://127.0.0.1:9050/api/docs
   - Admin panel: http://127.0.0.1:9050/admin
   - admin credentials: (`api/superuser_setup.py`) uses env vars mentioned above to create superuser automatically

## Project Structure
This will change over time, but here is the current structure:
```
missions_backend
    ├── api
    │   ├── authentication
    │   │   ├── api.py
    │   │   ├── backends
    │   │   │   ├── apple.py
    │   │   │   ├── base.py
    │   │   │   ├── google.py
    │   │   │   ├── __init__.py
    │   │   │   ├── jwt.py
    │   │   │   └── registry.py
    │   │   ├── constants.py
    │   │   ├── __init__.py
    │   │   ├── middleware.py
    │   │   ├── permissions.py
    │   │   ├── schemas.py
    │   │   └── utils.py
    │   ├── base
    │   │   ├── api.py
    │   │   ├── apps.py
    │   │   ├── filters.py
    │   │   ├── __init__.py
    │   │   ├── models.py
    │   │   ├── schemas.py
    │   │   └── utils
    │   │       ├── exceptions.py
    │   │       ├── helpers.py
    │   │       └── __init__.py
    │   ├── manage.py
    │   ├── project
    │   │   ├── api.py
    │   │   ├── asgi.py
    │   │   ├── __init__.py
    │   │   ├── settings.py
    │   │   ├── urls.py
    │   │   └── wsgi.py
    │   ├── superuser_setup.py
    │   └── users
    │       ├── admin.py
    │       ├── api.py
    │       ├── apps.py
    │       ├── constants.py
    │       ├── __init__.py
    │       ├── managers.py
    │       ├── migrations
    │       │   ├── 0001_initial.py
    │       │   └── __init__.py
    │       ├── models.py
    │       └── tests.py
    ├── docker-compose.yaml
    ├── Dockerfile
    ├── .env
    ├── .env.example
    ├── .gitignore
    ├── poetry.lock
    ├── pyproject.toml
    └── README.md

```

## Services

### Backend (Django)
- **Container**: `missions_backend`
- **Port**: 9050 (maps to container port 8000)
- **Features**:
  - Automatic database migrations
  - Automatic superuser creation
  - Hot reload for development

### Database (PostgreSQL)
- **Container**: `missions_postgres`
- **Port**: 5435 (maps to container port 5432)
- **Data persistence**: Volume `postgres_data`

## Development Commands

### Start services
```bash
docker compose up
```

### Build and start (after code changes)
```bash
docker compose up --build
```

### Run in background
```bash
docker compose up -d
```

### View logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f db
```

### Execute commands in containers
```bash
# Django management commands
docker compose exec backend poetry run python api/manage.py <command>

# Shell access
docker compose exec backend bash
docker compose exec db psql -U ${DATABASE_USER} -d ${DATABASE_NAME}
```

### Stop services
```bash
docker compose down
```

### Complete cleanup (removes containers, networks, volumes, and images)
```bash
docker compose down --rmi all --volumes --remove-orphans
```

## Common Django Commands

```bash
# Create migrations
docker compose exec backend poetry run python api/manage.py makemigrations

# Apply migrations(if needed manually)
docker compose exec backend poetry run python api/manage.py migrate

# Create superuser (if needed manually)
docker compose exec backend poetry run python api/manage.py createsuperuser

# Django shell
docker compose exec backend poetry run python api/manage.py shell

# Collect static files (for production)
docker compose exec backend poetry run python api/manage.py collectstatic
```

## Environment Variables
| Variable                    | Description                                  | Default / Example                             |
| --------------------------- | -------------------------------------------- | --------------------------------------------- |
| `DATABASE_NAME`             | PostgreSQL database name                     | `missions_db`                                 |
| `DATABASE_USER`             | PostgreSQL username                          | `postgres`                                    |
| `DATABASE_PASSWORD`         | PostgreSQL password                          | `postgres`                                    |
| `DATABASE_HOST`             | PostgreSQL host                              | `db`                                          |
| `DATABASE_PORT`             | PostgreSQL port                              | `5432`                                        |
| `DJANGO_SUPERUSER_USERNAME` | Django admin username                        | `admin`                                       |
| `DJANGO_SUPERUSER_EMAIL`    | Django admin email                           | `admin@gmail.com`                             |
| `DJANGO_SUPERUSER_PASSWORD` | Django admin password                        | `adminpassword`                               |
| `DJANGO_SECRET_KEY`         | Django secret key                            | `your-secret-key-here`                        |
| `ALLOWED_HOSTS`             | Comma-separated list of allowed hosts        | `*`                                           |
| `DEBUG`                     | Enable/disable debug mode                    | `True`                                        |
| `CORS_ALLOWED_ORIGINS`      | Comma-separated list of allowed CORS origins | `http://localhost:3000,http://127.0.0.1:3000` |
| `GOOGLE_CLIENT_ID`          | Google OAuth client ID                       | -                                             |
| `GOOGLE_CLIENT_SECRET`      | Google OAuth client secret                   | -                                             |
| `GOOGLE_REDIRECT_URI`       | Google OAuth redirect URI                    | -                                             |
| `APPLE_CLIENT_ID`           | Apple OAuth client ID                        | -                                             |
| `APPLE_TEAM_ID`             | Apple developer team ID                      | -                                             |
| `APPLE_KEY_ID`              | Apple private key ID                         | -                                             |
| `APPLE_PRIVATE_KEY`         | Apple private key content                    | -                                             |
| `APPLE_REDIRECT_URI`        | Apple OAuth redirect URI                     | -                                             |


## Troubleshooting

### Port already in use
If port 9050 is busy, change it in `docker-compose.yaml`:
```yaml
ports:
  - "9051:8000"  # Use different port
```

### Database connection issues
1. Ensure PostgreSQL container is healthy:
   ```bash
   docker compose ps
   ```
2. Check database logs:
   ```bash
   docker compose logs db
   ```

### Container won't start
1. Check logs for errors:
   ```bash
   docker compose logs backend
   ```
2. Rebuild containers:
   ```bash
   docker compose up --build --force-recreate
   ```

### Permission issues
Ensure your user is in the docker group:
```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

### Complete reset
If you need to start fresh:
```bash
docker compose down --rmi all --volumes --remove-orphans
docker compose up --build
```

## Production Considerations

For production deployment:

1. **Environment variables**: Use secure values and environment-specific settings
2. **Database**: Consider managed PostgreSQL service
3. **Static files**: Configure proper static file serving
4. **Security**: Update `ALLOWED_HOSTS` and `SECRET_KEY`
5. **Server**: Replace development server with Gunicorn/uWSGI
6. **Reverse proxy**: Add Nginx for static files and load balancing
7. **Volumes**: Use named volumes or bind mounts for data persistence

## Contributing

1. Make your changes on a new branch based on `main`
2. Test locally with `docker compose up --build`
3. Ensure all containers start successfully
4. Submit a pull request

## Support

If you encounter issues:
1. Check the logs: `docker compose logs -f`
2. Verify environment variables in `.env`
3. Ensure Docker and Docker Compose are installed correctly
4. Check port availability: `ss -tlnp | grep 9050`