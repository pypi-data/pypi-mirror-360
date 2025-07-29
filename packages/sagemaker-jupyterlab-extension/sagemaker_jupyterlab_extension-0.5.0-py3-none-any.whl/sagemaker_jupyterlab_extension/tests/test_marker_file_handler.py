import json
import pytest
import os
from unittest.mock import patch, MagicMock

from ..handlers import MarkerFileHandler


@pytest.fixture
def jp_server_config(jp_template_dir):
    return {
        "ServerApp": {"jpserver_extensions": {"sagemaker_jupyterlab_extension": True}},
    }


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
async def test_marker_file_get_exists(mock_exists, mock_log, jp_fetch):
    """Test GET request when marker file exists"""
    mock_log.return_value = "someInfoLog"
    mock_exists.return_value = True

    response = await jp_fetch("/aws/sagemaker/api/create-marker-file", method="GET")

    # Verify response
    assert response.code == 200
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"exists": True}

    # Verify the correct path was checked
    mock_exists.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH)


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
async def test_marker_file_get_not_exists(mock_exists, mock_log, jp_fetch):
    """Test GET request when marker file does not exist"""
    mock_log.return_value = "someInfoLog"
    mock_exists.return_value = False

    response = await jp_fetch("/aws/sagemaker/api/create-marker-file", method="GET")

    # Verify response
    assert response.code == 200
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"exists": False}

    # Verify the correct path was checked
    mock_exists.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH)


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
async def test_marker_file_get_exception(mock_exists, mock_log, jp_fetch):
    """Test GET request when an exception occurs"""
    mock_log.return_value = "someInfoLog"
    mock_exists.side_effect = Exception("Test error")

    with pytest.raises(Exception) as e:
        await jp_fetch("/aws/sagemaker/api/create-marker-file", method="GET")

    # Verify error contains expected status code
    assert "500" in str(e.value)


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
@patch("builtins.open", new_callable=MagicMock)
async def test_marker_file_post_create_success(
    mock_open, mock_exists, mock_log, jp_fetch
):
    """Test POST request when marker file doesn't exist and is created"""
    mock_log.return_value = "someInfoLog"
    mock_exists.return_value = False

    # Mock file context manager
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    response = await jp_fetch(
        "/aws/sagemaker/api/create-marker-file", method="POST", body="{}"
    )

    # Verify response
    assert response.code == 200
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"created": True}

    # Verify file operations
    mock_exists.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH)
    mock_open.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH, "w")
    mock_file.write.assert_called_once_with("")


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
@patch("builtins.open", new_callable=MagicMock)
async def test_marker_file_post_already_exists(
    mock_open, mock_exists, mock_log, jp_fetch
):
    """Test POST request when marker file already exists"""
    mock_log.return_value = "someInfoLog"
    mock_exists.return_value = True

    response = await jp_fetch(
        "/aws/sagemaker/api/create-marker-file", method="POST", body="{}"
    )

    # Verify response
    assert response.code == 200
    resp = json.loads(response.body.decode("utf-8"))
    assert resp == {"created": False}

    # Verify file operations
    mock_exists.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH)
    mock_open.assert_not_called()


@patch("sagemaker_jupyterlab_extension.handlers.MarkerFileHandler.log")
@patch("os.path.exists")
@patch("builtins.open")
async def test_marker_file_post_exception(mock_open, mock_exists, mock_log, jp_fetch):
    """Test POST request when an exception occurs during file creation"""
    mock_log.return_value = "someInfoLog"
    mock_exists.return_value = False
    mock_open.side_effect = Exception("Failed to create file")

    with pytest.raises(Exception) as e:
        await jp_fetch(
            "/aws/sagemaker/api/create-marker-file", method="POST", body="{}"
        )

    # Verify error contains expected status code
    assert "500" in str(e.value)

    # Verify file operations
    mock_exists.assert_called_once_with(MarkerFileHandler.MARKER_FILE_PATH)
