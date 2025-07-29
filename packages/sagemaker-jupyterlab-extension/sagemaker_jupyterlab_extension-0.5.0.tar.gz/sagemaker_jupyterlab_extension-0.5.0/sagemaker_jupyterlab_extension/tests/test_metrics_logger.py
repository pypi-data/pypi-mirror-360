import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from ..utils.metrics_logger import MetricsLogger, logger as metrics_logger


@pytest.fixture
def metrics_logger_instance():
    # Use a temporary file for testing
    with patch("os.makedirs") as mock_makedirs:
        logger = MetricsLogger("/tmp/test_metrics.log")
        mock_makedirs.assert_called_once_with(
            os.path.dirname("/tmp/test_metrics.log"), exist_ok=True
        )
        yield logger


def test_metrics_logger_init():
    # Test default initialization
    with patch("os.makedirs") as mock_makedirs:
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            logger = MetricsLogger()
            assert (
                logger.log_file_path
                == "/var/log/studio/jupyterlab/sm-jupyterlab-ext.ui.log"
            )
            mock_makedirs.assert_called_once_with(
                "/var/log/studio/jupyterlab", exist_ok=True
            )
            mock_logger.info.assert_called_once()

    # Test custom path initialization
    with patch("os.makedirs") as mock_makedirs:
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            custom_path = "/custom/path/metrics.log"
            logger = MetricsLogger(custom_path)
            assert logger.log_file_path == custom_path
            mock_makedirs.assert_called_once_with("/custom/path", exist_ok=True)
            mock_logger.info.assert_called_once()

    # Test initialization with error
    with patch("os.makedirs", side_effect=Exception("Test error")):
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            logger = MetricsLogger()
            mock_logger.error.assert_called_once()


def test_log_metric_success(metrics_logger_instance):
    # Test successful logging with valid JSON string
    valid_json = '{"metric": "test", "value": 1}'

    with patch("builtins.open", mock_open()) as mock_file:
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            result = metrics_logger_instance.log_metric(valid_json)
            assert result is True
            mock_file.assert_called_once_with("/tmp/test_metrics.log", "a")
            mock_file().write.assert_called_once_with(f"{valid_json}\n")
            mock_logger.info.assert_called()


def test_log_metric_invalid_json(metrics_logger_instance):
    # Test with invalid JSON
    invalid_json = "{metric: test, value: 1}"  # Missing quotes

    with patch("builtins.open", mock_open()) as mock_file:
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            result = metrics_logger_instance.log_metric(invalid_json)
            assert result is True  # Still returns True as it attempts to write anyway
            mock_logger.warning.assert_called_once()
            mock_file().write.assert_called_once_with(f"{invalid_json}\n")


def test_log_metric_non_string_input(metrics_logger_instance):
    # Test with non-string input
    non_string_input = {"metric": "test", "value": 1}

    with patch("builtins.open", mock_open()) as mock_file:
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            result = metrics_logger_instance.log_metric(non_string_input)
            assert result is True
            mock_logger.warning.assert_called_once()
            mock_file().write.assert_called_once_with(f"{non_string_input}\n")


def test_log_metric_file_error(metrics_logger_instance):
    # Test with file write error
    valid_json = '{"metric": "test", "value": 1}'

    with patch("builtins.open", side_effect=Exception("Test error")):
        with patch(
            "sagemaker_jupyterlab_extension.utils.metrics_logger.logger"
        ) as mock_logger:
            result = metrics_logger_instance.log_metric(valid_json)
            assert result is False
            mock_logger.error.assert_called_once()
