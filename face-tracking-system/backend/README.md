# Face Tracking System – Backend

This directory contains the FastAPI backend powering the **Face-Tracking System**.  
The service provides REST endpoints for authentication, MJPEG camera streaming, employee CRUD operations, face-embedding management, and attendance tracking.

---

## 1. Prerequisites

* Python ≥ 3.10 (recommended 3.11)
* PostgreSQL ≥ 13
* (Optional) CUDA-capable GPU and the required drivers if you plan to run the realtime face-tracking pipeline on GPU.

---

## 2. Installation (development)

```bash
# 1. Create and activate virtual-env
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env template and edit values
cp .env.sample .env  # then change SECRET_KEY / DB credentials

# 4. Create DB schema (one-off)
python -c "from db import create_tables; create_tables()"
```

---

## 3. Running locally

```bash
# From inside face-tracking-system/backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/docs for the interactive Swagger UI.

---

## 4. Production deployment

You have several options depending on your internal infrastructure:

### a) systemd service (bare-metal / VM)

1. Create dedicated *system* user `fts`.
2. Place project code under `/srv/face-tracking-system` (or similar).
3. Create `.env` file with production secrets (**never** commit real secrets):
   ```
   SECRET_KEY=super-long-random-string
   DB_HOST=10.0.0.5
   DB_PORT=5432
   DB_NAME=face_tracking
   DB_USER=fts
   DB_PASSWORD=s3cR3t
   ```
4. Create virtual-env, install requirements (same as dev).
5. Add `fts.service` under `/etc/systemd/system/`:
   ```ini
   [Unit]
   Description=Face Tracking System API
   After=network.target

   [Service]
   User=fts
   Group=fts
   WorkingDirectory=/srv/face-tracking-system/backend
   EnvironmentFile=/srv/face-tracking-system/backend/.env
   ExecStart=/srv/face-tracking-system/backend/.venv/bin/uvicorn app.main:app \
            --host 0.0.0.0 --port 9000 --workers 4
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```
6. Reload & start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable fts --now
   ```

### b) Docker (compose)

A full `docker-compose.yml` is provided at the repo root so you can launch **PostgreSQL + backend + frontend** with one command:

```bash
# At repo root
docker compose up -d --build
```

> Adjust environment variables in `docker-compose.yml` if necessary (e.g., GPU or port mapping).

---

## 5. Common pitfalls

* **Import errors** – Make sure you always run code from the `backend` root so the `app`, `core`, and `db` packages resolve correctly.
* **SECRET_KEY missing** – The server refuses to start if the `SECRET_KEY` is not set in environment.
* **Database connectivity** – Verify that PostgreSQL is reachable and that credentials match the `.env` file.
* **MJPEG bandwidth** – `streaming.py` does no per-client rate-limiting; tune or sit behind an Nginx reverse proxy if you expect many simultaneous viewers.

---

## 6. API quick reference

* `POST /auth/login/` – Obtain JWT access token.
* `GET  /stream/{camera_id}` – MJPEG live feed.
* `POST /embeddings/enroll/` – Bulk enrol one employee from several images (admin).
* `POST /embeddings/add/` – Add single embedding (admin).
* `DELETE /embeddings/delete_all/{employee_id}` – Remove all embeddings (admin).
* `GET /employees/` / `/employees/{id}` – CRUD employee records.
* `GET /attendance/` – Latest attendance records.

Full auto-generated docs available at `/docs`.