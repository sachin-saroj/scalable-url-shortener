"""Tests for Celery beat schedule configuration."""

from celery.schedules import crontab

from app.workers.celery_app import celery_app


class TestCeleryBeatSchedule:
    """Verify that all periodic tasks are correctly scheduled."""

    def test_beat_schedule_has_analytics_aggregation(self):
        schedule = celery_app.conf.beat_schedule
        assert "aggregate-daily-analytics" in schedule
        entry = schedule["aggregate-daily-analytics"]
        assert entry["task"] == "app.workers.tasks.aggregate_daily_analytics"
        assert isinstance(entry["schedule"], crontab)

    def test_beat_schedule_has_url_cleanup(self):
        schedule = celery_app.conf.beat_schedule
        assert "cleanup-expired-urls" in schedule
        entry = schedule["cleanup-expired-urls"]
        assert entry["task"] == "app.workers.tasks.cleanup_expired_urls"
        assert isinstance(entry["schedule"], crontab)

    def test_cleanup_runs_every_6_hours_not_15_minutes(self):
        """Verify cleanup interval is reasonable (6h, not 15m)."""
        schedule = celery_app.conf.beat_schedule
        entry = schedule["cleanup-expired-urls"]
        # Crontab hour="*/6" means every 6 hours
        assert entry["schedule"].hour == {0, 6, 12, 18}

    def test_beat_schedule_has_health_ping(self):
        schedule = celery_app.conf.beat_schedule
        assert "worker-health-ping" in schedule
        entry = schedule["worker-health-ping"]
        assert entry["task"] == "app.workers.tasks.worker_health_ping"
        assert isinstance(entry["schedule"], crontab)

    def test_all_scheduled_tasks_exist(self):
        """Verify that all scheduled task names map to real importable tasks."""
        schedule = celery_app.conf.beat_schedule
        expected_tasks = {
            "app.workers.tasks.aggregate_daily_analytics",
            "app.workers.tasks.cleanup_expired_urls",
            "app.workers.tasks.worker_health_ping",
        }
        actual_tasks = {entry["task"] for entry in schedule.values()}
        assert expected_tasks == actual_tasks
