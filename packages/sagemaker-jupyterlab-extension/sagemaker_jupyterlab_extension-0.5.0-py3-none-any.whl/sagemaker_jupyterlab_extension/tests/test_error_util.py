import botocore.exceptions
import re

from sagemaker_jupyterlab_extension.utils.error_util import is_fault


def test_is_fault_true():
    """Given"""
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": "SomeServiceException",
                "Message": "Details/context around the exception or error",
            },
            "ResponseMetadata": {
                "RequestId": "1234567890ABCDEF",
                "HostId": "host ID data will appear here as a hash",
                "HTTPStatusCode": 500,
                "HTTPHeaders": {"header metadata key/values will appear here"},
                "RetryAttempts": 0,
            },
        },
        "AWSSERVICEOPERATION",
    )

    expected_result = True

    """When"""
    actual_result = is_fault(error)

    """Then"""
    assert expected_result == actual_result


def test_is_fault_false_client_error():
    """Given"""
    error = botocore.exceptions.ClientError(
        {
            "Error": {
                "Code": "SomeServiceError",
                "Message": "Details/context around the exception or error",
            },
            "ResponseMetadata": {
                "RequestId": "1234567890ABCDEF",
                "HostId": "host ID data will appear here as a hash",
                "HTTPStatusCode": 400,
                "HTTPHeaders": {"header metadata key/values will appear here"},
                "RetryAttempts": 0,
            },
        },
        "AWSSERVICEOPERATION",
    )

    expected_result = False

    """When"""
    actual_result = is_fault(error)

    """Then"""
    assert expected_result == actual_result


def test_is_fault_false_connect_timeout_error():
    """Given"""
    error = botocore.exceptions.ConnectTimeoutError(endpoint_url="http")

    expected_result = False

    """When"""
    actual_result = is_fault(error)

    """Then"""
    assert expected_result == actual_result
