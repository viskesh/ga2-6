import time
import uuid
import threading
from collections import deque
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse

# ---------------------------------------------------------------------------
# Config — CHANGE THIS to your own registered email before deploying
# ---------------------------------------------------------------------------
STUDENT_EMAIL = "24f3002870@ds.study.iitm.ac.in"

app = FastAPI()

START_TIME = time.time()

# Thread-safe counter for total requests (any endpoint)
_counter_lock = threading.Lock()
request_count = 0

# Ring buffer of recent structured log entries (in-memory)
LOG_MAX = 1000
log_buffer = deque(maxlen=LOG_MAX)
_log_lock = threading.Lock()


def add_log_entry(level: str, path: str, request_id: str, **extra):
    entry = {
        "level": level,
        "ts": time.time(),
        "path": path,
        "request_id": request_id,
    }
    entry.update(extra)
    with _log_lock:
        log_buffer.append(entry)


# ---------------------------------------------------------------------------
# Middleware: increments the counter and logs every request to every endpoint
# ---------------------------------------------------------------------------
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    global request_count

    request_id = str(uuid.uuid4())
    path = request.url.path

    with _counter_lock:
        request_count += 1

    response = await call_next(request)

    add_log_entry(
        level="info",
        path=path,
        request_id=request_id,
        method=request.method,
        status_code=response.status_code,
    )

    return response


# ---------------------------------------------------------------------------
# GET /work?n=K
# ---------------------------------------------------------------------------
@app.get("/work")
async def work(n: int = 1):
    k = max(0, n)
    total = 0
    for i in range(k):
        total += i  # trivial busy work
    return {"email": STUDENT_EMAIL, "done": k}


# ---------------------------------------------------------------------------
# GET /metrics — Prometheus text exposition format
# ---------------------------------------------------------------------------
@app.get("/metrics")
async def metrics():
    with _counter_lock:
        count = request_count
    body = (
        "# HELP http_requests_total Total number of HTTP requests received.\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {count}\n"
    )
    return PlainTextResponse(content=body, media_type="text/plain; version=0.0.4")


# ---------------------------------------------------------------------------
# GET /healthz
# ---------------------------------------------------------------------------
@app.get("/healthz")
async def healthz():
    uptime = max(0.0, time.time() - START_TIME)
    return {"status": "ok", "uptime_s": uptime}


# ---------------------------------------------------------------------------
# GET /logs/tail?limit=N
# ---------------------------------------------------------------------------
@app.get("/logs/tail")
async def logs_tail(limit: int = 10):
    n = max(0, limit)
    with _log_lock:
        entries = list(log_buffer)[-n:] if n > 0 else []
    return JSONResponse(content=entries)
