import os
import socket
import logging
import redis

from dramatiq.middleware import Middleware
from tenacity import retry, stop_after_attempt, wait_exponential, after_log

logger = logging.getLogger(__name__)


class GraceFulShutdownMiddleware(Middleware):
    def __init__(self, redis_url, key_prefix="busy"):
        self.redis = redis.Redis.from_url(redis_url)
        self.hostname = socket.gethostname()
        self.pid = os.getpid()
        self.key_prefix = key_prefix
        self.key = f"{self.key_prefix}:{self.hostname}-{self.pid}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        after=after_log(logger, logging.WARNING),
        reraise=True,
    )
    def _set_busy_flag(self, message_ttl):
        self.redis.set(self.key, "1", ex=message_ttl)
        logger.debug(f"[GracefulShutdownMiddleware] Set busy flag: {self.key}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=2, max=10),
        after=after_log(logger, logging.WARNING),
        reraise=True,
    )
    def _clear_busy_flag(self):
        self.redis.delete(self.key)
        logger.debug(f"[GracefulShutdownMiddleware] Cleared busy flag: {self.key}")

    def before_process_message(self, broker, message):
        try:
            self._set_busy_flag(message_ttl=message.options["task_ttl"])
        except Exception as e:
            logger.error(f"[GracefulShutdownMiddleware] Failed to set busy flag: {e}")

    def after_process_message(self, broker, message, *, result=None, exception=None):
        try:
            self._clear_busy_flag()
        except Exception as e:
            logger.error(f"[GracefulShutdownMiddleware] Failed to clear busy flag: {e}")
