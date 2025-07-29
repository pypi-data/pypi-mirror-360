
from patronx.config import BackupConfig


def test_from_env_uses_defaults(monkeypatch):
    for var in [
        "PGHOST",
        "PGPORT",
        "PGUSER",
        "PGPASSWORD",
        "PGDATABASE",
        "BACKUP_DIR",
        "BACKUP_CRON",
        "CLEANUP_CRON",
        "RETENTION_DAYS",
    ]:
        monkeypatch.delenv(var, raising=False)

    backup = BackupConfig.from_env()

    assert backup.host == "localhost"
    assert backup.port == 5432
    assert backup.user == "test_user"
    assert backup.password == "test_password"
    assert backup.database == "test_db"
    assert backup.backup_dir == "./backups"
    assert backup.backup_cron == "0 0 * * *"
    assert backup.cleanup_cron == "0 1 * * *"
    assert backup.retention_days == 30


def test_from_env_reads_values(monkeypatch):
    monkeypatch.setenv("PGHOST", "db")
    monkeypatch.setenv("PGPORT", "6543")
    monkeypatch.setenv("PGUSER", "patronx")
    monkeypatch.setenv("PGPASSWORD", "secret")
    monkeypatch.setenv("PGDATABASE", "mydb")
    monkeypatch.setenv("BACKUP_DIR", "/tmp")
    monkeypatch.setenv("BACKUP_CRON", "*/5 * * * *")
    monkeypatch.setenv("CLEANUP_CRON", "0 */6 * * *")
    monkeypatch.setenv("RETENTION_DAYS", "10")

    backup = BackupConfig.from_env()

    assert backup.host == "db"
    assert backup.port == 6543
    assert backup.user == "patronx"
    assert backup.password == "secret"
    assert backup.database == "mydb"
    assert backup.backup_dir == "/tmp"
    assert backup.backup_cron == "*/5 * * * *"
    assert backup.cleanup_cron == "0 */6 * * *"
    assert backup.retention_days == 10