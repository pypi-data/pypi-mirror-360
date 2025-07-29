import json
import logging
import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO

import pytest

from lewis_lazy_logger import simple_logger_setup


def test_logger_creation():
    logger = simple_logger_setup(level="warning", name="test_logger")
    assert isinstance(logger, logging.Logger)
    assert logger.level == logging.WARNING
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)


def test_logger_rich_handler():
    logger = simple_logger_setup(use_rich=True, name="rich_logger_test")
    from rich.logging import RichHandler

    assert any(isinstance(h, RichHandler) for h in logger.handlers)


def test_logger_json_output(capfd):
    logger = simple_logger_setup(json_output=True, name="json_logger_test")
    logger.info("Test message")
    out, _ = capfd.readouterr()
    log_dict = json.loads(out.strip())

    assert log_dict["message"] == "Test message"
    assert log_dict["level"] == "INFO"
    assert log_dict["logger"] == "json_logger_test"


def test_logger_file_output():
    with tempfile.NamedTemporaryFile(delete=False) as temp_log:
        logger = simple_logger_setup(
            log_to_file=True, file_path=temp_log.name, name="file_logger_test"
        )
        logger.warning("This is a warning!")

    with open(temp_log.name, "r") as f:
        contents = f.read()

    assert "This is a warning!" in contents
    assert "WARNING" in contents
    assert "file_logger_test" in contents


def test_logger_env_level_override(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "ERROR")
    logger = simple_logger_setup(level="debug", name="env_logger_test")
    assert logger.level == logging.ERROR
