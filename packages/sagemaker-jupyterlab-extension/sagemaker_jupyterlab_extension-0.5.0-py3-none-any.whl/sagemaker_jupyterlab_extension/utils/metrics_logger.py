import os
import json
import logging
from datetime import datetime

# Configure basic logging
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)


class MetricsLogger:
    """Simple metrics logger that writes metrics directly to a log file"""

    def __init__(self, log_file_path=None):
        """Initialize the metrics logger with a log file path"""
        if log_file_path is None:
            # Default log file path
            log_dir = "/var/log/studio/jupyterlab"
            self.log_file_path = os.path.join(log_dir, "sm-jupyterlab-ext.ui.log")
        else:
            self.log_file_path = log_file_path

        # Ensure the directory exists
        try:
            os.makedirs(os.path.dirname(self.log_file_path), exist_ok=True)
            logger.info(
                f"MetricsLogger initialized with log file: {self.log_file_path}"
            )
        except Exception as e:
            logger.error(f"Failed to create log directory: {str(e)}")

    def log_metric(self, metric_data):
        """Log a metric to the log file

        Args:
            metric_data: The metric data to log (already JSON serialized)
        """
        try:
            # Try to parse the JSON to validate it
            try:
                if isinstance(metric_data, str):
                    json.loads(metric_data)
                    logger.info(f"Successfully parsed metric data JSON")
                else:
                    logger.warning(f"Metric data is not a string: {type(metric_data)}")
            except json.JSONDecodeError as e:
                logger.warning(f"Received invalid JSON: {str(e)}")

            # Write to the log file
            with open(self.log_file_path, "a") as log_file:
                log_file.write(f"{metric_data}\n")

            logger.info(f"Successfully wrote metric to {self.log_file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to log metric: {str(e)}")
            return False
