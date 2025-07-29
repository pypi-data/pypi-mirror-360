"""SMTP utilities."""
from email.message import EmailMessage
from smtplib import SMTP


def send_msg(msg: EmailMessage, smtp_server: str = 'localhost', smtp_port: int = 0) -> None:
    """Send email message using smtp server."""
    with SMTP(smtp_server, smtp_port) as server:
        server.send_message(msg)
