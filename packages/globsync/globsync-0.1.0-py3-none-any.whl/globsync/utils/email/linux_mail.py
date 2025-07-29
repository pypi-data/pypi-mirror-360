"""Email utilities."""
from email.message import EmailMessage
import subprocess


def send_msg(msg: EmailMessage) -> None:
    """Send email using the Linux system's mail application."""
    sender = msg["Reply-To"]
    subject = msg["Subject"]
    receiver = msg["To"]
    body = msg.get_content()
    command = f'echo "{body}" | mail -S replyto="{sender}" -s "{subject}" {receiver}'
    subprocess.run(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
