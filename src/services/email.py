from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).resolve().parent.parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email with a confirmation link to the user.

    This function generates a verification token for the given email, creates a message
    containing the token, and sends it to the provided email address with a link to
    confirm the user's email.

    Args:
        email (EmailStr): The email address of the user to send the confirmation email.
        username (str): The username of the user, which will be included in the email body.
        host (str): The host URL to be included in the email, typically the base URL of the app.

    Raises:
        ConnectionErrors: If there is a problem connecting to the mail server.
    """
    try:
        token_verification = create_email_token({"sub": email})

        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Send the message via FastMail
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        # Log the error if there's a problem with the connection
        print(err)


async def send_reset_email(email: EmailStr, reset_link: str, username: str, host: str):
    """
    Sends a password reset email to the user.

    This function creates a reset password message that includes a reset link and sends it
    to the provided email address. The email contains a link that allows the user to reset
    their password.

    Args:
        email (EmailStr): The email address of the user to send the reset email.
        reset_link (str): The URL that allows the user to reset their password.
        username (str): The username of the user, which will be included in the email body.
        host (str): The host URL to be included in the email, typically the base URL of the app.

    Raises:
        ConnectionErrors: If there is a problem connecting to the mail server.
    """
    try:
        # Create the email message
        message = MessageSchema(
            subject="Reset your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "reset_link": reset_link
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)