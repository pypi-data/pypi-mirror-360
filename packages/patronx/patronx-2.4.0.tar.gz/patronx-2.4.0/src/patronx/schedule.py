from datetime import datetime, timedelta, timezone
from typing import cast

import redis
import remoulade
from croniter import croniter
from remoulade.scheduler import ScheduledJob, Scheduler

from patronx.config import BackupConfig
from patronx.logger import get_logger

logger = get_logger(__name__)

def _interval_from_cron(expr: str) -> int:
    """Compute seconds between two consecutive cron occurrences."""

    now = datetime.now(timezone.utc)
    itr = croniter(expr, now)
    first = cast(datetime, itr.get_next(datetime))
    second = cast(datetime, itr.get_next(datetime))
    return int((second - first).total_seconds()) or 1


def _job_from_cron(expr: str, actor_name: str) -> ScheduledJob:
    """Return a ``ScheduledJob`` configured from a cron expression."""

    now = datetime.utcnow()
    itr = croniter(expr, now)
    next_run = itr.get_next(datetime)
    interval = _interval_from_cron(expr)
    # schedule first run at ``next_run`` by setting last_queued ``interval``
    # seconds before that moment
    last_queued = next_run - timedelta(seconds=interval)

    return ScheduledJob(
        actor_name=actor_name,
        interval=interval,
        last_queued=last_queued,
    )


def init_scheduled_jobs(backup_cron: str, cleanup_cron: str) -> list[ScheduledJob]:
    return [
        _job_from_cron(backup_cron, "run_backup_job"),
        _job_from_cron(cleanup_cron, "cleanup_old_backups"),
    ]

def start_scheduler() -> None:
    """Start a scheduler with backup and cleanup jobs."""
    config = BackupConfig.from_env()
    redis_client = redis.from_url(config.redis_url)
    #  Prevent duplicate jobs on container restart
    for job in redis_client.hvals("remoulade:schedule"):
        # each job is a pickled ScheduledJob; quickest check is actor name
        if b"run_backup_job" in job or b"cleanup_old_backups" in job:
            redis_client.hdel(
                "remoulade:schedule",  # type: ignore[arg-type]
                cast(bytes, job)[:40],  # first 40 bytes → key
            )

    scheduler = Scheduler(
        broker=remoulade.get_broker(),
        client=redis_client,
        schedule=init_scheduled_jobs(config.backup_cron, config.cleanup_cron),
    )

    scheduler.logger = logger
    remoulade.set_scheduler(scheduler)
    logger.info("Starting scheduler")
    remoulade.get_scheduler().start()
    logger.info("Scheduler stopped")