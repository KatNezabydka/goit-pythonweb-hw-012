import pytest
from unittest.mock import patch, MagicMock

from src.services.upload_file import UploadFileService


@pytest.fixture
def cloudinary_config():
    return {
        "cloud_name": "demo",
        "api_key": "123456789",
        "api_secret": "supersecret"
    }


@patch("cloudinary.config")
def test_init_upload_file_service(mock_config, cloudinary_config):
    service = UploadFileService(**cloudinary_config)

    mock_config.assert_called_once_with(
        cloud_name="demo",
        api_key="123456789",
        api_secret="supersecret",
        secure=True
    )


@patch("cloudinary.uploader.upload")
@patch("cloudinary.CloudinaryImage.build_url")
def test_upload_file(mock_build_url, mock_upload):
    mock_upload.return_value = {"version": "123456"}
    mock_build_url.return_value = "https://res.cloudinary.com/demo/image/upload/v123456/RestApp/testuser"

    file_mock = MagicMock()
    file_mock.file = "dummy_file_stream"

    result = UploadFileService.upload_file(file_mock, "testuser")

    mock_upload.assert_called_once_with(
        "dummy_file_stream",
        public_id="RestApp/testuser",
        overwrite=True
    )

    mock_build_url.assert_called_once_with(
        width=250,
        height=250,
        crop="fill",
        version="123456"
    )

    assert result == "https://res.cloudinary.com/demo/image/upload/v123456/RestApp/testuser"
