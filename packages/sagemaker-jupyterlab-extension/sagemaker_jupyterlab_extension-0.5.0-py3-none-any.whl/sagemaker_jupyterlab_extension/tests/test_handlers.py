import json
import pytest
import asyncio

from unittest.mock import ANY, Mock, patch, MagicMock, AsyncMock
from ..handlers import (
    register_handlers,
    InstanceMetricsHandler,
    GitCloneHandler,
    ProjectCloneHandler,
    CustomMetricsHandler,
    MarkerFileHandler,
    EnvironmentHandler,
)


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {"jpserver_extensions": {"sagemaker_jupyterlab_extension": True}},
    }


def test_mapping_added():
    mock_nb_app = Mock()
    mock_web_app = Mock()
    mock_nb_app.web_app = mock_web_app
    mock_web_app.settings = {"base_url": "nb_base_url"}
    register_handlers(mock_nb_app)
    mock_web_app.add_handlers.assert_called_once_with(".*$", ANY)


# We need to mock the log method from handler class to prevent from invoking
# internal code from common package during unit testing.
@patch("sagemaker_jupyterlab_extension.handlers.InstanceMetricsHandler.log")
async def test_get_instance_metrics_success(mock_logger, jp_fetch):
    mock_logger.return_value = "someInfoLog"
    response = await jp_fetch("/aws/sagemaker/api/instance/metrics", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert response.code == 200

    # Assert metric attributes are present metrics is populated
    metrics_object = resp["metrics"]
    assert "memory" in metrics_object
    assert "cpu" in metrics_object
    assert "storage" in metrics_object

    # Assert attributes of memory present
    memory_metric = resp["metrics"]["memory"]
    assert memory_metric is not None
    assert "rss_in_bytes" in memory_metric
    assert "total_in_bytes" in memory_metric
    assert "memory_percentage" in memory_metric

    # Assert CPU metrics is populated
    cpu_metric = resp["metrics"]["cpu"]
    assert cpu_metric is not None
    assert "cpu_count" in cpu_metric
    assert "cpu_percentage" in cpu_metric

    # Assert Disk usage metrics is populated
    storage_metric = resp["metrics"]["storage"]
    assert storage_metric is not None


@patch.object(
    InstanceMetricsHandler, "get", side_effect=Exception("No parent process found")
)
async def test_get_instance_metrics_failed(jp_fetch):
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/instance/metrics", method="GET")
    assert str(e.value) == "No parent process found"


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.handlers._get_domain_repositories")
@patch(
    "sagemaker_jupyterlab_extension.handlers._get_user_profile_and_space_repositories"
)
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
@patch(
    "sagemaker_jupyterlab_extension.handlers.GitCloneHandler.log",
    return_value="infoLogs",
)
async def test_get_git_repositories_empty_userprofile_repositories_success(
    mock_logger,
    mock_get_space_settings,
    mock_get_profile_repositories,
    mock_get_domain_repo,
    jp_fetch,
):
    mock_get_domain_repo.return_value = ["https://github.com/domain/domain.git"]
    mock_get_space_settings.return_value = {
        "CodeRepositories": [],
        "OwnerUserProfileName": "test-profile",
    }
    mock_get_profile_repositories.return_value = []
    response = await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"GitCodeRepositories": ["https://github.com/domain/domain.git"]}


@pytest.mark.asyncio
@patch(
    "sagemaker_jupyterlab_extension.handlers.GitCloneHandler.log",
    return_value="infoLogs",
)
async def test_get_environment_md_success(mock_logger, jp_fetch):
    with (
        patch(
            "sagemaker_jupyterlab_extension_common.util.environment.EnvironmentDetector.get_environment"
        ) as mock_get_env,
        patch(
            "sagemaker_jupyterlab_extension_common.util.environment.EnvironmentDetector.is_md_environment"
        ) as mock_is_md,
    ):
        mock_is_md.return_value = True
        response = await jp_fetch("/aws/sagemaker/api/is-md-environment", method="GET")
        assert response.code == 200

        resp = json.loads(response.body.decode())
        assert resp == {"isMaxDomeEnvironment": True}


@pytest.mark.asyncio
async def test_get_environment_non_md_success(jp_fetch):
    with (
        patch(
            "sagemaker_jupyterlab_extension_common.util.environment.EnvironmentDetector.get_environment"
        ) as mock_get_env,
        patch(
            "sagemaker_jupyterlab_extension_common.util.environment.EnvironmentDetector.is_md_environment"
        ) as mock_is_md,
    ):
        mock_is_md.return_value = False

        response = await jp_fetch("/aws/sagemaker/api/is-md-environment", method="GET")
        assert response.code == 200

        resp = json.loads(response.body.decode())
        assert resp == {"isMaxDomeEnvironment": False}


