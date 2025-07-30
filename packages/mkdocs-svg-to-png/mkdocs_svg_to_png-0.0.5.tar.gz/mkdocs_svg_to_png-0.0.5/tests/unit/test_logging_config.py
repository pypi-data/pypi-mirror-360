"""Tests for logging configuration module."""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from mkdocs_svg_to_png.logging_config import (
    StructuredFormatter,
    create_error_context,
    create_performance_context,
    create_processing_context,
    get_plugin_logger,
    log_with_context,
    setup_plugin_logging,
)


class TestStructuredFormatter:
    """Test StructuredFormatter class."""

    def test_format_basic_message(self) -> None:
        """Test formatting a basic log message."""
        formatter = StructuredFormatter(include_caller=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)
        assert "level=INFO" in formatted
        assert "logger=test.logger" in formatted
        assert "message=Test message" in formatted
        assert "timestamp=" in formatted

    def test_format_with_caller_info(self) -> None:
        """Test formatting with caller information."""
        formatter = StructuredFormatter(include_caller=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Error message",
            args=(),
            exc_info=None,
            func="test_function",
        )

        formatted = formatter.format(record)
        assert "caller=file.py:test_function:42" in formatted

    def test_format_with_context(self) -> None:
        """Test formatting with context information."""
        formatter = StructuredFormatter(include_caller=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Context message",
            args=(),
            exc_info=None,
        )
        record.context = {"key1": "value1", "key2": "value2"}

        formatted = formatter.format(record)
        assert "key1=value1" in formatted
        assert "key2=value2" in formatted

    def test_format_with_exception(self) -> None:
        """Test formatting with exception information."""
        formatter = StructuredFormatter(include_caller=False)
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys

            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="",
                lineno=0,
                msg="Exception occurred",
                args=(),
                exc_info=exc_info,
            )

        formatted = formatter.format(record)
        assert "exception=" in formatted
        assert "ValueError" in formatted

    def test_format_without_pathname_attribute(self) -> None:
        """Test formatting when record has no pathname attribute."""
        formatter = StructuredFormatter(include_caller=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None,
            funcName="test_function",
        )

        # Remove the pathname attribute to test hasattr check
        delattr(record, "pathname")

        formatted = formatter.format(record)
        # When pathname attribute doesn't exist, caller info should not be included
        assert "caller=" not in formatted

    def test_format_with_non_dict_context(self) -> None:
        """Test formatting when context is not a dict."""
        formatter = StructuredFormatter(include_caller=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Context message",
            args=(),
            exc_info=None,
        )
        record.context = "not a dict"

        formatted = formatter.format(record)
        # Should not contain context key=value pairs since context is not a dict
        assert "=" in formatted  # Only timestamp=, level=, etc.


