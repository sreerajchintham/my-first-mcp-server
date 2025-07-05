from dotenv import load_dotenv
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

# Load environment variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GOOGLE_CREDENTIALS_DIR = os.getenv("GOOGLE_CREDENTIALS_DIR")
GOOGLE_TOKEN_FILE = os.path.join(os.getenv("GOOGLE_CREDENTIALS_DIR", "CREDENTIALS"), "token.json")

# Test GitHub token
if GITHUB_TOKEN:
    print(f"GitHub token: {GITHUB_TOKEN}")
    print("GitHub token loaded successfully")
else:
    print("Error: GITHUB_TOKEN not found")

# Test Google credentials
try:
    print(f"Google token file: {GOOGLE_TOKEN_FILE}")
    creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE)
    drive_service = build("drive", "v3", credentials=creds)
    print("Google Drive API initialized successfully")
except Exception as e:
    print(f"Error initializing Google Drive API: {e}")

if __name__ == "__main__":
    print("Environment setup verification complete")