import json
import pytest
import asyncio

from unittest.mock import ANY, Mock, patch, MagicMock, AsyncMock
from sagemaker_jupyterlab_extension.utils.project_clone_util import (
    _get_projects_list,
)

LIST_PROJECTS_TEST_RESPONSE = {
    "NextToken": "token",
    "ProjectSummaryList": [
        {
            "CreationTime": 12345,
            "ProjectArn": "arn:test-project",
            "ProjectDescription": "test project",
            "ProjectId": "test-project",
            "ProjectName": "test-project",
            "ProjectStatus": "CreateCompleted",
        }
    ],
}


TEST_LIST_PROJECTS_RESPONSE = ["test-project"]


class SageMakerClientMock:
    list_projects_response: any

    def __init__(self, list_projects_resp):
        self.list_projects_response = list_projects_resp

    async def list_projects(self):
        return self.list_projects_response


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.utils.project_clone_util.get_sagemaker_client")
async def test_get_domain_repositories(sagemaker_client_mock):
    sagemaker_client_mock.return_value = SageMakerClientMock(
        LIST_PROJECTS_TEST_RESPONSE
    )
    _get_projects_list.cache_clear()
    response = await _get_projects_list()
    assert response == TEST_LIST_PROJECTS_RESPONSE
