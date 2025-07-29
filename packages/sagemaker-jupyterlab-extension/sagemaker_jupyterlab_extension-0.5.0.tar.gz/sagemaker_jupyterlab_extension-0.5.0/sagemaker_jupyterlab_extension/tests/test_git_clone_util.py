import json
import pytest
import asyncio

from unittest.mock import ANY, Mock, patch, MagicMock, AsyncMock
from sagemaker_jupyterlab_extension.utils.git_clone_util import (
    _get_domain_repositories,
    _get_user_profile_and_space_repositories,
    _get_space_settings,
)

DESCRIBE_USER_PROFILE_TEST_RESPONSE = {
    "UserSettings": {
        "JupyterLabAppSettings": {
            "DefaultResourceSpec": {
                "SageMakerImageArn": "arn:aws:sagemaker:us-east-2:112233445566:image/jupyter-server-3",
                "InstanceType": "system",
            },
            "CodeRepositories": [
                {"RepositoryUrl": "https://github.com/user/userprofile.git"}
            ],
        },
    }
}

DESCRIBE_USER_PROFILE_TEST_RESPONSE_NO_REPOSITORIES = {"UserSettings": {}}


DESCRIBE_DOMAIN_TEST_RESPONSE = {
    "DefaultUserSettings": {
        "JupyterLabAppSettings": {
            "DefaultResourceSpec": {
                "SageMakerImageArn": "arn:aws:sagemaker:us-east-2:112233445566:image/jupyter-server-3",
                "InstanceType": "system",
            },
            "CodeRepositories": [
                {"RepositoryUrl": "https://github.com/domain/domain.git"}
            ],
        },
    }
}

DESCRIBE_SPACE_TEST_RESPONSE = {
    "DomainId": "d-1234567890",
    "SpaceArn": "arn:aws:someArn",
    "SpaceName": "default-test-space",
    "Status": "InService",
    "LastModifiedTime": "2023-09-25T23:53:53.469000+00:00",
    "CreationTime": "2023-09-25T23:53:41.245000+00:00",
    "SpaceSettings": {
        "AppType": "JupyterLab",
        "SpaceStorageSettings": {"EbsStorageSettings": {"EbsVolumeSizeInGb": 5}},
        "JupyterLabAppSettings": {
            "CodeRepositories": [
                {"RepositoryUrl": "https://github.com/space/space-repo.git"}
            ],
        },
    },
    "OwnershipSettings": {"OwnerUserProfileName": "default-test-user-profile"},
    "SpaceSharingSettings": {"SharingType": "Private"},
}


TEST_DOMAIN_RESPONSE = ["https://github.com/domain/domain.git"]


TEST_USER_PROFILE_RESPONSE = [
    "https://github.com/user/userprofile.git",
    "https://github.com/space/space.git",
]

TEST_SPACE_SETTING_RESPONSE = {
    "CodeRepositories": ["https://github.com/space/space-repo.git"],
    "OwnerUserProfileName": "default-test-user-profile",
}


class SageMakerClientMock:
    domain_response: any
    user_profile_response: any

    def __init__(self, domain_resp, user_profile_resp, space_setting_response=None):
        self.domain_response = domain_resp
        self.user_profile_response = user_profile_resp
        self.space_setting_response = space_setting_response

    async def describe_domain(self):
        return self.domain_response

    async def describe_user_profile(self, user_profile_name=None):
        return self.user_profile_response

    async def describe_space(self):
        return self.space_setting_response


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util.get_sagemaker_client")
async def test_get_domain_repositories(sagemaker_client_mock):
    sagemaker_client_mock.return_value = SageMakerClientMock(
        DESCRIBE_DOMAIN_TEST_RESPONSE, DESCRIBE_USER_PROFILE_TEST_RESPONSE
    )
    _get_domain_repositories.cache_clear()
    response = await _get_domain_repositories()
    assert response == TEST_DOMAIN_RESPONSE


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util.get_sagemaker_client")
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
async def test_get_user_profile_repositories(mock_get_space, sagemaker_client_mock):
    sagemaker_client_mock.return_value = SageMakerClientMock(
        DESCRIBE_DOMAIN_TEST_RESPONSE, DESCRIBE_USER_PROFILE_TEST_RESPONSE
    )
    mock_get_space.return_value = {
        "CodeRepositories": ["https://github.com/space/space.git"],
        "OwnerUserProfileName": "test-profile",
    }
    _get_user_profile_and_space_repositories.cache_clear()
    response = await _get_user_profile_and_space_repositories()
    assert response == TEST_USER_PROFILE_RESPONSE


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util.get_sagemaker_client")
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
async def test_get_user_profile_repositories_return_empty_json(
    mock_get_space, sagemaker_client_mock
):
    sagemaker_client_mock.return_value = SageMakerClientMock(
        DESCRIBE_DOMAIN_TEST_RESPONSE,
        DESCRIBE_USER_PROFILE_TEST_RESPONSE_NO_REPOSITORIES,
    )
    mock_get_space.return_value = {
        "CodeRepositories": [],
        "OwnerUserProfileName": "test-profile",
    }
    _get_user_profile_and_space_repositories.cache_clear()
    response = await _get_user_profile_and_space_repositories()
    assert response == []


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util.get_sagemaker_client")
async def test_get_space_settings(sagemaker_client_mock):
    sagemaker_client_mock.return_value = SageMakerClientMock(
        DESCRIBE_DOMAIN_TEST_RESPONSE,
        DESCRIBE_USER_PROFILE_TEST_RESPONSE,
        DESCRIBE_SPACE_TEST_RESPONSE,
    )
    _get_space_settings.cache_clear()
    response = await _get_space_settings()
    assert response == TEST_SPACE_SETTING_RESPONSE
