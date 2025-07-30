"""Tests for the BasicLogger class in bear_epoch_time."""

from contextlib import redirect_stdout
from io import StringIO

import pytest

from bear_epoch_time.basic_logger import BasicLogger


class TestBasicLogger:
    """Test suite for the BasicLogger class."""

    @pytest.fixture
    def logger(self) -> BasicLogger:
        """Fixture to create a BasicLogger instance."""
        return BasicLogger()

    def test_logging_methods(self, logger: BasicLogger) -> None:
        """Test that all logging methods are callable."""
        methods = [
            "info",
            "debug",
            "warning",
            "error",
            "exception",
            "success",
            "failure",
            "verbose",
            "print",
            "log",
            "inspect",
            "print_json",
        ]
        for method in methods:
            assert callable(getattr(logger, method))

    def test_logging_output(self, logger: BasicLogger) -> None:
        """Test that logging methods produce output."""
        output = StringIO()
        with redirect_stdout(output):
            logger.info("Test info message")
            logger.debug("Test debug message")
            logger.warning("Test warning message")
            logger.error("Test error message")
            logger.exception("Test exception message")
            logger.success("Test success message")
            logger.failure("Test failure message")
            logger.verbose("Test verbose message")

        output_string: str = output.getvalue()
        output.close()

        assert "Test info message" in output_string
        assert "Test debug message" in output_string
        assert "Test warning message" in output_string
        assert "Test error message" in output_string
        assert "Test exception message" in output_string
        assert "Test success message" in output_string
        assert "Test failure message" in output_string
        assert "Test verbose message" in output_string

    @pytest.mark.visual
    def test_console_output(self, logger: BasicLogger) -> None:
        """Test that the console output is styled correctly."""
        logger.info("Testing console output")
        logger.debug("Testing console output")
        logger.warning("Testing console output")
        logger.error("Testing console output")
        logger.exception("Testing console output")
        logger.success("Testing console output")
        logger.failure("Testing console output")
        logger.verbose("Testing console output")

    @pytest.mark.visual
    def test_print_json(self, logger: BasicLogger) -> None:
        """Test that the print_json method works correctly."""
        data = {
            "key": "value",
            "number": 42,
            "list": [1, 2, 3],
            "nested": {"inner_key": "inner_value"},
        }
        logger.print_json(data, indent=4)

    def test_inspect_method(self, logger: BasicLogger) -> None:
        """Test that the inspect method works correctly."""
        obj = {"key": "value", "number": 42}
        output = StringIO()
        with redirect_stdout(output):
            logger.inspect(obj, all=True)

        output_string: str = output.getvalue()
        output.close()
        assert "key" in output_string
        assert "value" in output_string
        assert "number" in output_string
        assert "42" in output_string
        assert "new empty dictionary" in output_string
