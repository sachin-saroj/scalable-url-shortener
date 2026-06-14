"""
Celery Tasks
─────────────
Background tasks for analytics aggregation and URL cleanup.

DESIGN:
- Each task is idempotent (safe to retry)
- Tasks use synchronous DB connections (Celery workers are sync)
- Exceptions are logged but don't crash the worker
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()

# Synchronous engine for Celery (workers run sync code)
sync_engine = create_engine(settings.SYNC_DATABASE_URL, pool_size=5)
SyncSession = sessionmaker(bind=sync_engine)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[no-untyped-call]
def aggregate_daily_analytics(self):
    """
    Aggregate click data into daily_analytics table.

    WHY?
    - COUNT(*) on clicks table gets slower as data grows
    - Pre-aggregation makes analytics API O(1) instead of O(n)
    - Runs hourly, so data is at most 1 hour stale
    """
    try:
        session = SyncSession()
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).date()

        # Aggregate clicks grouped by url_id and date
        result = session.execute(
            text("""
            INSERT INTO daily_analytics (url_id, date, total_clicks, unique_clicks)
            SELECT
                url_id,
                DATE(clicked_at) as click_date,
                COUNT(*) as total,
                COUNT(DISTINCT ip_address) as unique_ips
            FROM clicks
            WHERE DATE(clicked_at) = :target_date
            GROUP BY url_id, DATE(clicked_at)
            ON CONFLICT (url_id, date)
            DO UPDATE SET
                total_clicks = EXCLUDED.total_clicks,
                unique_clicks = EXCLUDED.unique_clicks
        """),
            {"target_date": yesterday},
        )

        session.commit()
        rowcount = getattr(result, "rowcount", 0)
        logger.info(f"Daily analytics aggregated for {yesterday}: {rowcount} records")
        session.close()

    except Exception as e:
        logger.error(f"Analytics aggregation failed: {e}")
        raise self.retry(exc=e) from e


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)  # type: ignore[no-untyped-call]
def cleanup_expired_urls(self):
    """
    Deactivate expired URLs and remove them from cache.

    WHY deactivate instead of delete?
    - Preserves analytics data
    - Audit trail
    - Can be reactivated if needed

    PERFORMANCE:
    - Uses partial index on expires_at (only scans active URLs with expiry)
    """
    try:
        session = SyncSession()
        now = datetime.now(timezone.utc)

        # Deactivate expired URLs
        result = session.execute(
            text("""
            UPDATE urls
            SET is_active = false
            WHERE expires_at IS NOT NULL
              AND expires_at <= :now
              AND is_active = true
            RETURNING short_code, custom_alias
        """),
            {"now": now},
        )

        deactivated = result.fetchall()
        session.commit()

        # Clear cache for deactivated URLs
        if deactivated:
            import redis as sync_redis

            r = sync_redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
            )
            for row in deactivated:
                code = row[1] or row[0]  # custom_alias or short_code
                if code:
                    r.delete(f"url:{code}")
            r.close()

        logger.info(f"Cleaned up {len(deactivated)} expired URLs")
        session.close()

    except Exception as e:
        logger.error(f"URL cleanup failed: {e}")
        raise self.retry(exc=e) from e