@pytest.mark.asyncio
async def test_get_environment_error(jp_fetch):
    with patch(
        "sagemaker_jupyterlab_extension_common.util.environment.EnvironmentDetector.get_environment"
    ) as mock_get_env:
        error_message = "Test environment detection error"

        async def async_error():
            raise Exception(error_message)

        mock_get_env.side_effect = async_error

        with pytest.raises(Exception) as exc_info:
            await jp_fetch("/aws/sagemaker/api/is-md-environment", method="GET")

        assert "500" in str(exc_info.value)


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.handlers._get_domain_repositories")
@patch(
    "sagemaker_jupyterlab_extension.handlers._get_user_profile_and_space_repositories"
)
@patch("sagemaker_jupyterlab_extension.utils.git_clone_util._get_space_settings")
@patch(
    "sagemaker_jupyterlab_extension.handlers.GitCloneHandler.log",
    return_value="someInfoLog",
)
async def test_get_git_repositories_success(
    mock_logger,
    mock_get_space_settings,
    mock_get_profile_repositories,
    mock_get_domain_repo,
    jp_fetch,
):
    mock_get_domain_repo.return_value = ["https://github.com/domain/domain.git"]
    mock_get_space_settings.return_value = {
        "CodeRepositories": ["https://github.com/space/space.git"],
        "OwnerUserProfileName": "test-profile",
    }
    mock_get_profile_repositories.return_value = [
        "https://github.com/user/userprofile.git",
        "https://github.com/space/space.git",
    ]
    response = await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert resp.get("GitCodeRepositories") is not None
    assert set(resp.get("GitCodeRepositories")) == set(
        [
            "https://github.com/domain/domain.git",
            "https://github.com/user/userprofile.git",
            "https://github.com/space/space.git",
        ]
    )


@patch.object(
    GitCloneHandler, "get", side_effect=Exception("Internal Server error occurred")
)
async def test_get_git_repositories_failure(jp_fetch):
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/git/list-repositories", method="GET")
    assert str(e.value) == "Internal Server error occurred"


@pytest.mark.asyncio
@patch("sagemaker_jupyterlab_extension.handlers._get_projects_list")
@patch(
    "sagemaker_jupyterlab_extension.handlers.ProjectCloneHandler.log",
    return_value="someInfoLog",
)
async def test_get_projects_list_success(
    mock_logger,
    mock_get_projects_list,
    jp_fetch,
):
    mock_get_projects_list.return_value = ["test-project", "test-project2"]
    response = await jp_fetch("/aws/sagemaker/api/projects/list-projects", method="GET")
    resp = json.loads(response.body.decode("utf-8"))
    assert resp.get("projectsList") is not None
    assert set(resp.get("projectsList")) == set(["test-project", "test-project2"])


@patch.object(
    ProjectCloneHandler, "get", side_effect=Exception("Internal Server error occurred")
)
async def test_get_projects_list_failure(jp_fetch):
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/projects/list-projects", method="GET")
    assert str(e.value) == "Internal Server error occurred"


@patch("sagemaker_jupyterlab_extension.handlers.CustomMetricsHandler.log")
@patch.object(CustomMetricsHandler, "get_metrics_logger")
async def test_custom_metrics_post_success(mock_get_logger, mock_log, jp_fetch):
    # Setup mock logger
    mock_logger = MagicMock()
    mock_logger.log_metric.return_value = True
    mock_get_logger.return_value = mock_logger

    # Test POST request
    test_data = json.dumps({"metric": "test", "value": 1})
    response = await jp_fetch(
        "/aws/sagemaker/api/add-metrics", method="POST", body=test_data
    )

    # Verify response
    assert response.code == 204
    mock_logger.log_metric.assert_called_once()


@patch("sagemaker_jupyterlab_extension.handlers.CustomMetricsHandler.log")
@patch.object(CustomMetricsHandler, "get_metrics_logger")
async def test_custom_metrics_post_failure(mock_get_logger, mock_log, jp_fetch):
    # Setup mock logger to return failure
    mock_logger = MagicMock()
    mock_logger.log_metric.return_value = False
    mock_get_logger.return_value = mock_logger

    # Test POST request
    test_data = json.dumps({"metric": "test", "value": 1})

    # Use pytest.raises to catch the expected HTTP error
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/add-metrics", method="POST", body=test_data)

    # Verify the error contains the expected message
    assert "500" in str(e.value)


@patch("sagemaker_jupyterlab_extension.handlers.CustomMetricsHandler.log")
@patch.object(CustomMetricsHandler, "get_metrics_logger")
async def test_custom_metrics_post_exception(mock_get_logger, mock_log, jp_fetch):
    # Setup mock logger to raise exception
    mock_logger = MagicMock()
    mock_logger.log_metric.side_effect = Exception("Test error")
    mock_get_logger.return_value = mock_logger

    # Test POST request
    test_data = json.dumps({"metric": "test", "value": 1})

    # Use pytest.raises to catch the expected HTTP error
    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/add-metrics", method="POST", body=test_data)

    # Verify the error contains the expected status code
    assert "500" in str(e.value)


async def test_custom_metrics_options(jp_fetch):
    # Test OPTIONS request for CORS
    response = await jp_fetch("/aws/sagemaker/api/add-metrics", method="OPTIONS")

    # Verify response
    assert response.code == 204
    assert response.headers.get("Access-Control-Allow-Origin") == "*"
    assert response.headers.get("Access-Control-Allow-Methods") == "POST, OPTIONS"
    assert response.headers.get("Access-Control-Allow-Headers") == "Content-Type"


def test_custom_metrics_handler_singleton():
    # Test that the metrics logger is a singleton
    # First reset the singleton
    CustomMetricsHandler._metrics_logger = None

    # Mock the MetricsLogger class
    with patch(
        "sagemaker_jupyterlab_extension.utils.metrics_logger.MetricsLogger"
    ) as mock_metrics_logger:
        mock_instance = MagicMock()
        mock_metrics_logger.return_value = mock_instance

        # Create a method to get the logger that doesn't require handler instantiation
        logger1 = CustomMetricsHandler.get_metrics_logger(CustomMetricsHandler)
        mock_metrics_logger.assert_called_once()

        # Second call should return the existing logger
        logger2 = CustomMetricsHandler.get_metrics_logger(CustomMetricsHandler)
        mock_metrics_logger.assert_called_once()  # Still only called once

        # Both calls should return the same logger instance
        assert logger1 is logger2
        assert logger1 is mock_instance
