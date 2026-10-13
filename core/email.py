import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from core.config import EMAIL_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USER

logger = logging.getLogger("uvicorn.error")


# Build the FastAPI-Mail connection settings from the .env values
def _get_mailer() -> FastMail:
    config = ConnectionConfig(
        MAIL_USERNAME=SMTP_USER,
        MAIL_PASSWORD=SMTP_PASSWORD,
        MAIL_FROM=EMAIL_FROM,
        MAIL_SERVER=SMTP_HOST,
        MAIL_PORT=SMTP_PORT,
        MAIL_STARTTLS=True,  # port 587 uses STARTTLS
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )
    return FastMail(config)


# Send one plain-text email with FastAPI-Mail.
# It never raises: a mail problem must not break the request that triggered it.
async def send_email(to: str, subject: str, body: str) -> None:
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Email not configured (SMTP_USER/SMTP_PASSWORD); skipped email to %s", to)
        return

    message = MessageSchema(
        subject=subject, recipients=[to], body=body, subtype=MessageType.plain
    )
    try:
        await _get_mailer().send_message(message)
    except Exception:
        logger.exception("Failed to send email to %s", to)


async def send_welcome_email(to: str, username: str) -> None:
    await send_email(
        to=to,
        subject="Welcome!",
        body=f"Hi {username},\n\nYour account has been created successfully. You can now log in.\n",
    )
