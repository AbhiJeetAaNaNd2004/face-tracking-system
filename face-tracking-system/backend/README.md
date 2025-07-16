# Face Tracking System Backend

## Setup

1. Clone the repo and navigate to backend:
   ```bash
   cd face-tracking-system/backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in your secrets:
   ```bash
   cp .env.example .env
   ```

## Running (Development)

```bash
cd app
uvicorn main:app --reload
```

## Running (Production)

- Use Uvicorn or Gunicorn with Uvicorn workers:

```bash
cd app
uvicorn main:app --host 0.0.0.0 --port 8000
# Or for multiple workers:
gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --workers 4
```

- Use a reverse proxy (Nginx/Apache) for HTTPS and static files.

## Environment Variables
- `SECRET_KEY`: JWT secret
- `DATABASE_URL`: PostgreSQL connection string
- `FRONTEND_URL`: Allowed CORS origin

## Health Check
- Visit `GET /` to check if the API is running.