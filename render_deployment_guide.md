# Deploying MCP Server to Render

## Prerequisites

Before deploying to Render, make sure you have:
1. Your Google OAuth credentials (`client_secret.json` and `token.json`)
2. A GitHub Personal Access Token
3. A Google Gemini API key
4. A Render account

## Environment Variables Setup

### Required Environment Variables

Add these environment variables in your Render service settings:

```
GOOGLE_CREDENTIALS_DIR=/app/credentials
GOOGLE_TOKEN_FILE=token.json
GITHUB_TOKEN=your_github_personal_access_token
GEMINI_API_KEY=your_gemini_api_key
```

### Steps to Add Environment Variables in Render:

1. Go to your Render dashboard
2. Select your service
3. Go to "Environment" tab
4. Add each variable with the name and value

## Credential Files Setup

Since `token.json` and `client_secret.json` contain sensitive data, you have several options:

### Option 1: Environment Variables (Recommended)

Convert your credential files to environment variables:

1. **For `token.json`:**
   ```bash
   # Convert to base64
   cat CREDENTIALS/token.json | base64
   ```
   Add as environment variable: `GOOGLE_TOKEN_BASE64=<base64_encoded_content>`

2. **For `client_secret.json`:**
   ```bash
   # Convert to base64
   cat CREDENTIALS/client_secret.json | base64
   ```
   Add as environment variable: `GOOGLE_CLIENT_SECRET_BASE64=<base64_encoded_content>`

### Option 2: Modify Server Code to Use Environment Variables

Update your `mcp_server.py` to decode credentials from environment variables:

```python
import base64
import json
import tempfile

# Add this after the existing environment variable setup
def setup_credentials():
    """Setup Google credentials from environment variables"""
    credentials_dir = "/app/credentials"
    os.makedirs(credentials_dir, exist_ok=True)
    
    # Decode and write token.json
    token_base64 = os.getenv("GOOGLE_TOKEN_BASE64")
    if token_base64:
        token_content = base64.b64decode(token_base64).decode('utf-8')
        with open(os.path.join(credentials_dir, "token.json"), 'w') as f:
            f.write(token_content)
    
    # Decode and write client_secret.json
    client_secret_base64 = os.getenv("GOOGLE_CLIENT_SECRET_BASE64")
    if client_secret_base64:
        client_secret_content = base64.b64decode(client_secret_base64).decode('utf-8')
        with open(os.path.join(credentials_dir, "client_secret.json"), 'w') as f:
            f.write(client_secret_content)

# Call this function before initializing Google APIs
setup_credentials()
```

## Deployment Files

### 1. Create `render.yaml` (Optional)

```yaml
services:
  - type: web
    name: mcp-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python mcp_server.py
    envVars:
      - key: GOOGLE_CREDENTIALS_DIR
        value: /app/credentials
      - key: GOOGLE_TOKEN_FILE
        value: token.json
      - key: GITHUB_TOKEN
        fromDatabase:
          name: github-token
          property: connectionString
      - key: GEMINI_API_KEY
        fromDatabase:
          name: gemini-key
          property: connectionString
```

### 2. Update `requirements.txt`

Make sure your `requirements.txt` includes all necessary dependencies:

```
mcp>=1.10.0
google-auth>=2.15.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.2.0
google-api-python-client>=2.100.0
google-generativeai>=0.8.0
PyGithub>=2.0.0
python-dotenv>=1.0.0
requests>=2.28.0
pydantic>=2.0.0
anyio>=3.0.0
uvicorn>=0.20.0
```

### 3. Create `Procfile` (if needed)

```
web: python mcp_server.py
```

## Modified Server Code

Here's the updated server initialization code that handles credentials from environment variables:

```python
import os
import base64
import json
from pathlib import Path

def setup_credentials():
    """Setup Google credentials from environment variables for Render deployment"""
    credentials_dir = os.getenv("GOOGLE_CREDENTIALS_DIR", "/app/credentials")
    os.makedirs(credentials_dir, exist_ok=True)
    
    # Setup token.json from environment variable
    token_base64 = os.getenv("GOOGLE_TOKEN_BASE64")
    if token_base64:
        try:
            token_content = base64.b64decode(token_base64).decode('utf-8')
            token_path = os.path.join(credentials_dir, "token.json")
            with open(token_path, 'w') as f:
                f.write(token_content)
            logger.info(f"Created token.json at {token_path}")
        except Exception as e:
            logger.error(f"Failed to setup token.json: {e}")
    
    # Setup client_secret.json from environment variable
    client_secret_base64 = os.getenv("GOOGLE_CLIENT_SECRET_BASE64")
    if client_secret_base64:
        try:
            client_secret_content = base64.b64decode(client_secret_base64).decode('utf-8')
            client_secret_path = os.path.join(credentials_dir, "client_secret.json")
            with open(client_secret_path, 'w') as f:
                f.write(client_secret_content)
            logger.info(f"Created client_secret.json at {client_secret_path}")
        except Exception as e:
            logger.error(f"Failed to setup client_secret.json: {e}")

# Call this before initializing Google APIs
setup_credentials()
```

## Deployment Steps

1. **Prepare your environment variables:**
   ```bash
   # Convert credentials to base64
   echo "GOOGLE_TOKEN_BASE64=$(cat CREDENTIALS/token.json | base64)"
   echo "GOOGLE_CLIENT_SECRET_BASE64=$(cat CREDENTIALS/client_secret.json | base64)"
   ```

2. **Create a new web service on Render:**
   - Connect your GitHub repository
   - Choose "Web Service"
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python mcp_server.py`

3. **Add environment variables:**
   - `GOOGLE_CREDENTIALS_DIR` = `/app/credentials`
   - `GOOGLE_TOKEN_FILE` = `token.json`
   - `GITHUB_TOKEN` = `your_github_token`
   - `GEMINI_API_KEY` = `your_gemini_api_key`
   - `GOOGLE_TOKEN_BASE64` = `<base64_encoded_token_json>`
   - `GOOGLE_CLIENT_SECRET_BASE64` = `<base64_encoded_client_secret_json>`

4. **Deploy your service**

## Security Notes

- Never commit credential files to your repository
- Use environment variables for all sensitive data
- Consider using Render's secret management features
- Regularly rotate your API keys and tokens

## Health Check Endpoints

Your deployed service will have these endpoints available:
- `https://your-service.onrender.com/` - Root endpoint with service info
- `https://your-service.onrender.com/health` - Health check endpoint

## Troubleshooting

### "No ports are free" Error
This has been fixed by configuring the server to bind to Render's PORT environment variable using uvicorn.

### Common Issues:
- **Port binding errors**: Make sure your service type is "Web Service" in Render
- **Authentication errors**: Check Render logs and verify environment variables are set correctly
- **Credential issues**: Ensure your base64 encoded credentials are properly formatted
- **API timeouts**: Verify your Google API tokens haven't expired
- **Service not responding**: Check the `/health` endpoint to verify the service is running

### Debug Steps:
1. Check Render deployment logs for startup errors
2. Verify all environment variables are set in Render dashboard
3. Test the health endpoint: `curl https://your-service.onrender.com/health`
4. Ensure credentials are valid and not expired
5. Test Google API scopes are sufficient for your use case 