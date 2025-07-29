"""Email utilities."""
import os.path
from jinja2 import Environment, FileSystemLoader
from email.message import EmailMessage
from typing import Any

from globsync import utils
import globsync.utils.email.smtp
import globsync.utils.email.linux_mail
import globsync.utils.email.gmail
import globsync.utils.email.office365
from globsync.utils.logging import log


def create_body(template_file: str, data: dict[str, Any]) -> str:
    """Create message body from template."""
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
    template = env.get_template(template_file)
    body = template.render(**data)
    return body


def create_msg(sender: str, receiver: str, subject: str, subtype2body: str) -> EmailMessage:
    """Create email message."""
    msg = EmailMessage()
    msg["To"] = receiver
    msg["From"] = sender
    msg["Reply-To"] = sender
    msg["Subject"] = subject
    msg.set_content(subtype2body.get('plain', ''))
    for subtype, body in subtype2body.items():
        if subtype == 'plain':
            continue
        msg.add_alternative(body, subtype=subtype)
    return msg


def send_msg(msg: EmailMessage, backend: str = "gmail", **kwargs) -> None:
    """Send email message."""
    try:
        if backend == "smtp":
            globsync.utils.email.smtp.send_msg(msg, **kwargs)
        elif backend == "linux_mail":
            globsync.utils.email.linux_mail.send_msg(msg, **kwargs)
        elif backend == "gmail":
            gmail_secrets_file = kwargs.get('gmail_secrets_file', None)
            assert gmail_secrets_file is not None
            globsync.utils.email.gmail.send_msg(msg, gmail_secrets_file)
        elif backend == "office365":
            globsync.utils.email.office365.send_msg(msg, **kwargs)
    except Exception as error:
        log("error", f'Failed to send email, following error occurred: {error}')
    else:
        log("info", f'Email sent successfully to {msg["To"]}.')
