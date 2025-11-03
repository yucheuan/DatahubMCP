import os
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Scopes for Google Sheets, Forms, and Drive
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/drive.readonly'
]

def get_credentials() -> Credentials:
    """
    Get Google API credentials with automatic token refresh.
    
    Returns:
        Google OAuth2 credentials object
        
    Note:
        - On first run, opens browser for OAuth authorization
        - Tokens are cached in token.pickle for future use
        - Automatically refreshes expired tokens
    """
    creds = None

    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, 'token.pickle')

    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    return creds


def get_sheets_service():
    """
    Get Google Sheets API service.
    
    Returns:
        Google Sheets API service object (v4)
    """
    creds = get_credentials()
    return build('sheets', 'v4', credentials=creds)


def get_forms_service():
    """
    Get Google Forms API service.
    
    Returns:
        Google Forms API service object (v1)
    """
    creds = get_credentials()
    return build('forms', 'v1', credentials=creds)


def get_drive_service():
    """
    Get Google Drive API service.
    
    Returns:
        Google Drive API service object (v3)
    """
    creds = get_credentials()
    return build('drive', 'v3', credentials=creds)

