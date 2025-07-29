import logging

from patronx import logger as logger_module


def test_get_logger_emits_logs(monkeypatch, caplog):
    # Replace Logstash handler to avoid network usage
    records = []

    class DummyHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    monkeypatch.setattr(
        logger_module,
        "TCPLogstashHandler",
        lambda *args, **kwargs: DummyHandler(),
    )
    monkeypatch.setattr(
        logger_module,
        "LogstashFormatterVersion1",
        lambda *args, **kwargs: logging.Formatter("%(levelname)s: %(message)s"),
    )

    with caplog.at_level(logging.INFO):
        log = logger_module.get_logger("test")
        log.info("hello")

    assert any("hello" in message for message in caplog.messages)
    assert any(r.getMessage() == "hello" for r in records)