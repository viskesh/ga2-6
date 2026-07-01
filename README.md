# Observable FastAPI Service

Implements all four grader-required endpoints:

| Endpoint | Description |
|---|---|
| `GET /work?n=K` | Returns `{"email":"...", "done": K}` and increments counter |
| `GET /metrics` | Live Prometheus counter `http_requests_total` |
| `GET /healthz` | `{"status":"ok", "uptime_s": <float>}` |
| `GET /logs/tail?limit=N` | Last N log entries (level, ts, path, request_id) |

---

## ⚡ Deploy on Railway (easiest, free tier available)

1. Push this folder to a **GitHub repo**.
2. Go to [railway.app](https://railway.app) → **New Project → Deploy from GitHub repo**.
3. Select your repo — Railway auto-detects the `Procfile` or `Dockerfile`.
4. Under **Settings → Networking → Generate Domain** to get a public URL.
5. Paste that URL into the grader.

> Make sure to set `your@email.com` in `main.py` to your real email first!

---

## ⚡ Deploy on Render (free tier available)

1. Push to GitHub.
2. [render.com](https://render.com) → **New Web Service** → connect repo.
3. Runtime: **Python 3**, Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Deploy — get your `.onrender.com` URL.

---

## ⚡ Deploy on Fly.io

```bash
fly launch          # detects Dockerfile, prompts for app name
fly deploy
fly open /healthz   # verify
```

---

## Local test

```bash
pip install -r requirements.txt
uvicorn main:app --reload

# In another terminal:
curl http://localhost:8000/healthz
curl "http://localhost:8000/work?n=5"
curl http://localhost:8000/metrics
curl "http://localhost:8000/logs/tail?limit=5"
```
