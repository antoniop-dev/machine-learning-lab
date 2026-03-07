# MachineInnovatorsInc Frontend

React + Vite frontend for the sentiment analysis application.

## What this app does

- collects user text input
- calls backend endpoint `POST /api/v1/predict`
- renders predicted label and class confidence scores

## Local development

From this `frontend/` directory:

```bash
npm install
npm run dev
```

Default dev URL:
- `http://localhost:5173`

In development, Vite proxies `/api/*` to:
- `http://localhost:8000`

So make sure the backend is running.

## Build and preview

```bash
npm run build
npm run preview
```

## API base URL

Runtime API base is read from:
- `VITE_API_BASE_URL`

Default value is:
- `/api/v1`

## Dockerized frontend

This folder includes:
- `Dockerfile` (multi-stage: Node build + Nginx serve)
- `nginx.conf` (SPA routing + `/api/` reverse proxy to `backend:8000`)

The recommended way to run it is from project root via Docker Compose:

```bash
docker compose up --build
```

Then open:
- `http://localhost:8080`