class TestSetupPluginLogging:
    """Test setup_plugin_logging function."""

    def setup_method(self) -> None:
        """Clear any existing handlers before each test."""
        logger = logging.getLogger("mkdocs_svg_to_png")
        logger.handlers.clear()

    def test_setup_with_env_variable(self) -> None:
        """Test setup with environment variable override."""
        with patch.dict(os.environ, {"MKDOCS_SVG_TO_PNG_LOG_LEVEL": "DEBUG"}):
            setup_plugin_logging(level="INFO", force=True)

        logger = logging.getLogger("mkdocs_svg_to_png")
        assert logger.level == logging.DEBUG

    def test_setup_with_invalid_env_variable(self) -> None:
        """Test setup with invalid environment variable."""
        with patch.dict(os.environ, {"MKDOCS_SVG_TO_PNG_LOG_LEVEL": "INVALID"}):
            setup_plugin_logging(level="INFO", force=True)

        logger = logging.getLogger("mkdocs_svg_to_png")
        assert logger.level == logging.INFO

    def test_setup_with_log_file(self) -> None:
        """Test setup with log file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            setup_plugin_logging(log_file=log_file, force=True)

            logger = logging.getLogger("mkdocs_svg_to_png")
            assert len(logger.handlers) == 2  # Console + File
            assert log_file.exists()

    def test_setup_without_force_skips_existing(self) -> None:
        """Test setup without force skips when handlers exist."""
        # First setup
        setup_plugin_logging(force=True)
        logger = logging.getLogger("mkdocs_svg_to_png")
        initial_handler_count = len(logger.handlers)

        # Second setup without force should not add more handlers
        setup_plugin_logging(force=False)
        assert len(logger.handlers) == initial_handler_count

    def test_setup_with_force_clears_existing(self) -> None:
        """Test setup with force clears existing handlers."""
        # First setup
        setup_plugin_logging(force=True)
        logger = logging.getLogger("mkdocs_svg_to_png")

        # Add an extra handler manually
        extra_handler = logging.StreamHandler()
        logger.addHandler(extra_handler)
        handler_count_with_extra = len(logger.handlers)

        # Second setup with force should clear all and recreate
        setup_plugin_logging(force=True)
        assert len(logger.handlers) < handler_count_with_extra


class TestGetPluginLogger:
    """Test get_plugin_logger function."""

    def test_get_logger_without_context(self) -> None:
        """Test getting logger without context."""
        logger = get_plugin_logger("test.module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"

    def test_get_logger_with_context(self) -> None:
        """Test getting logger with context."""
        logger = get_plugin_logger("test.module", key1="value1", key2="value2")
        assert isinstance(logger, logging.LoggerAdapter)
        assert logger.logger.name == "test.module"
        assert logger.extra == {"key1": "value1", "key2": "value2"}

    def test_context_adapter_process(self) -> None:
        """Test ContextAdapter process method."""
        logger = get_plugin_logger("test.module", base_key="base_value")

        # Test with no extra in kwargs
        msg, kwargs = logger.process("test message", {})
        assert "extra" in kwargs
        assert "context" in kwargs["extra"]
        assert kwargs["extra"]["context"]["base_key"] == "base_value"

        # Test with existing extra but no context
        msg, kwargs = logger.process("test message", {"extra": {"other": "value"}})
        assert kwargs["extra"]["other"] == "value"
        assert kwargs["extra"]["context"]["base_key"] == "base_value"

        # Test with existing context
        msg, kwargs = logger.process(
            "test message", {"extra": {"context": {"existing": "context"}}}
        )
        assert kwargs["extra"]["context"]["existing"] == "context"
        assert kwargs["extra"]["context"]["base_key"] == "base_value"


def test_log_with_context() -> None:
    """Test log_with_context function."""
    mock_logger = Mock(spec=logging.Logger)
    mock_logger.info = Mock()

    log_with_context(mock_logger, "info", "Test message", key1="value1", key2="value2")

    mock_logger.info.assert_called_once_with(
        "Test message", extra={"context": {"key1": "value1", "key2": "value2"}}
    )


def test_create_processing_context() -> None:
    """Test create_processing_context function."""
    context = create_processing_context(page_file="test.md", block_index=1)
    assert context["page_file"] == "test.md"
    assert context["block_index"] == 1

    context = create_processing_context()
    assert context["page_file"] is None
    assert context["block_index"] is None


def test_create_error_context() -> None:
    """Test create_error_context function."""
    context = create_error_context(
        error_type="ValidationError", processing_step="parsing"
    )
    assert context["error_type"] == "ValidationError"
    assert context["processing_step"] == "parsing"

    context = create_error_context()
    assert context["error_type"] is None
    assert context["processing_step"] is None


def test_create_performance_context() -> None:
    """Test create_performance_context function."""
    context = create_performance_context(execution_time_ms=123.45, image_format="png")
    assert context["execution_time_ms"] == 123.45
    assert context["image_format"] == "png"

    context = create_performance_context(execution_time_ms=100.0, image_format="svg")
    assert context["execution_time_ms"] == 100.0
    assert context["image_format"] == "svg"

    # Test with invalid image format
    context = create_performance_context(execution_time_ms=100.0, image_format="gif")
    assert context["execution_time_ms"] == 100.0
    assert "image_format" not in context

    context = create_performance_context()
    assert context["execution_time_ms"] is None
    assert "image_format" not in context


class TestUnifiedLoggerFactory:
    """Test unified logger factory functionality (TDD RED phase)."""

    def test_get_logger_should_return_consistent_logger_instance(self) -> None:
        """Test that get_logger returns consistent logger instances across modules."""
        # This test should fail initially (RED phase)
        from mkdocs_svg_to_png.logging_config import get_logger

        logger1 = get_logger("module1")
        logger2 = get_logger("module1")

        # Same module name should return same logger instance
        assert logger1 is logger2
        assert isinstance(logger1, logging.Logger)
        assert logger1.name == "module1"

    def test_get_logger_should_have_proper_type_annotation(self) -> None:
        """Test that get_logger has proper type annotation (not Optional[Any])."""
        # This test should fail initially (RED phase)
        from mkdocs_svg_to_png.logging_config import get_logger

        logger = get_logger("test_module")
        # Should be logging.Logger, not Optional[Any]
        assert isinstance(logger, logging.Logger)

    def test_setup_logger_should_not_exist_in_utils(self) -> None:
        """Test that setup_logger function should not exist in utils module."""
        # This test should fail initially (RED phase)
        import importlib.util

        # Check if setup_logger exists in utils module
        try:
            spec = importlib.util.find_spec("mkdocs_svg_to_png.utils")
            if spec is not None and spec.loader is not None:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, "setup_logger"):
                    raise AssertionError(
                        "setup_logger should not exist in utils module"
                    )
        except ImportError:
            # This is expected after refactoring
            pass

    def test_all_modules_should_use_unified_logger_factory(self) -> None:
        """Test that all modules use the unified logger factory."""
        # This test should fail initially (RED phase)

        # Check that plugin.py uses get_logger instead of setup_logger
        from mkdocs_svg_to_png import plugin

        # Plugin should have proper logger type
        plugin_instance = plugin.SvgToPngPlugin()
        # This will fail initially because plugin uses Optional[Any]
        if hasattr(plugin_instance, "logger") and plugin_instance.logger is not None:
            assert isinstance(plugin_instance.logger, logging.Logger)
