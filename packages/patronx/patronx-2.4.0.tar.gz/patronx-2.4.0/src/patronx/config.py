import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class BackupConfig:
    """Configuration for backing up a PostgreSQL database.

    Values are pulled from environment variables typically used by the
    ``pg_dump`` command. Default values mirror those used by the PostgreSQL
    client utilities when an environment variable is missing.
    """
    host: str = "localhost"
    port: int = 5432
    user: str = "test_user"
    password: Optional[str] = "test_password"
    database: str = "test_db"
    backup_dir: str = "./backups"
    s3_bucket: Optional[str] = None
    cleanup_cron: str = "0 1 * * *"
    retention_days: int = 30
    backup_cron: str = "0 0 * * *"
    redis_url: str = "redis://redis:6379/0"
    amqp_url: str = "amqp://guest:guest@rabbitmq:5672/"

    @classmethod
    def from_env(cls) -> "BackupConfig":
        """Create configuration from environment variables.

        The following variables are consulted:

        - ``PGHOST``: Database server host.
        - ``PGPORT``: Server port number. Defaults to ``5432``.
        - ``PGUSER``: Authentication user name. Defaults to ``postgres``.
        - ``PGPASSWORD``: Password for authentication. Optional.
        - ``PGDATABASE``: Name of the database to back up. Defaults to ``postgres``.
        - ``BACKUP_DIR``: Directory where the dump file should be placed. Defaults to the current directory.
        - ``BACKUP_CRON``: Cron schedule for periodic backups. Defaults to "0 0 * * *" (midnight daily).
        - ``CLEANUP_CRON``: Cron schedule for cleaning up old backups. Defaults to "0 1 * * *" (1 AM daily).
        - ``RETENTION_DAYS``: Number of days to keep backups. Defaults to ``30``.
        - ``S3_BUCKET``: Optional S3 bucket name for storing backups.
        """

        def getenv(key: str, default):
            return os.getenv(key, default)

        def getenv_int(key: str, default: int) -> int:
            value = os.getenv(key)
            try:
                return int(value) if value is not None else default
            except ValueError:
                return default

        return cls(
            host=getenv("PGHOST", cls.host),
            port=getenv_int("PGPORT", cls.port),
            user=getenv("PGUSER", cls.user),
            password=getenv("PGPASSWORD", cls.password),
            database=getenv("PGDATABASE", cls.database),
            backup_dir=getenv("BACKUP_DIR", cls.backup_dir),
            s3_bucket=getenv("S3_BUCKET", cls.s3_bucket),
            backup_cron=getenv("BACKUP_CRON", cls.backup_cron),
            cleanup_cron=getenv("CLEANUP_CRON", cls.cleanup_cron),
            retention_days=getenv_int("RETENTION_DAYS", cls.retention_days),
            redis_url=getenv("REDIS_URL", cls.redis_url),
            amqp_url=getenv("AMQP_URL", cls.amqp_url)
        )
