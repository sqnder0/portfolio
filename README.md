# portfolio

### description:
These are the source files for my personal portfolio site.

### Technical details
**Frontend:** html, css, sass, js\
**Backend:** Flask, SQLite3

## Local development

1. Create and activate your virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create env file from template:

```bash
cp .env.example .env
```

4. Start app:

```bash
python app.py
```

5. Optional CSS rebuild:

```bash
npm install
npm run build:css
```

## Production configuration

Set these environment variables in production:

- SECRET_KEY
- FLASK_ENV=production
- DATABASE_PATH
- OWNER_EMAIL
- SMTP_HOST
- SMTP_PORT
- SMTP_SENDER
- SMTP_PASSWORD
- TOOLS_CACHE_TTL

## Health check

Use the health endpoint for runtime checks:

```bash
curl http://localhost:5000/health
```

Expected response:

```json
{"status":"ok"}
```

## Dockploy deployment

This repo includes a Dockerfile that starts the app with Gunicorn.

1. Create a new app in Dockploy from this repository.
2. Set build context to project root.
3. Expose container port 5000.
4. Add required environment variables from the list above.
5. Deploy and verify:

```bash
curl https://your-domain/health
```

## Docker Compose

Use compose for local containerized runs:

```bash
docker compose up --build -d
```

Stop the stack:

```bash
docker compose down
```

Inspect logs:

```bash
docker compose logs -f web
```

### Common Dokploy image error

If Dokploy shows `No such image: ...:latest`, it is usually trying to start a container before a successful build was produced.

Fix checklist:

1. In Dokploy, ensure deployment type is Compose/Repository build (not prebuilt image only).
2. Redeploy with build enabled and no cached failed deployment.
3. Confirm service name is `web` (from [docker-compose.yml](docker-compose.yml)).
4. If Dokploy asks for image variable, set `APP_IMAGE=portfolio-web:latest`.
5. Re-run deployment and verify [health endpoint](README.md#health-check).

## Smoke test checklist

1. Homepage loads and tool cards render.
2. Invalid contact email returns validation error.
3. Valid contact submission returns success message.
4. App logs do not show unhandled exceptions.



 
