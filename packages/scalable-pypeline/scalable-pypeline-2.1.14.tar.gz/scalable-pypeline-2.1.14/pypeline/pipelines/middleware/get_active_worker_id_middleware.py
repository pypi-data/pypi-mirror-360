import contextvars
from dramatiq import Middleware


class GetActiveWorkerIdMiddleware(Middleware):
    _ACTIVE_WORKER_ID: contextvars.ContextVar["Optional[Message[Any]]"] = (
        contextvars.ContextVar("_ACTIVE_WORKER_ID", default=None)
    )

    @classmethod
    def get_active_worker_id(cls):
        return cls._ACTIVE_WORKER_ID.get()

    def before_process_message(self, broker, message):
        """Sets the active worker ID, verifying broker has a broker_id first."""
        broker_id = getattr(broker, "broker_id", None)
        if not broker_id:
            return
        self._ACTIVE_WORKER_ID.set(broker_id)

    def after_process_message(self, broker, message, *, result=None, exception=None):
        self._ACTIVE_WORKER_ID.set(None)
