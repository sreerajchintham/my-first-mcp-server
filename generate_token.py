from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import json

# Path to your client secret file
CLIENT_SECRET_FILE = os.path.join(os.getenv("GOOGLE_CREDENTIALS_DIR", "CREDENTIALS"), "client_secret.json")
TOKEN_FILE = os.path.join(os.getenv("GOOGLE_CREDENTIALS_DIR", "CREDENTIALS"), "token.json")
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def generate_token():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    print("Token generated successfully at:", TOKEN_FILE)

if __name__ == "__main__":
    generate_token()