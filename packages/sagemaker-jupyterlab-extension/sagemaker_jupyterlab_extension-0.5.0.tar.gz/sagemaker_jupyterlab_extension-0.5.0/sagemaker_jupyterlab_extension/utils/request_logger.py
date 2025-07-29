import re
import json
import os
import logging
from functools import lru_cache
from .._version import __version__ as ExtVersion

from aws_embedded_metrics.logger.metrics_context import MetricsContext
from aws_embedded_metrics.serializers.log_serializer import LogSerializer
from jupyter_server.log import log_request as orig_log_request

from sagemaker_jupyterlab_extension_common.constants import (
    REQUEST_METRICS_SCHEMA,
)
from sagemaker_jupyterlab_extension_common.util.app_metadata import (
    get_domain_id,
    get_aws_account_id,
    get_space_name,
)

from sagemaker_jupyterlab_extension_common.logging.logging_utils import (
    _default_eventlog,
    SchemaDocument,
    get_handler,
)

# AppType is stored as camel-case in env. We convert it to lower case so that base url
# for jupyter-server can match regex for URIs. In logn term we would use base-url for regex matching
app_prefix = os.environ.get("SAGEMAKER_APP_TYPE", "jupyterlab").lower()


def get_http_request_event_logger():
    """
    This function builds an eventlogger for http request logging.
    It uses the HttpRequest schema defined in the SagemakerStudioJuypterLabExtensionCommon/logging/schemas/request_metrics.yml

    :get_handler(), method is defined in SagemakerStudioJuypterLabExtensionCommon/logging/logging_utils library and builds
    logging handler with FileHandler.

    :_default_event_log: returns a new instance of jupyter-event "EventLogger"

    Logging file would be /var/log/studio/jupyter-server.requests.log
    """
    schema_doc = SchemaDocument.RequestMetrics
    eventlog = _default_eventlog
    handler = get_handler(schema_doc)
    eventlog.register_handler(handler)
    # JupyterServer SchemaRegistry raises SchemaRegistryException, if schema is alredy regsitered, we
    # will catch the exception and just log warning on succcessive invocation of this method for each request.
    try:
        eventlog.register_event_schema(schema_doc.get_schema_file_path())
    except Exception as error:
        logging.warning(f"Schema is already registered {error}")
    return eventlog


"""
This is list of regex patterns that define filter pattern for the APIs that 
we want to log to CW log-groups. 

For example - it currently filters supported APIs for
- resource-plugin: aws/sagemaker/api/instance/metrics
- git plugin:  aws/sagemaker/api/git/list/repositories
- emr APIs

It is necessary to gate these APIs so we dont blowup metrics emitted into cloudwatch.
These APIs are used as metric dimension. Cloud Watch does not have limits (https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/cloudwatch_limits.html)
on number of custom metrics or values per dimension, but they do not recommend high cardinality features as dimensions.

"""
allowed_uri_patterns = [
    {
        "regex": re.compile(r"/%s/default/aws/sagemaker/api/(emr|git).*" % app_prefix),
    }
]


def default_sanitize_uri_fn(uri, match):
    grp = match.group()
    if grp is None or len(match.groups()) < 1:
        return None
    return uri


def default_sanitize_path_fn(uri, match):
    return uri


@lru_cache(maxsize=50)
def sanitize_uri_and_path(input_uri):
    """
    sanitize uri to avoid high cardinality for dimension

    caching to avoid regex comparison for frequent operations
    """
    santitized_uri = None
    santitized_path = None
    for uri in allowed_uri_patterns:
        res = uri["regex"].match(input_uri)
        if res is not None:
            santitized_uri = default_sanitize_uri_fn(input_uri, res)
            santitized_path = default_sanitize_path_fn(input_uri, res)
    return santitized_uri, santitized_path


def get_operation_from_uri(path, method):
    """
    In typical coral services service_log, for every API we have a Operation dimension
    However Jupyter APIs follow strict REST Pattern with method names and with params (like UUID) in the
    url. This method sanitizes those part and  returns URI of format
    "$HTTPMETHOD.$SanitizedURIName"
    eg:
      GET, /api/kernels -> "GET./api/kernels"
    Some operation includes customer's information. sanitized_path returns santitized path that is safe to log.
    """
    sanitized_uri, sanitized_path = sanitize_uri_and_path(path)
    if sanitized_uri is None:
        return None, sanitized_path
    return f"{method}.{sanitized_uri}", sanitized_path


def get_request_metrics_context(request, uri_path, operation, event_details):
    """
    Returns metrics dictionary in aws cloudwatch embedded format.
    """

    try:
        # namespace is already setup as part of server extension
        metrics_ctx = MetricsContext()
        metrics_ctx.put_dimensions({"Operation": operation})
        metrics_ctx.put_metric("ResponseLatencyMS", request.request_time(), "Seconds")

        status_metrics = {"Http5xx": 0, "Http2xx": 0, "Http4xx": 0}
        http_status = event_details["Status"]

        if http_status >= 500:
            status_metrics["Http5xx"] = 1
        elif http_status >= 400:
            status_metrics["Http4xx"] = 1
        else:
            # status < 300 considering as success
            status_metrics["Http2xx"] = 1

        for key in status_metrics:
            metrics_ctx.put_metric(key, status_metrics[key], "Count")

        # Added sanitized uri path to the metric
        metrics_ctx.set_property("UriPath", uri_path)
        return json.loads(LogSerializer.serialize(metrics_ctx)[0])
    except Exception as e:
        logging.warning(f"Unable to generate metrics for URI {request.path}: {e}")
        return {}


def log_metrics_from_request(handler):
    """
    Log a request to the eventlog.

    Emit EMF-format metrics, similar to LooseLeafNb2kg/StudioLab
    """
    try:
        request = handler.request
        operation, uri_path = get_operation_from_uri(request.path, request.method)
        if operation is not None:
            try:
                status_reason = handler._reason
            except AttributeError:
                # Status reason not found.
                status_reason = "[Status reason not found]"
            event = dict(
                Context=dict(
                    AccountId=get_aws_account_id(),
                    DomainId=get_domain_id(),
                    SpaceName=get_space_name(),
                    ExtensionName="SagemakerStudioJuypterLabExtensionCommon",
                    ExtensionVersion=ExtVersion,
                )
            )
            event["Status"] = handler.get_status()
            event["StatusReason"] = status_reason
            request_metrics = get_request_metrics_context(
                request, uri_path, operation, event
            )
            event.update(request_metrics)
            eventlog = getattr(handler, "eventlog", None)
            if eventlog is None:
                eventlog = get_http_request_event_logger()
            eventlog.emit(schema_id=REQUEST_METRICS_SCHEMA, data=event)
        else:
            skip_http_log_request = getattr(handler, "skip_http_log_request", False)
            if not skip_http_log_request:
                orig_log_request(handler)
    except Exception as ex:
        logging.warn(f"Error in emitting request log. Logging to operational log {ex}")
        orig_log_request(handler)
