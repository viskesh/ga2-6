import time
import uuid
import threading
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

# ── Startup time ────────────────────────────────────────────────────────────
START_TIME = time.time()

# ── Shared state (thread-safe) ───────────────────────────────────────────────
_counter_lock = threading.Lock()
_request_counter: int = 0

_log_lock = threading.Lock()
_log_buffer: deque = deque(maxlen=10_000)

app = FastAPI(title="Observable API")


# ── Middleware: count every request + structured log ─────────────────────────
@app.middleware("http")
async def observe(request: Request, call_next):
    global _request_counter
    request_id = str(uuid.uuid4())
    path = request.url.path  # e.g. /work  (no query string)

    # Increment counter
    with _counter_lock:
        _request_counter += 1

    # Buffer structured log entry
    entry = {
        "level": "info",
        "ts": time.time(),
        "path": path,
        "request_id": request_id,
    }
    with _log_lock:
        _log_buffer.append(entry)

    response = await call_next(request)
    return response


# ── GET /work?n=K ────────────────────────────────────────────────────────────
@app.get("/work")
async def work(n: int = 1):
    """Do K units of work and return confirmation."""
    return {"email": "your@email.com", "done": n}


# ── GET /metrics ─────────────────────────────────────────────────────────────
@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    """Prometheus text exposition format."""
    with _counter_lock:
        count = _request_counter
    body = (
        "# HELP http_requests_total Total number of HTTP requests received\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {count}\n"
    )
    return PlainTextResponse(content=body, media_type="text/plain; version=0.0.4")


# ── GET /healthz ─────────────────────────────────────────────────────────────
@app.get("/healthz")
async def healthz():
    """Health check with uptime."""
    return {"status": "ok", "uptime_s": round(time.time() - START_TIME, 4)}


# ── GET /logs/tail?limit=N ───────────────────────────────────────────────────
@app.get("/logs/tail")
async def logs_tail(limit: int = 20):
    """Return the last N structured log entries."""
    with _log_lock:
        entries = list(_log_buffer)[-limit:]
    return entries
