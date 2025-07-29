import importlib


def test_interval_from_cron_is_positive():
    sched = importlib.import_module("patronx.schedule")
    assert sched._interval_from_cron("* * * * *") > 0


def test_start_scheduler_starts(monkeypatch):
    sched = importlib.import_module("patronx.schedule")
    importlib.reload(sched)

    # Dummy BackupConfig
    DummyCfg = type(
        "Cfg",
        (),
        {
            "backup_cron": "* * * * *",
            "cleanup_cron": "* * * * *",
            "redis_url": "redis://r",
            "from_env": classmethod(lambda cls: cls()),
        },
    )
    monkeypatch.setattr(sched, "BackupConfig", DummyCfg, raising=False)

    # Track hdel calls
    hdel_calls = []

    # Mock redis client
    class FakeRedis:
        def hvals(self, key):
            assert key == "remoulade:schedule"
            # Simulate two jobs: one matching "run_backup_job", one not
            return [b"xxxrun_backup_jobyyy", b"other_job"]

        def hdel(self, key, job_key):
            hdel_calls.append((key, job_key))

    monkeypatch.setattr(sched.redis, "from_url", lambda url: FakeRedis())

    fake_broker = object()
    monkeypatch.setattr(sched.remoulade, "get_broker", lambda: fake_broker)

    jobs = [object()]
    monkeypatch.setattr(sched, "init_scheduled_jobs", lambda b, c: jobs)

    created = {}

    class DummyScheduler:
        def __init__(self, broker, client, schedule):
            created["args"] = (broker, client, schedule)
            self.logger = None

        def start(self):
            created["started"] = True

    monkeypatch.setattr(sched, "Scheduler", DummyScheduler)

    holder = {}
    monkeypatch.setattr(sched.remoulade, "set_scheduler", lambda s: holder.setdefault("sched", s))
    monkeypatch.setattr(sched.remoulade, "get_scheduler", lambda: holder["sched"])
    monkeypatch.setattr(sched.logger, "info", lambda *a, **k: None)

    sched.start_scheduler()

    assert created["args"][0] is fake_broker
    assert isinstance(created["args"][1], FakeRedis)
    assert created["args"][2] == jobs
    assert created.get("started") is True

    # Confirm hdel was called only for matching job
    assert hdel_calls == [("remoulade:schedule", b"xxxrun_backup_jobyyy"[:40])]



def test_job_from_cron_sets_future_last_queued(monkeypatch):
    sched = importlib.import_module("patronx.schedule")
    importlib.reload(sched)

    fixed_now = sched.datetime(2024, 1, 1, 23, 50, 0)

    class DummyDatetime(sched.datetime):
        @classmethod
        def utcnow(cls):  # type: ignore[override]
            return fixed_now

    monkeypatch.setattr(sched, "datetime", DummyDatetime)

    job = sched._job_from_cron("0 0 * * *", "run_backup_job")

    next_run = job.last_queued + sched.timedelta(seconds=job.interval)
    assert next_run > fixed_now
    assert (next_run - fixed_now).total_seconds() == 10 * 60