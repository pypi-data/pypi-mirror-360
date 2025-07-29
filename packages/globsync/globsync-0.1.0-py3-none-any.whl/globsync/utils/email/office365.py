"""Office365 utilities."""
from email.message import EmailMessage
from smtplib import SMTP


def send_msg(msg: EmailMessage, smtp_server: str = 'smtp.office365.com', smtp_port: int = 587, username: str = "u0050435", password: str = "password") -> None:
    """Send email message using Office365 smtp server."""
    with SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)

