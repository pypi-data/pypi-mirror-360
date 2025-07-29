import time

from click.testing import CliRunner

from patronx import __version__, cli, schedule
from patronx.cli import main


def test_main_prints_message():
    runner = CliRunner()
    result = runner.invoke(main)
    assert result.exit_code == 0
    assert "PatronX CLI invoked" in result.output


def test_cli_version_option():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_check_db_success(monkeypatch):
    def fake_connect(**kwargs):
        class FakeConn:
            def close(self):
                pass

        return FakeConn()

    monkeypatch.setattr(cli.psycopg2, "connect", fake_connect)

    runner = CliRunner()
    result = runner.invoke(main, ["check-db"])

    assert result.exit_code == 0
    assert "Database connection successful" in result.output


def test_diff_cmd(monkeypatch):
    monkeypatch.setattr(cli, "diff_last_backup", lambda cfg: "diff")
    runner = CliRunner()
    result = runner.invoke(main, ["diff"])
    assert result.exit_code == 0
    assert "diff" in result.output


def test_list_backups_missing_dir(tmp_path, monkeypatch):
    missing = tmp_path / "missing"
    monkeypatch.setenv("BACKUP_DIR", str(missing))
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_list_backups_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "No backups found" in result.output


def test_list_backups(tmp_path, monkeypatch):
    f1 = tmp_path / "a.dump"
    f1.write_text("1")
    time.sleep(0.01)
    f2 = tmp_path / "b.dump"
    f2.write_text("2")
    monkeypatch.setenv("BACKUP_DIR", str(tmp_path))
    runner = CliRunner()
    result = runner.invoke(main, ["list"])
    assert result.exit_code == 0
    assert "a.dump" in result.output
    assert "b.dump" in result.output


def test_diff_cmd_failure(monkeypatch):
    def boom(cfg):
        raise FileNotFoundError("none")
    monkeypatch.setattr("patronx.cli.diff_last_backup", boom)
    runner = CliRunner()
    result = runner.invoke(main, ["diff"])
    assert result.exit_code == 1
    assert "none" in result.output


def test_enqueue_backup(monkeypatch):
    called = []

    def fake_send():
        called.append(True)
        return "backup-queued"

    monkeypatch.setattr(cli.run_backup_job, "send", fake_send)
    runner = CliRunner()
    result = runner.invoke(main, ["enqueue-backup"])
    assert result.exit_code == 0
    assert called == [True]
    assert "backup-queued" in result.output


def test_enqueue_cleanup(monkeypatch):
    called = []

    def fake_send():
        called.append(True)
        return "cleanup-queued"

    monkeypatch.setattr(cli.cleanup_old_backups, "send", fake_send)
    runner = CliRunner()
    result = runner.invoke(main, ["enqueue-cleanup"])
    assert result.exit_code == 0
    assert called == [True]
    assert "cleanup-queued" in result.output


def test_list_schedule(monkeypatch):
    fake_jobs = [
        schedule.ScheduledJob(actor_name="run_backup_job", interval=60, last_queued=schedule.datetime(2024, 1, 1)),
        schedule.ScheduledJob(actor_name="cleanup_old_backups", interval=120, last_queued=schedule.datetime(2024, 1, 1)),
    ]

    monkeypatch.setattr(schedule, "init_scheduled_jobs", lambda b, c: fake_jobs)
    runner = CliRunner()
    result = runner.invoke(main, ["list-schedule"])
    assert result.exit_code == 0
    assert "run_backup_job" in result.output
    assert "cleanup_old_backups" in result.output
