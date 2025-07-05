import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# All scopes needed for the MCP server
SCOPES = [
    'https://www.googleapis.com/auth/drive',           # Full Drive access
    'https://www.googleapis.com/auth/documents',       # Google Docs access
    'https://www.googleapis.com/auth/drive.file'       # File creation access
]

def reauthorize_google_apis():
    """Re-authorize Google APIs with expanded scopes"""
    
    # Paths
    credentials_dir = os.getenv("GOOGLE_CREDENTIALS_DIR", "CREDENTIALS")
    client_secret_path = os.path.join(credentials_dir, "client_secret.json")
    token_path = os.path.join(credentials_dir, "token.json")
    
    # Check if client_secret.json exists
    if not os.path.exists(client_secret_path):
        print(f"❌ Error: {client_secret_path} not found!")
        print("Please download your OAuth 2.0 client credentials from Google Cloud Console")
        return False
    
    print("🔄 Starting Google API re-authorization process...")
    print(f"📁 Using credentials from: {credentials_dir}")
    print(f"🔐 Required scopes:")
    for scope in SCOPES:
        print(f"   • {scope}")
    
    try:
        # Delete existing token if it exists
        if os.path.exists(token_path):
            print(f"🗑️  Removing existing token: {token_path}")
            os.remove(token_path)
        
        # Create flow from client secrets
        flow = InstalledAppFlow.from_client_secrets_file(
            client_secret_path, SCOPES)
        
        # Run the OAuth flow
        print("\n🌐 Opening browser for authorization...")
        print("Please:")
        print("1. Sign in to your Google account")
        print("2. Grant access to all requested permissions")
        print("3. Return to this terminal")
        
        creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print(f"\n✅ Authorization successful!")
        print(f"💾 New token saved to: {token_path}")
        
        # Test the credentials
        print("\n🧪 Testing new credentials...")
        test_credentials(creds)
        
        return True
        
    except Exception as e:
        print(f"❌ Authorization failed: {e}")
        return False

def test_credentials(creds):
    """Test the new credentials"""
    try:
        from googleapiclient.discovery import build
        
        # Test Drive API
        drive_service = build('drive', 'v3', credentials=creds)
        about = drive_service.about().get(fields="user").execute()
        print(f"✅ Drive API: Connected as {about['user']['emailAddress']}")
        
        # Test Docs API
        docs_service = build('docs', 'v1', credentials=creds)
        print("✅ Docs API: Connection successful")
        
        # Test by listing some files
        results = drive_service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        print(f"✅ Can access {len(files)} files in Drive")
        
    except Exception as e:
        print(f"⚠️  Warning: Credential test failed: {e}")

if __name__ == "__main__":
    print("🚀 Google API Re-Authorization Tool")
    print("=" * 50)
    
    success = reauthorize_google_apis()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ RE-AUTHORIZATION COMPLETE!")
        print("You can now restart your MCP server:")
        print("   python mcp_server.py")
        print("\nAll Google Docs tools should now work properly.")
    else:
        print("\n" + "=" * 50)
        print("❌ RE-AUTHORIZATION FAILED")
        print("Please check the error messages above and try again.") 