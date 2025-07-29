import os
import pytest
from unittest.mock import patch, MagicMock
from ..utils.request_logger import (
    sanitize_uri_and_path,
    get_operation_from_uri,
    get_request_metrics_context,
    log_metrics_from_request,
)

from .helper import (
    get_last_entry,
)

from sagemaker_jupyterlab_extension_common.constants import (
    REQUEST_METRICS_SCHEMA,
)
from sagemaker_jupyterlab_extension_common.constants import (
    REQUEST_METRICS_SCHEMA,
    LOGFILE_ENV_NAME,
    REQUEST_LOG_FILE_NAME,
)


@pytest.fixture
def mock_eventlogger():
    mock_logger = MagicMock()
    with patch(
        "sagemaker_jupyterlab_extension.utils.request_logger.get_http_request_event_logger",
        return_value=mock_logger,
    ):
        yield mock_logger


class MockHandler:
    """Minimal API for a handler"""

    def get_status(self):
        return 200


class MockRequest:
    """Minimal API to for a request"""

    uri = "foo"
    path = "foo"
    method = "GET"
    remote_ip = "1.1.1.1"

    def request_time(self):
        return 0.1


def test_sanitize_uri_and_path():
    test_cases = [
        # [ input, expected ]
        [
            "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
            (
                "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
            ),
        ],
        [
            "/jupyterlab/default/aws/sagemaker/api/instance/metrics",
            (None, None),
        ],
        [
            "/jupyterlab/default/aws/sagemaker/api/emr/describe-cluster",
            (
                "/jupyterlab/default/aws/sagemaker/api/emr/describe-cluster",
                "/jupyterlab/default/aws/sagemaker/api/emr/describe-cluster",
            ),
        ],
        [
            "/jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
            (
                "/jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
                "/jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
            ),
        ],
        # [returns None,as due to apptype name case mismatch, regex will not match. JupyterLab != jupyterlab]
        [
            "/Jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
            (
                None,
                None,
            ),
        ],
        ["/jupyterlab/default/api-that-should-not-be-logged", (None, None)],
    ]
    for test_case in test_cases:
        res = sanitize_uri_and_path(test_case[0])
        assert res == test_case[1]


def test_get_operation_from_uri():
    test_cases = [
        # [ input, expected ]
        [
            ("/jupyterlab/default/aws/sagemaker/api/git/list-repositories", "GET"),
            (
                "GET./jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
            ),
        ],
        [
            ("/jupyterlab/default/aws/sagemaker/api/instance/metrics", "GET"),
            (
                None,
                None,
            ),
        ],
        [
            ("/jupyterlab/default/aws/sagemaker/api/emr/describe-cluster", "POST"),
            (
                "POST./jupyterlab/default/aws/sagemaker/api/emr/describe-cluster",
                "/jupyterlab/default/aws/sagemaker/api/emr/describe-cluster",
            ),
        ],
        [
            ("/jupyterlab/default/aws/sagemaker/api/emr/list-clusters", "POST"),
            (
                "POST./jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
                "/jupyterlab/default/aws/sagemaker/api/emr/list-clusters",
            ),
        ],
        ["/jupyterlab/default/aws/some-random-api", (None, None)],
        ["/jupyterlab/default/jupyter/internal-api", (None, None)],
    ]
    for test_case in test_cases:
        res = get_operation_from_uri(test_case[0][0], test_case[0][1])
        assert res == test_case[1]


def test_get_request_metrics_context():
    # [ input, expected ]
    test_cases = [
        [
            (
                "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "GET./jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                dict(
                    DomainId="test-domain-id",
                    Status=200,
                    StatusReason="OK",
                ),
            ),
            {
                "Http2xx": 1,
                "Http4xx": 0,
                "Http5xx": 0,
                "Operation": "GET./jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "ResponseLatencyMS": 0.1,
                "UriPath": "/jupyterlab/default/aws/sagemaker/api/git/list-repositories",
                "_aws": {
                    "CloudWatchMetrics": [
                        {
                            "Dimensions": [["Operation"]],
                            "Metrics": [
                                {"Name": "ResponseLatencyMS", "Unit": "Seconds"},
                                {"Name": "Http5xx", "Unit": "Count"},
                                {"Name": "Http2xx", "Unit": "Count"},
                                {"Name": "Http4xx", "Unit": "Count"},
                            ],
                            "Namespace": "StudioJupyterLabExtensionServer",
                        }
                    ],
                    "Timestamp": 123456,
                },
            },
        ]
    ]
    for test_case in test_cases:
        request = MockRequest()
        request.uri = test_case[0][0]
        res = get_request_metrics_context(
            request, test_case[0][1], test_case[0][2], test_case[0][3]
        )
        res["_aws"]["Timestamp"] = 123456
        assert res == test_case[1]


@patch(
    "sagemaker_jupyterlab_extension.utils.request_logger.get_domain_id",
    return_value="d-jk12345678",
)
@patch(
    "sagemaker_jupyterlab_extension.utils.request_logger.get_aws_account_id",
    return_value="1234567890",
)
@patch(
    "sagemaker_jupyterlab_extension.utils.request_logger.get_space_name",
    return_value="default-space",
)
def test_log_request(
    mock_space,
    mock_aws_account,
    mock_domain,
    mock_eventlogger,
):
    handler = MockHandler()
    request = MockRequest()
    request.path = "/jupyterlab/default/aws/sagemaker/api/git/list-repositories"
    request.method = "GET"
    handler.request = request

    # Log the metric event
    log_metrics_from_request(handler)

    # Verify the event logger was called with correct data
    mock_eventlogger.emit.assert_called_once()
    call_args = mock_eventlogger.emit.call_args[1]

    assert call_args["schema_id"] == REQUEST_METRICS_SCHEMA
    data = call_args["data"]
    assert data["Status"] == 200
    assert data["Context"]["AccountId"] == "1234567890"
    assert data["Context"]["DomainId"] == "d-jk12345678"
    assert data["Context"]["SpaceName"] == "default-space"
    data["_aws"]["Timestamp"] = 123456

    assert data["_aws"] == {
        "CloudWatchMetrics": [
            {
                "Dimensions": [["Operation"]],
                "Metrics": [
                    {"Name": "ResponseLatencyMS", "Unit": "Seconds"},
                    {"Name": "Http5xx", "Unit": "Count"},
                    {"Name": "Http2xx", "Unit": "Count"},
                    {"Name": "Http4xx", "Unit": "Count"},
                ],
                "Namespace": "StudioJupyterLabExtensionServer",
            }
        ],
        "Timestamp": 123456,
    }
