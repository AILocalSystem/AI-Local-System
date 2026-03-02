import os
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Core Scopes for the Sovereign Vault & Business Profile
SCOPES = [
    'https://www.googleapis.com/auth/business.manage',  # Google Business Profile
    'https://www.googleapis.com/auth/spreadsheets',     # Sovereign Vault (Google Sheets)
    'https://www.googleapis.com/auth/drive.file'        # Google Drive (To manage the vault file)
]

def get_authenticated_service(api_name, api_version):
    """
    Centralized Authentication Utility.
    """
    creds = None
    token_path = 'token.json'
    creds_path = 'credentials.json'

def get_client_email():
    """Mocking UID/Email extraction for isolation protocol."""
    return "demo.client@example.com"

    # The file token.json stores the user's access and refresh tokens
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded external credentials from token.json")
        except ValueError as e:
            logger.warning(f"Error reading token.json: {e}")
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Access token expired. Refreshing token...")
            try:
                creds.refresh(Request())
                logger.info("Token successfully refreshed.")
            except Exception as e:
                logger.error(f"Failed to refresh token: {e}")
                creds = None
                
        # If refreshing failed or credentials never existed
        if not creds:
            logger.warning("No valid credentials. Manual re-authentication required.")
            # Triggering Graceful Failure Flag for Dashboard simulation 
            _trigger_graceful_failure()
            
            if os.path.exists(creds_path):
                logger.info(f"Initiating OAuth flow using {creds_path}")
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                logger.error(f"Missing {creds_path}! Cannot authenticate. Please download OAuth client secrets from Google Cloud Console.")
                raise FileNotFoundError(f"Missing {creds_path}")

        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            logger.info("Saved new credentials to token.json")

    # Build and return the required service
    try:
        service = build(api_name, api_version, credentials=creds)
        logger.info(f"Successfully built service: {api_name} {api_version}")
        return service
    except Exception as e:
        logger.error(f"Failed to build Google API service '{api_name}': {e}")
        raise

def _trigger_graceful_failure():
    """
    Outputs a structural payload to flag the failure
    for the Dashboard's Action Center.
    """
    payload = {
        "action": "SYSTEM_ALERT",
        "data": {
            "type": "AUTH_FAILURE",
            "message": "Re-Authentication Required. The Google OAuth token has expired or is missing.",
            "severity": "CRITICAL"
        }
    }
    # Print or log this clearly so 'dashboard.py' can pick it up
    print(f"\n[DASHBOARD_ALERT] {payload}\n")

if __name__ == '__main__':
    # Simple test execution to ensure it tries to load or auth
    try:
        print("Testing GBP Authentication...")
        service = get_authenticated_service('mybusinessbusinessinformation', 'v1')
        print("Authentication flow completed successfully.")
    except Exception as e:
        print(f"Auth test generated an expected error (likely missing credentials.json): {e}")
