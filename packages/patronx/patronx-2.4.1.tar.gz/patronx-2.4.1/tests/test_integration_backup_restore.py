import io

import pytest

from patronx.backup import run_backup, run_restore
from patronx.config import BackupConfig


def test_backup_and_restore(monkeypatch: pytest.MonkeyPatch, tmp_path):

    data = b"dummy dump"
    cfg = BackupConfig(backup_dir=str(tmp_path))
    dump_file = tmp_path / "dump"

    # ``run_backup`` calls this helper to determine the progress bar size.
    monkeypatch.setattr("patronx.backup._db_size", lambda _cfg: len(data))

    class FakeDumpProc:
        def __init__(self) -> None:
            self.stdout = io.BytesIO(data)
            self.stderr = io.BytesIO()

        def wait(self) -> int:
            return 0

    class FakeRestoreProc:
        def __init__(self) -> None:
            class _Buf(io.BytesIO):
                def close(buf_self):
                    buf_self.seek(0)
                    written.append(buf_self.read())
                    super().close()

            self.stdin = _Buf()
            self.stderr = io.BytesIO()

        def wait(self) -> int:
            return 0

    written: list[bytes] = []

    def fake_popen(cmd, **kwargs):
        """Return a fake process for ``pg_dump``/``pg_restore``."""

        if cmd[0] == "pg_dump":
            return FakeDumpProc()
        return FakeRestoreProc()

    monkeypatch.setattr("patronx.backup.sp.Popen", fake_popen)

    class FakeCursor:
        def execute(self, *args, **kwargs):
            pass

        def __enter__(self) -> "FakeCursor":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            pass

    class FakeConn:
        def cursor(self) -> FakeCursor:
            return FakeCursor()

        def close(self) -> None:  # noqa: D401 - part of DB API
            pass

        def __enter__(self) -> "FakeConn":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            pass

    monkeypatch.setattr("patronx.backup.psycopg2.connect", lambda **kw: FakeConn())

    run_backup(cfg, dump_file, show_progress=False)
    assert dump_file.read_bytes() == data

    run_restore(cfg, dump_file, show_progress=False)
    assert written == [data]