import pytest
from unittest.mock import MagicMock
from synth_codeai.utils.agent_thread_manager import (
    agent_thread_registry,
    stop_agent,
    is_agent_running,
    has_received_stop_signal,
)

@pytest.fixture
def mock_registry():
    agent_thread_registry.clear()
    yield agent_thread_registry
    agent_thread_registry.clear()

def test_stop_agent_success(mock_registry):
    stop_event_mock = MagicMock()
    mock_registry[123] = {
        "thread": MagicMock(is_alive=lambda: True),
        "stop_event": stop_event_mock,
    }
    assert stop_agent(123) is True
    stop_event_mock.set.assert_called_once()

def test_stop_agent_no_entry(mock_registry):
    assert stop_agent(999) is False

def test_is_agent_running_true(mock_registry):
    mock_registry[111] = {
        "thread": MagicMock(is_alive=lambda: True),
        "stop_event": MagicMock(),
    }
    assert is_agent_running(111) is True

def test_is_agent_running_false(mock_registry):
    mock_registry[222] = {
        "thread": MagicMock(is_alive=lambda: False),
        "stop_event": MagicMock(),
    }
    assert is_agent_running(222) is False

def test_has_received_stop_signal_true(mock_registry):
    stop_event_mock = MagicMock(is_set=lambda: True)
    mock_registry[333] = {
        "thread": MagicMock(),
        "stop_event": stop_event_mock,
    }
    assert has_received_stop_signal(333) is True

def test_has_received_stop_signal_false(mock_registry):
    assert has_received_stop_signal(444) is False