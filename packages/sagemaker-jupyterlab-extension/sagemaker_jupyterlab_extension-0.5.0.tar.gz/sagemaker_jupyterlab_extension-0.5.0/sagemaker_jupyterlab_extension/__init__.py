import json
from os import path
from pathlib import Path
from .handlers import register_handlers
from aws_embedded_metrics.config import get_config

from .utils.request_logger import log_metrics_from_request

from ._version import __version__

HERE = Path(__file__).parent.resolve()

with (HERE / "labextension" / "package.json").open(encoding="utf-8") as fid:
    data = json.load(fid)


# Path to the frontend JupyterLab extension assets
def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]


def _jupyter_server_extension_points():
    return [
        {
            "module": "sagemaker_jupyterlab_extension",
        }
    ]


# Entrypoint of the server extension
def _load_jupyter_server_extension(nb_app):
    nb_app.log.info(f"Loading SageMaker JupyterLab server extension {__version__}")
    web_app = nb_app.web_app

    # configure EMF logger
    emf_config = get_config()
    emf_config.namespace = "StudioJupyterLabExtensionServer"
    web_app.log_request = log_metrics_from_request

    register_handlers(nb_app)


load_jupyter_server_extension = _load_jupyter_server_extension
