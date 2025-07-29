import botocore.exceptions
import re

# Pattern to match 5xx error codes.
pattern = re.compile(r"^5\d{2}$")

"""
Utility functions that determines if an error is Fault or Customer Error
"""


def is_fault(error):
    if isinstance(error, botocore.exceptions.ClientError):
        if error.response["Error"]["Code"] in ["AccessDenied"]:
            return False
        http_code = error.response["ResponseMetadata"]["HTTPStatusCode"]
        if pattern.match(str(http_code)):
            return True
        else:
            return False
    elif isinstance(error, botocore.exceptions.ConnectTimeoutError):
        return False
    return True
