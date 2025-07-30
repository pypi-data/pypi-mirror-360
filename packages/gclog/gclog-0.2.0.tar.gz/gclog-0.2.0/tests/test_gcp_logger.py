import json
import os
import sys
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch, MagicMock, Mock
import pytest
import requests

from gclog import (
    get_logger,
    GCPLogger,
    is_running_on_cloud,
    serialize,
    gcp_sink,
    local_sink,
    set_contextual_logger,
    clear_contextual_logger,
)


# Test is_running_on_cloud function
@pytest.mark.parametrize(
    "env_var,env_value",
    [
        ("K_REVISION", "test-revision"),
        ("FUNCTION_NAME", "test-function"),
        ("GAE_APPLICATION", "test-app"),
        ("CLOUD_RUN_JOB", "test-job"),
        ("KUBERNETES_SERVICE_HOST", "10.0.0.1"),
    ],
)
def test_gcp_environment_detection(env_var, env_value):
    """Test detection of various GCP environments via environment variables."""
    with patch.dict(os.environ, {env_var: env_value}):
        assert is_running_on_cloud() is True


@patch("requests.get")
def test_compute_engine_detection(mock_get):
    """Test detection of Compute Engine via metadata server."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {}, clear=True):
        assert is_running_on_cloud() is True
        mock_get.assert_called_once_with(
            "http://metadata.google.internal/computeMetadata/v1/instance/id",
            headers={"Metadata-Flavor": "Google"},
            timeout=1,
        )


@pytest.mark.parametrize(
    "exception_type",
    [
        requests.RequestException("Connection failed"),
        requests.Timeout("Request timed out"),
        requests.ConnectionError("Cannot connect"),
    ],
)
@patch("requests.get")
def test_compute_engine_detection_failure(mock_get, exception_type):
    """Test Compute Engine detection when metadata server fails."""
    mock_get.side_effect = exception_type

    with patch.dict(os.environ, {}, clear=True):
        assert is_running_on_cloud() is False


@pytest.mark.parametrize("status_code", [404, 403, 500])
@patch("requests.get")
def test_compute_engine_detection_wrong_status(mock_get, status_code):
    """Test Compute Engine detection with wrong HTTP status."""
    mock_response = Mock()
    mock_response.status_code = status_code
    mock_get.return_value = mock_response

    with patch.dict(os.environ, {}, clear=True):
        assert is_running_on_cloud() is False


def test_not_on_cloud():
    """Test when not running on any cloud platform."""
    with patch.dict(os.environ, {}, clear=True), patch("requests.get") as mock_get:
        mock_get.side_effect = requests.RequestException()
        assert is_running_on_cloud() is False


# Test serialize function
@pytest.mark.parametrize(
    "level_name,message,elapsed_seconds",
    [
        ("INFO", "Test info message", 1.5),
        ("ERROR", "Test error message", 0.1),
        ("DEBUG", "Test debug message", 2.0),
        ("WARNING", "Test warning message", 0.5),
    ],
)
def test_serialize_basic_record(level_name, message, elapsed_seconds):
    """Test serialization of basic log records with different levels."""
    mock_file = Mock()
    mock_file.name = "test.py"
    mock_file.path = "/path/to/test.py"

    mock_level = Mock()
    mock_level.name = level_name

    mock_process = Mock()
    mock_process.id = 1234
    mock_process.name = "python"

    mock_thread = Mock()
    mock_thread.id = 5678
    mock_thread.name = "MainThread"

    test_time = datetime(2023, 1, 1, 12, 0, 0)
    test_elapsed = timedelta(seconds=elapsed_seconds)

    record = {
        "level": mock_level,
        "message": message,
        "elapsed": test_elapsed,
        "exception": None,
        "file": mock_file,
        "function": "test_function",
        "line": 42,
        "module": "test_module",
        "name": "test_logger",
        "process": mock_process,
        "thread": mock_thread,
        "time": test_time,
        "extra": {"key": "value"},
    }

    result = serialize(record)
    data = json.loads(result)

    assert data["severity"] == level_name
    assert data["message"] == message
    assert data["elapsed"] == elapsed_seconds
    assert data["exception"] is None
    assert data["file"]["name"] == "test.py"
    assert data["file"]["path"] == "/path/to/test.py"
    assert data["function"] == "test_function"
    assert data["line"] == 42
    assert data["module"] == "test_module"
    assert data["name"] == "test_logger"
    assert data["process"]["id"] == 1234
    assert data["process"]["name"] == "python"
    assert data["thread"]["id"] == 5678
    assert data["thread"]["name"] == "MainThread"
    assert data["time"] == "2023-01-01T12:00:00"
    assert data["extra"] == {"key": "value"}


@pytest.mark.parametrize(
    "exception_type,exception_message",
    [
        (ValueError, "Test value error"),
        (TypeError, "Test type error"),
        (RuntimeError, "Test runtime error"),
    ],
)
def test_serialize_with_exception(exception_type, exception_message):
    """Test serialization of log record with different exception types."""
    mock_file = Mock()
    mock_file.name = "test.py"
    mock_file.path = "/path/to/test.py"

    mock_level = Mock()
    mock_level.name = "ERROR"

    mock_process = Mock()
    mock_process.id = 1234
    mock_process.name = "python"

    mock_thread = Mock()
    mock_thread.id = 5678
    mock_thread.name = "MainThread"

    # Mock exception info
    try:
        raise exception_type(exception_message)
    except exception_type:
        import sys

        exc_info = sys.exc_info()

    record = {
        "level": mock_level,
        "message": "Error occurred",
        "elapsed": timedelta(seconds=0.1),
        "exception": exc_info,
        "file": mock_file,
        "function": "test_function",
        "line": 42,
        "module": "test_module",
        "name": "test_logger",
        "process": mock_process,
        "thread": mock_thread,
        "time": datetime(2023, 1, 1, 12, 0, 0),
        "extra": {},
    }

    result = serialize(record)
    data = json.loads(result)

    assert data["severity"] == "ERROR"
    assert data["message"] == "Error occurred"
    assert data["exception"] is not None
    assert f"{exception_type.__name__}: {exception_message}" in data["exception"]
    assert "Traceback" in data["exception"]


# Test sink functions
def test_gcp_sink():
    """Test GCP sink function."""
    # Use actual loguru to create a real message
    from loguru import logger

    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        # Capture a real log record using loguru's handler system
        captured_record = None

        def capture_record(message):
            nonlocal captured_record
            captured_record = message.record

        test_logger = logger.bind(test_key="test_value")
        test_logger.add(capture_record, level="DEBUG")
        test_logger.info("Test message")
        test_logger.remove()

        # Create message with real record
        mock_message = Mock()
        mock_message.record = captured_record

        gcp_sink(mock_message)
        output = mock_stderr.getvalue()

    # Should output JSON
    assert output.strip()
    data = json.loads(output.strip())
    assert data["message"] == "Test message"
    assert data["severity"] == "INFO"


@pytest.mark.parametrize(
    "level_no,expected_stream",
    [
        (10, "stdout"),  # DEBUG
        (20, "stdout"),  # INFO
        (25, "stdout"),  # Custom level below WARNING
        (30, "stderr"),  # WARNING
        (40, "stderr"),  # ERROR
        (50, "stderr"),  # CRITICAL
    ],
)
def test_local_sink_stream_selection(level_no, expected_stream):
    """Test local sink directs messages to correct stream based on level."""

    # Create a simple message object
    class SimpleMessage:
        def __init__(self, level_no, text):
            self.record = {"level": type("Level", (), {"no": level_no})()}
            self.text = text

        def __str__(self):
            return self.text

    message = SimpleMessage(level_no, f"Level {level_no}: Test message")

    stdout_patch = patch("sys.stdout", new_callable=StringIO)
    stderr_patch = patch("sys.stderr", new_callable=StringIO)

    with stdout_patch as mock_stdout, stderr_patch as mock_stderr:
        local_sink(message)

        if expected_stream == "stdout":
            assert message.text in mock_stdout.getvalue()
            assert mock_stderr.getvalue() == ""
        else:
            assert message.text in mock_stderr.getvalue()
            assert mock_stdout.getvalue() == ""


# Test GCPLogger class
def test_singleton_behavior():
    """Test that GCPLogger implements singleton pattern."""
    with patch("gclog.gclog.logger") as mock_logger:
        logger1 = GCPLogger()
        logger2 = GCPLogger()

        # Should return the same logger instance
        assert logger1 is logger2
        assert logger1 is mock_logger


@pytest.mark.parametrize(
    "is_cloud,expected_sink",
    [
        (True, "gcp_sink"),
        (False, "local_sink"),
    ],
)
@patch("gclog.gclog.logger")
def test_logger_configuration_by_environment(mock_logger, is_cloud, expected_sink):
    """Test logger configuration based on cloud environment."""
    with patch("gclog.gclog.is_running_on_cloud") as mock_is_cloud:
        mock_is_cloud.return_value = is_cloud

        GCPLogger()

        mock_logger.remove.assert_called_once()
        mock_logger.add.assert_called_once()
        args, kwargs = mock_logger.add.call_args
        assert args[0].__name__ == expected_sink
        assert kwargs["backtrace"] is True
        # Different sinks have different parameters
        if expected_sink == "gcp_sink":
            assert kwargs["catch"] is True
        else:
            assert kwargs["diagnose"] is True


@patch("gclog.gclog.is_running_on_cloud")
@patch("gclog.gclog.logger")
def test_configuration_failure(mock_logger, mock_is_cloud):
    """Test logger configuration failure handling."""
    mock_is_cloud.return_value = False
    mock_logger.add.side_effect = [Exception("Config failed"), None, None]

    GCPLogger()

    # Should have attempted configuration and fallback
    assert mock_logger.add.call_count >= 2
    mock_logger.exception.assert_called_once()


@pytest.mark.parametrize("log_level", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
def test_custom_log_level(log_level):
    """Test logger with different custom log levels."""
    with (
        patch("gclog.gclog.is_running_on_cloud") as mock_is_cloud,
        patch("gclog.gclog.logger") as mock_logger,
    ):
        mock_is_cloud.return_value = False

        GCPLogger(level=log_level)

        args, kwargs = mock_logger.add.call_args
        assert kwargs["level"] == log_level


# Test get_logger function
def test_get_logger_returns_logger():
    """Test that get_logger returns a logger instance."""
    with patch("gclog.gclog.GCPLogger") as mock_gcp_logger:
        mock_gcp_logger.return_value = "mock_logger"

        result = get_logger()

        assert result == "mock_logger"
        mock_gcp_logger.assert_called_once()


def test_extra_data_persistence():
    """Test that extra data added to logger is persisted in log output."""
    from loguru import logger
    
    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        # Capture a real log record with extra data
        captured_record = None

        def capture_record(message):
            nonlocal captured_record
            captured_record = message.record

        test_logger = logger.bind(user_id="12345", session_id="abc123")
        test_logger.add(capture_record, level="DEBUG")
        test_logger.info("User performed action", extra={"action": "login", "ip": "192.168.1.1"})
        test_logger.remove()

        # Create message with real record
        mock_message = Mock()
        mock_message.record = captured_record

        gcp_sink(mock_message)
        output = mock_stderr.getvalue()

    # Should output JSON with extra data
    assert output.strip()
    data = json.loads(output.strip())
    
    # Check the message is correct
    assert data["message"] == "User performed action"
    assert data["severity"] == "INFO"
    
    # Check extra data is persisted in extra field
    extra = data["extra"]
    assert extra["user_id"] == "12345"
    assert extra["session_id"] == "abc123"
    assert extra["action"] == "login"
    assert extra["ip"] == "192.168.1.1"


def test_bound_logger_extra_data():
    """Test that bound logger context persists across multiple log calls."""
    from loguru import logger
    
    captured_records = []

    def capture_record(message):
        captured_records.append(message.record)

    # Create a bound logger with persistent context
    test_logger = logger.bind(service="api", version="1.0.0")
    test_logger.add(capture_record, level="DEBUG")
    
    # Log multiple messages
    test_logger.info("Service started")
    test_logger.warning("Rate limit approaching", extra={"current_requests": 950})
    test_logger.error("Service error", extra={"error_code": "E500"})
    
    test_logger.remove()

    # Check all records have the bound context
    assert len(captured_records) == 3
    
    # Test using our serialize function to get properly merged data
    for i, record in enumerate(captured_records):
        serialized = serialize(record)
        data = json.loads(serialized)
        
        # All should have bound context
        assert data["extra"]["service"] == "api"
        assert data["extra"]["version"] == "1.0.0"
    
    # Check specific extra data in serialized format
    data1 = json.loads(serialize(captured_records[1]))
    data2 = json.loads(serialize(captured_records[2]))
    
    assert data1["extra"]["current_requests"] == 950
    assert data2["extra"]["error_code"] == "E500"


@pytest.mark.parametrize("extra_data", [
    {"user_id": "123", "action": "view"},
    {"session": "sess_abc", "ip": "10.0.0.1", "user_agent": "Mozilla/5.0"},
    {"nested": {"key": "value", "number": 42}, "list": [1, 2, 3]},
])
def test_various_extra_data_types(extra_data):
    """Test that various types of extra data are properly serialized."""
    from loguru import logger
    
    with patch("sys.stderr", new_callable=StringIO) as mock_stderr:
        captured_record = None

        def capture_record(message):
            nonlocal captured_record
            captured_record = message.record

        test_logger = logger
        test_logger.add(capture_record, level="DEBUG")
        test_logger.info("Test message", extra=extra_data)
        test_logger.remove()

        # Create message with real record
        mock_message = Mock()
        mock_message.record = captured_record

        gcp_sink(mock_message)
        output = mock_stderr.getvalue()

    # Should output JSON with extra data preserved
    data = json.loads(output.strip())
    
    # Check extra data is in extra field
    for key, value in extra_data.items():
        assert data["extra"][key] == value


# Test format_record function
def test_format_record_without_extra_data():
    """Test format_record function returns basic format when no extra data."""
    from gclog.gclog import format_record
    
    record = {
        "extra": {}
    }
    
    result = format_record(record)
    base_format = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> | <level>{level: <8}</level> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level>\n"
    assert result == base_format


def test_format_record_with_extra_data():
    """Test format_record function includes extra data when present."""
    from gclog.gclog import format_record
    
    record = {
        "extra": {"user_id": "123", "action": "login"}
    }
    
    result = format_record(record)
    expected_format = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> | <level>{level: <8}</level> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level> | <y>{extra}</y>\n"
    assert result == expected_format


def test_format_record_with_nested_extra_data():
    """Test format_record function properly handles nested extra data."""
    from gclog.gclog import format_record
    
    record = {
        "extra": {
            "user_id": "123",
            "extra": {"session_id": "abc", "ip": "192.168.1.1"}
        }
    }
    
    result = format_record(record)
    expected_format = "<g>{time:YYYY-MM-DD HH:mm:ss.SSS}</g> | <level>{level: <8}</level> | <c>{name}</c>:<c>{function}</c>:<c>{line}</c> - <level>{message}</level> | <y>{extra}</y>\n"
    assert result == expected_format


def test_logger_already_configured():
    """Test that configure method returns early when already configured."""
    with patch("gclog.gclog.logger") as mock_logger:
        # Set configured to True to trigger early return
        GCPLogger._configured = True
        
        # Call configure method directly 
        GCPLogger._configure_logger("INFO")
        
        # Should not call any logger methods due to early return
        mock_logger.remove.assert_not_called()
        mock_logger.add.assert_not_called()


# Test contextual logger functionality
def test_contextual_logger_set_and_get():
    """Test that contextual logger can be set and retrieved."""
    from loguru import logger
    
    # Create a bound logger
    bound_logger = logger.bind(user_id="123", session_id="abc")
    
    # Set contextual logger
    set_contextual_logger(bound_logger)
    
    # Get logger should return the contextual logger
    result = get_logger()
    assert result is bound_logger
    
    # Clear context
    clear_contextual_logger()
    
    # Now should return base logger
    with patch("gclog.gclog.GCPLogger") as mock_gcp_logger:
        mock_gcp_logger.return_value = "base_logger"
        result = get_logger()
        assert result == "base_logger"


def test_contextual_logger_clear():
    """Test that clearing contextual logger works correctly."""
    from loguru import logger
    
    # Set contextual logger
    bound_logger = logger.bind(test_key="test_value")
    set_contextual_logger(bound_logger)
    
    # Verify it's set
    assert get_logger() is bound_logger
    
    # Clear it
    clear_contextual_logger()
    
    # Should return None from context
    with patch("gclog.gclog.GCPLogger") as mock_gcp_logger:
        mock_gcp_logger.return_value = "base_logger"
        result = get_logger()
        assert result == "base_logger"


def test_contextual_logger_isolation():
    """Test that contextual logger isolates between different contexts."""
    import asyncio
    from loguru import logger
    
    results = []
    
    async def context_task(task_id, user_id):
        # Set different contextual loggers in each task
        bound_logger = logger.bind(task_id=task_id, user_id=user_id)
        set_contextual_logger(bound_logger)
        
        # Simulate some async work
        await asyncio.sleep(0.01)
        
        # Get logger should return the correct contextual logger
        result_logger = get_logger()
        results.append((task_id, result_logger is bound_logger))
    
    async def run_concurrent_tasks():
        # Run multiple tasks concurrently
        tasks = [
            context_task(1, "user_123"),
            context_task(2, "user_456"),
            context_task(3, "user_789")
        ]
        await asyncio.gather(*tasks)
    
    # Run the test
    asyncio.run(run_concurrent_tasks())
    
    # All tasks should have gotten their own contextual logger
    assert len(results) == 3
    for task_id, is_correct_logger in results:
        assert is_correct_logger, f"Task {task_id} did not get correct contextual logger"


def test_contextual_logger_with_bound_context():
    """Test that contextual logger preserves bound context in log output."""
    from loguru import logger
    
    # Create bound logger with context
    bound_logger = logger.bind(user_id="123", conversation_id="abc")
    set_contextual_logger(bound_logger)
    
    # Get logger should return the bound logger with context
    contextual_logger = get_logger()
    
    # Capture log output
    captured_records = []
    
    def capture_record(message):
        captured_records.append(message.record)
    
    contextual_logger.add(capture_record, level="DEBUG")
    contextual_logger.info("Test message with context")
    contextual_logger.remove()
    
    # Should have captured one record
    assert len(captured_records) == 1
    
    # Serialize the record and check context is preserved
    serialized = serialize(captured_records[0])
    data = json.loads(serialized)
    
    assert data["extra"]["user_id"] == "123"
    assert data["extra"]["conversation_id"] == "abc"
    
    # Clear context
    clear_contextual_logger()


def test_contextual_logger_without_context():
    """Test that get_logger returns base logger when no context is set."""
    # Make sure no context is set
    clear_contextual_logger()
    
    with patch("gclog.gclog.GCPLogger") as mock_gcp_logger:
        mock_gcp_logger.return_value = "base_logger"
        
        result = get_logger()
        assert result == "base_logger"
        mock_gcp_logger.assert_called_once()


def test_contextual_logger_async_propagation():
    """Test that contextual logger propagates across async boundaries."""
    import asyncio
    from loguru import logger
    
    captured_records = []
    
    def capture_record(message):
        captured_records.append(message.record)
    
    async def inner_function():
        # This should get the contextual logger set in outer function
        inner_logger = get_logger()
        inner_logger.add(capture_record, level="DEBUG")
        inner_logger.info("Inner function log")
        inner_logger.remove()
    
    async def outer_function():
        # Set contextual logger
        bound_logger = logger.bind(request_id="req_123")
        set_contextual_logger(bound_logger)
        
        # Log from outer function
        outer_logger = get_logger()
        outer_logger.add(capture_record, level="DEBUG")
        outer_logger.info("Outer function log")
        outer_logger.remove()
        
        # Call inner function - context should propagate
        await inner_function()
        
        # Clear context
        clear_contextual_logger()
    
    # Run the test
    asyncio.run(outer_function())
    
    # Should have captured two records
    assert len(captured_records) == 2
    
    # Both should have the same context
    for record in captured_records:
        serialized = serialize(record)
        data = json.loads(serialized)
        assert data["extra"]["request_id"] == "req_123"
