import os
import json
import tempfile
from sagemaker_jupyterlab_extension_common.constants import (
    REQUEST_LOG_FILE_NAME,
    LOGFILE_ENV_NAME,
)

# Create jupyterlab directory in /tmp
JUPYTERLAB_DIR = "/tmp/jupyterlab"
os.makedirs(JUPYTERLAB_DIR, exist_ok=True)

# Create the log file with the exact name expected
logfile = os.path.join(JUPYTERLAB_DIR, REQUEST_LOG_FILE_NAME)
os.environ[LOGFILE_ENV_NAME] = logfile


def get_last_entry(file_name):
    """Read the last entry from the temporary logfile"""
    log_path = os.environ[LOGFILE_ENV_NAME]
    try:
        with open(log_path) as fid:
            lines = fid.readlines()
            return json.loads(lines[-1]) if lines else {"__schema__": None}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"__schema__": None}
