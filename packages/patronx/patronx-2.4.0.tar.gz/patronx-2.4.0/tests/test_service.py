import threading
import time

import remoulade
from remoulade import Worker, actor
from remoulade.brokers.stub import StubBroker

import patronx.service as service


def test_run_worker_and_scheduler(monkeypatch):
    broker = StubBroker()
    remoulade.set_broker(broker)

    executed = []

    @actor
    def dummy_job():
        executed.append(True)

    remoulade.declare_actors([dummy_job])

    started = threading.Event()
    health_started = threading.Event()

    def fake_run_scheduler():
        started.set()
        dummy_job.send()
        # keep the thread alive briefly so service can verify it's running
        time.sleep(0.05)

    monkeypatch.setattr(service, "run_scheduler", fake_run_scheduler)

    def fake_start_health_server():
        health_started.set()
        time.sleep(0.05)

    monkeypatch.setattr(service, "start_health_server", fake_start_health_server)

    class TestWorker(Worker):
        def start(self):
            super().start()
            # wait for queued job and then shut down
            self.broker.join("default", timeout=1000)
            self.stop()

    monkeypatch.setattr(service, "Worker", TestWorker)

    service.run_worker_and_scheduler()

    assert started.is_set()
    assert health_started.is_set()
    assert executed == [True]