import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import remoulade
from remoulade import Worker

import patronx.tasks  # noqa: F401  # ensure actors are declared
from patronx.logger import get_logger
from patronx.schedule import start_scheduler

logger = get_logger(__name__)

def start_health_server() -> None:
    """Expose a basic /health endpoint for container orchestration."""

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # type: ignore[override]
            if self.path in {"/", "/health", "/healthz"}:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_response(404)
                self.end_headers()

        def log_message(self, format: str, *args: object) -> None:  # noqa: D401
            return  # silence default logging

    port = int(os.getenv("HEALTH_PORT", "7775"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    logger.info("Health server listening on port %s", port)
    server.serve_forever()

def run_scheduler() -> None:
    logger.info("Starting scheduler")
    start_scheduler()

def run_worker() -> None:
    logger.info("Starting worker")
    worker = Worker(remoulade.get_broker())
    worker.start()
    worker.logger = logger


def run_worker_and_scheduler() -> None:
    health_thread = threading.Thread(
        target=start_health_server, name="health", daemon=True
    )
    health_thread.start()

    sched_thread = threading.Thread(
        target=run_scheduler, name="scheduler", daemon=True
    )
    sched_thread.start()

    # ensure the scheduler thread actually started
    time.sleep(0.01)
    if not sched_thread.is_alive():
        raise RuntimeError("Scheduler thread failed to start")

    if not health_thread.is_alive():
        raise RuntimeError("Health server failed to start")

    run_worker()
