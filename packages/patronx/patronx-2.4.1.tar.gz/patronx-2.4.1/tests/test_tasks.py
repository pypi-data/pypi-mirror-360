import importlib
import os
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace

import pytest


def _load_tasks(monkeypatch: pytest.MonkeyPatch, backup_dir: Path):
    monkeypatch.setenv("BACKUP_DIR", str(backup_dir))
    monkeypatch.setenv("POSTGRES_DB", "testdb")
    monkeypatch.setenv("RETENTION_DAYS", "30")

    tasks = importlib.import_module("patronx.tasks")
    importlib.reload(tasks)

    DummyCfg = SimpleNamespace(
        backup_dir=str(backup_dir),
        database="testdb",
        retention_days=30,
        from_env=lambda: SimpleNamespace(
            backup_dir=str(backup_dir),
            database="testdb",
            retention_days=30,
        ),
    )
    monkeypatch.setattr(tasks, "BackupConfig", DummyCfg, raising=False)

    def fake_run_backup(cfg, dst, plain=False, show_progress=False):  # noqa: D401
        """Pretend pg_dump by just creating an empty file."""
        Path(dst).touch()

    monkeypatch.setattr(tasks, "run_backup", fake_run_backup, raising=False)

    return tasks


def test_run_backup_job_creates_backup(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    tasks = _load_tasks(monkeypatch, tmp_path)
    fixed_now = tasks.datetime(2024, 2, 3, 4, 5, 6)

    class DummyDatetime(tasks.datetime):
        @classmethod
        def utcnow(cls):  # type: ignore[override]
            return fixed_now

    monkeypatch.setattr(tasks, "datetime", DummyDatetime)

    result = tasks.run_backup_job(show_progress=False)

    expected = tmp_path / "testdb-20240203-040506.dump"
    assert result == str(expected)
    assert expected.exists()


def test_run_backup_job_skips_existing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    tasks = _load_tasks(monkeypatch, tmp_path)
    fixed_now = tasks.datetime(2024, 2, 3, 4, 5, 6)

    class DummyDatetime(tasks.datetime):
        @classmethod
        def utcnow(cls):  # type: ignore[override]
            return fixed_now

    monkeypatch.setattr(tasks, "datetime", DummyDatetime)

    existing = tmp_path / "testdb-20240203-000000.dump"
    existing.touch()

    called: list[bool] = []

    def fake_run_backup(*args, **kwargs):
        called.append(True)

    monkeypatch.setattr(tasks, "run_backup", fake_run_backup, raising=False)

    result = tasks.run_backup_job(show_progress=False)

    assert result == str(existing)
    assert called == []

def test_cleanup_old_backups(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    tasks = _load_tasks(monkeypatch, tmp_path)

    old_file = tmp_path / "old.dump"
    old_file.touch()
    # modify mtime to 40 days ago
    old_ts = datetime.utcnow() - timedelta(days=40)
    os.utime(old_file, (old_ts.timestamp(), old_ts.timestamp()))

    new_file = tmp_path / "new.dump"
    new_file.touch()

    removed = tasks.cleanup_old_backups()

    assert removed == 1
    assert not old_file.exists()
    assert new_file.exists()