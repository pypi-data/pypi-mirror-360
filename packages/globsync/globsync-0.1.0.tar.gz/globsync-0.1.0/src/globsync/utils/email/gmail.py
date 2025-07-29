"""Gmail utilities."""
import os
import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail(gmail_secrets_file: str) -> Credentials:
    """Get Gmail credentials."""
    creds = None
    gmail_token_file = os.path.join(os.path.dirname(gmail_secrets_file), 'gmail_token')
    if os.path.exists(gmail_token_file):
        creds = Credentials.from_authorized_user_file(gmail_token_file, SCOPES)
    else:
        with open(gmail_token_file, 'w') as f:
            pass
        os.chmod(gmail_token_file, 0o600)
    if not creds or not creds.valid:
        refresh_creds = True
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refresh_creds = False
            except:
                pass
        if refresh_creds:
            flow = InstalledAppFlow.from_client_secrets_file(gmail_secrets_file, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            auth_url, _ = flow.authorization_url(prompt='consent')
            print(f'Please go to this URL: {auth_url}')
            code = input('Enter the authorization code: ')
            flow.fetch_token(code=code)
            creds = flow.credentials
        assert(creds and creds.valid)
        with open(gmail_token_file, 'w') as f:
            f.write(creds.to_json())
    return creds


def send_msg(msg: EmailMessage, gmail_secrets_file: str) -> None:
    """Send email message using Gmail API."""
    creds = authenticate_gmail(gmail_secrets_file)
    service = build('gmail', 'v1', credentials=creds)
    service.users().messages().send(userId='me', body={'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}).execute()
