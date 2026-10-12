# django-htmx-sse

A Django project exploring HTMX Server-Sent Events (SSE) with Tailwind CSS, running in Docker.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

No local Python or Node.js installation is required.

## Quick start

1. **Create the environment file**:

   ```bash
   cp .env.example .env
   ```

   Or create `.env` manually:

   ```bash
   DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
   PYTHONUNBUFFERED=1
   ```

   Generate a secure secret key:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

2. **Build and start the services**:

   ```bash
   docker compose up --build
   ```

3. **Open the app**:

   - Django app: http://localhost:8000
   - Tailwind watcher runs alongside Django and rebuilds CSS automatically.

## Services

The project runs two containers:

| Service | Purpose | Command |
|--------|---------|---------|
| `web` | Django development server | `poetry run python manage.py runserver 0.0.0.0:8000` |
| `tailwind` | Tailwind CSS watcher | `npm run dev` in `theme/static_src` |

## Useful commands

Run Django management commands:

```bash
docker compose run --rm web poetry run python manage.py <command>
```

Examples:

```bash
docker compose run --rm web poetry run python manage.py migrate
docker compose run --rm web poetry run python manage.py createsuperuser
docker compose run --rm web poetry run python manage.py collectstatic
```

View logs:

```bash
docker compose logs -f
```

Stop everything:

```bash
docker compose down
```

Remove containers and volumes (useful if `node_modules` gets into a bad state):

```bash
docker compose down -v
```

## Notes

- The `node_modules` directory is managed as a Docker named volume so the Linux-native Tailwind binaries stay inside the container, even when your local `theme/` directory is mounted from macOS.
- The `.env` file is ignored by Git (see `.gitignore`). It is loaded by `docker-compose.yml` via `env_file: .env`.
- The Dockerfile defaults to `poetry run python manage.py tailwind start`, but `docker-compose.yml` overrides this to run Django and Tailwind as separate services.
