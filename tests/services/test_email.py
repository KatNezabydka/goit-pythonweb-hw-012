import pytest
from unittest.mock import AsyncMock, patch

from src.services.email import send_email, send_reset_email

test_email = "test@example.com"
test_username = "testuser"
test_host = "http://testserver"
test_token = "mocked_token"
test_reset_link = "http://testserver/api/auth/reset-password?token=abc123"


@pytest.mark.asyncio
@patch("src.services.email.FastMail.send_message", new_callable=AsyncMock)
@patch("src.services.email.create_email_token", return_value=test_token)
async def test_send_email(mock_create_token, mock_send_message):
    await send_email(test_email, test_username, test_host)

    mock_create_token.assert_called_once_with({"sub": test_email})
    mock_send_message.assert_called_once()
    args, kwargs = mock_send_message.call_args
    assert kwargs["template_name"] == "verify_email.html"


@pytest.mark.asyncio
@patch("src.services.email.FastMail.send_message", new_callable=AsyncMock)
async def test_send_reset_email(mock_send_message):
    await send_reset_email(test_email, test_reset_link, test_username, test_host)

    mock_send_message.assert_called_once()
    args, kwargs = mock_send_message.call_args
    assert kwargs["template_name"] == "reset_password.html"
