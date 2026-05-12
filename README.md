# portfolio

Personal portfolio site (Flask backend + static frontend) with v2 as the default homepage.

## Stack

- Backend: Flask
- Frontend: HTML, CSS/SCSS, JavaScript
- Runtime server: Gunicorn
- Build/deploy target: Nixpacks

## Local Development

1. Create and activate virtual environment.
2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Create local env file:

```bash
cp .env.example .env
```

4. Run app:

```bash
python app.py
```

## Client Email Dashboard

Compose and send client emails from the built-in panel:

```bash
GET /dashboard/emails
```

Features:

- Client address book
- Draft save and load
- Send history
- HTML preview rendered with the same outgoing email template markup

Optional protection for dashboard routes:

- `DASHBOARD_USERNAME`
- `DASHBOARD_PASSWORD`

## Nixpacks Deployment

This repo includes `nixpacks.toml` with build/start commands.

Required environment variables:

- `FLASK_ENV=production`
- `SECRET_KEY`
- `DATABASE_PATH`
- `OWNER_EMAIL`
- `WEBSITE_URL`
- `RESEND_FROM_EMAIL`
- `RESEND_API_KEY`
- `TOOLS_CACHE_TTL`

Optional:

- `SMTP_SENDER` (fallback sender value)

Start command (from Nixpacks):

```bash
/opt/venv/bin/gunicorn --bind 0.0.0.0:${PORT:-5000} app:app
```

## Health Check

Endpoint:

```bash
GET /health
```

Expected response:

```json
{"status":"ok"}
```

## Email Deliverability Notes

For reliable inbox placement, verify SPF, DKIM, and DMARC for the sending domain used in `RESEND_FROM_EMAIL`.

## Smoke Test Checklist

1. Home (`/`) loads correctly.
2. Language switcher works on the homepage.
3. Contact form rejects invalid email input.
4. Contact form sends user + owner email on valid input.
5. Health endpoint returns HTTP 200.
