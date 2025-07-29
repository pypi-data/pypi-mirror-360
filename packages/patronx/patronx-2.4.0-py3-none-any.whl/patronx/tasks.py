import os
from datetime import datetime, timedelta
from pathlib import Path

import remoulade
from remoulade import actor
from remoulade.brokers.rabbitmq import RabbitmqBroker

from patronx.backup import run_backup
from patronx.config import BackupConfig
from patronx.logger import get_logger

BROKER_URL = os.getenv("AMQP_URL", "amqp://guest:guest@localhost:5672/")
broker = RabbitmqBroker(url=BROKER_URL)
remoulade.set_broker(broker)

logger = get_logger(__name__)
# ensure all actors defined below are associated with the broker

def _backup_path(cfg: BackupConfig) -> Path:
    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    path = Path(cfg.backup_dir) / f"{cfg.database}-{stamp}.dump"
    logger.info("Computed backup path %s", path)
    return path


@actor(
    queue_name="backups",
    max_retries=5,
)
def run_backup_job(*, show_progress: bool = False) -> str:

    logger.info("Starting backup job (show_progress=%s)", show_progress)
    cfg = BackupConfig.from_env()
    dst = _backup_path(cfg)
    # Check if a backup for today already exists
    today = datetime.utcnow().strftime("%Y%m%d")
    pattern = f"{cfg.database}-{today}-*.dump"
    existing = sorted(Path(cfg.backup_dir).glob(pattern))

    if existing:
        logger.warning(
            "A backup for %s already exists – skipping new backup: %s",
            today,
            existing[-1],
        )
        return str(existing[-1])




    logger.info("Backup destination: %s", dst.resolve())
    dst.parent.mkdir(parents=True, exist_ok=True)
    if not dst.parent.exists():
        logger.error("Failed to create backup directory %s", dst.parent)
        raise FileNotFoundError(dst.parent)
    logger.debug("Backup directory exists: %s", dst.parent)
    run_backup(cfg, dst, show_progress=show_progress)
    logger.info("Backup completed: %s (%s MiB)", dst, dst.stat().st_size / 1_048_576)
    return str(dst)

# Cleanup tasks
@actor(queue_name="cleanup", max_retries=1)
def cleanup_old_backups() -> int:
    """Remove backup files older than the configured retention period."""
    cfg = BackupConfig.from_env()
    cutoff = datetime.utcnow() - timedelta(days=cfg.retention_days)
    removed = 0
    backup_dir = Path(cfg.backup_dir)

    for path in backup_dir.glob("*.dump"):
        try:
            if path.stat().st_mtime < cutoff.timestamp():
                path.unlink()
                removed += 1
                logger.debug("Removed old backup: %s", path)
        except FileNotFoundError:
            logger.warning("Backup file %s disappeared before it could be deleted", path)
        except Exception as e:
            logger.error("Failed to remove backup file %s: %s", path, e, exc_info=True)

    logger.info("Removed %d old backups", removed)
    return removed

# register the actor so `.send()` can use the configured broker
remoulade.declare_actors([run_backup_job, cleanup_old_backups])