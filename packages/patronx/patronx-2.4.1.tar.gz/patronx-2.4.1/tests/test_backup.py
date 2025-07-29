import io
from types import SimpleNamespace

import pytest

from patronx.backup import _db_size, _upload_to_s3, diff_last_backup, run_backup
from patronx.config import BackupConfig


def test_diff_last_backup_no_files(tmp_path):
    cfg = BackupConfig(backup_dir=str(tmp_path))
    with pytest.raises(FileNotFoundError):
        diff_last_backup(cfg)


def test_diff_last_backup(tmp_path, monkeypatch):
    cfg = BackupConfig(backup_dir=str(tmp_path), password=None)
    dump = tmp_path / "a.dump"
    dump.write_text("line1\nline2\n")

    def fake_run(cmd, stdout, stderr, text, env):
        return SimpleNamespace(returncode=0, stdout="line1\nline2b\n")

    monkeypatch.setattr("patronx.backup.sp.run", fake_run)
    out = diff_last_backup(cfg)
    assert "-line2" in out
    assert "+line2b" in out


def test_db_size_failure(monkeypatch):
    def boom(**kw):
        raise Exception("fail")
    monkeypatch.setattr("patronx.backup.psycopg2.connect", boom)
    cfg = BackupConfig()
    assert _db_size(cfg) is None


def test_upload_to_s3(monkeypatch, tmp_path):
    called = {}

    class FakeStore:
        def upload_file(self, file, bucket, key):
            called["args"] = (file, bucket, key)

    monkeypatch.setattr(
        "patronx.backup.AWSAssetStore", SimpleNamespace(from_env=lambda: FakeStore())
    )

    f = tmp_path / "x"
    f.write_text("hi")
    _upload_to_s3(f, "b", "k")

    assert called["args"] == (f, "b", "k")


def test_run_backup_uses_clean_s3_key(monkeypatch, tmp_path):
    cfg = BackupConfig(backup_dir=str(tmp_path), s3_bucket="bucket", password=None)
    called = {}

    monkeypatch.setattr("patronx.backup._db_size", lambda _cfg: 0)

    class FakeProc:
        def __init__(self):
            self.stdout = io.BytesIO(b"data")
            self.stderr = io.BytesIO()

        def wait(self):
            return 0

    monkeypatch.setattr(
        "patronx.backup.sp.Popen", lambda *a, **k: FakeProc()
    )

    def fake_upload(file, bucket, key):
        called["key"] = key

    monkeypatch.setattr("patronx.backup._upload_to_s3", fake_upload)

    out = tmp_path / "dump.dump"
    run_backup(cfg, out, show_progress=False)

    assert called["key"] == f"{out.name}"