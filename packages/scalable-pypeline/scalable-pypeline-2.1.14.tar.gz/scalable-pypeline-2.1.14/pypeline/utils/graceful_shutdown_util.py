import threading
import signal
import os
import redis
import socket
import sys
import time
import logging
from pypeline.pipelines.middleware.graceful_shutdown_middleware import (
    GraceFulShutdownMiddleware,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def enable_graceful_shutdown(broker, redis_url):
    """Attach GracefulShutdownMiddleware and a SIGTERM handler to the current process."""
    broker.add_middleware(GraceFulShutdownMiddleware(redis_url=redis_url))

    if threading.current_thread().name == "MainThread":
        key_prefix = "busy"
        hostname = socket.gethostname()
        pid = os.getpid()
        busy_key = f"{key_prefix}:{hostname}-{pid}"
        r = redis.Redis.from_url(redis_url)

        def shutdown_handler(signum, frame):
            logger.info(f"[Signal Handler] Received signal {signum}")
            while r.get(busy_key):
                logger.info(f"[Signal Handler] Busy ({busy_key}), waiting...")
                time.sleep(30)
            logger.info(f"[Signal Handler] Done. Exiting.")
            sys.exit(0)

        signal.signal(signal.SIGTERM, shutdown_handler)
