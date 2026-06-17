"""
Celery Application
───────────────────
Background task queue configuration.

WHY Celery?
- Battle-tested distributed task queue
- Redis as broker (already in our stack)
- Supports periodic tasks (Celery Beat)
- Handles retries, error recovery, concurrency

TASKS:
1. Record click analytics (high frequency)
2. Aggregate daily analytics (periodic)
3. Clean up expired URLs (periodic)
"""

from celery import Celery
from celery.schedules import crontab
from celery.signals import setup_logging

from app.config import get_settings

settings = get_settings()

celery_app = Celery(  # type: ignore[no-untyped-call]
    "url_shortener",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# ── Celery Configuration ──────────────────────────────
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,  # Acknowledge after task completes (at-least-once)
    worker_prefetch_multiplier=1,  # Don't prefetch too many tasks
    result_expires=3600,  # Results expire after 1 hour
)

# ── Periodic Tasks (Celery Beat) ──────────────────────
celery_app.conf.beat_schedule = {
    # Aggregate daily analytics every hour
    "aggregate-daily-analytics": {
        "task": "app.workers.tasks.aggregate_daily_analytics",
        "schedule": crontab(minute="0"),  # Every hour, at :00
    },
    # Clean up expired URLs every 6 hours
    # URL expiry is hour-granularity, so 15-minute checks are excessive.
    # Running every 6 hours balances timeliness with resource efficiency.
    "cleanup-expired-urls": {
        "task": "app.workers.tasks.cleanup_expired_urls",
        "schedule": crontab(minute="0", hour="*/6"),  # Every 6 hours
    },
    # Worker health ping — verifies the task pipeline is functioning.
    # Logs a heartbeat every 30 minutes for monitoring systems to track.
    "worker-health-ping": {
        "task": "app.workers.tasks.worker_health_ping",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.workers"])  # type: ignore[no-untyped-call]


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from app.config import get_settings
    from app.utils.logging import configure_logging

    settings = get_settings()
    configure_logging(env=settings.APP_ENV, debug=settings.APP_DEBUG)
