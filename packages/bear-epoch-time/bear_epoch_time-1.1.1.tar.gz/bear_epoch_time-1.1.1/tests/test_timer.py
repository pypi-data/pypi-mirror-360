"""Tests for the timer context manager in bear_epoch_time."""

import re
import time

from bear_epoch_time.timer import timer


class DummyConsole:
    def __init__(self) -> None:
        """Initialize a dummy console to capture printed messages."""
        self.messages = []

    def print(self, msg, **kwargs) -> None:  # noqa: ARG002
        """Simulate printing a message to the console."""
        self.messages.append(msg)


class TestTimerContextManager:
    """Tests for the timer context manager."""

    def test_custom_name_and_console(self) -> None:
        """Test that the timer can be used with a custom name and console."""
        dummy = DummyConsole()
        with timer(name="custom", console=dummy) as data:
            assert data.name == "custom"
            assert data.console is dummy
        assert len(dummy.messages) == 1
        assert "custom" in dummy.messages[0]
        assert "Elapsed time" in dummy.messages[0]

    def test_subsecond_accuracy(self) -> None:
        """Test that the timer can measure subsecond durations accurately."""
        dummy = DummyConsole()
        with timer(name="quick", console=dummy) as data:
            time.sleep(0.05)

        assert 0 < data.elapsed_seconds < 0.2
        assert 50 <= data.elapsed_milliseconds < 200

    def test_logging_precision(self) -> None:
        """Test that the timer logs elapsed time with high precision."""
        dummy = DummyConsole()
        with timer(name="precision", console=dummy):
            pass

        assert re.search(r"Elapsed time: [0-9]*\.[0-9]{6} seconds", dummy.messages[0])
