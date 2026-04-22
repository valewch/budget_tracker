import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only access is enough for your expense tracker
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def get_service():
    """
    Authenticates user and returns Gmail API service object.
    Creates token.json on first run.
    """

    creds = None

    # 1. Load existing token if available
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 2. If no valid credentials, start OAuth flow
    if not creds or not creds.valid:

        # Refresh token if expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # First-time login flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next runs
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # 3. Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    return service