# MCP Google Colab Server Setup Guide

This guide will help you set up and run the MCP (Model Context Protocol) server for Google Colab notebook management.

## Prerequisites

- Python 3.8 or higher
- Google account with Google Drive access
- (Optional) Gemini API key for enhanced README generation

## Installation Steps

### 1. Clone/Download the Project

```bash
git clone <repository-url>
cd my-first-mcp-server
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 3. Install Dependencies

Choose one of the following installation methods:

#### Option A: Flexible Installation (Recommended for development)
```bash
pip install -r requirements.txt
```

#### Option B: Exact Version Match (Recommended for production)
```bash
pip install -r requirements-lock.txt
```

### 4. Set Up Google Drive API

#### 4.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Drive API

#### 4.2 Create OAuth 2.0 Credentials
1. Go to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the JSON file and save it as `CREDENTIALS/client_secret.json`

#### 4.3 Generate Authentication Token
```bash
python generate_token.py
```
Follow the browser prompts to authenticate and grant permissions.

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
GOOGLE_CREDENTIALS_DIR=/path/to/your/project/CREDENTIALS
GOOGLE_CLIENT_SECRET_FILE=client_secret.json
GOOGLE_TOKEN_FILE=token.json

# Optional: For enhanced README generation
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 5.1 Get Gemini API Key (Optional)
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API key"
4. Add the key to your `.env` file

## Usage

### 1. Start the MCP Server

```bash
python mcp_server.py
```

### 2. Test the Server

```bash
# Run comprehensive test
python test_client.py

# Run README generation demo
python demo_readme.py
```

### 3. Available Tools

The MCP server provides the following tools:

- **`ping`**: Test server connectivity
- **`list_colab_files`**: List Google Colab notebooks in Drive
- **`read_colab_notebook`**: Read notebook content and metadata
- **`generate_readme`**: Generate comprehensive README files using AI

## Features

### Enhanced README Generation

The server can generate two types of README files:

1. **AI-Powered** (with Gemini API): Comprehensive analysis with intelligent insights
2. **Fallback Mode**: Smart parsing with library detection and structure analysis

### Automatic Features

- ✅ Library detection from import statements
- ✅ Cell type analysis (code vs markdown)
- ✅ Professional markdown formatting
- ✅ Usage instructions generation
- ✅ Error handling and fallback modes

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Regenerate token
   rm CREDENTIALS/token.json
   python generate_token.py
   ```

2. **Permission Issues**
   - Ensure your Google account has access to the Colab files
   - Check that the OAuth scope includes `drive.readonly`

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   ```

4. **Gemini API Errors**
   - Verify your API key is correct
   - Check API quotas and limits
   - Server will fallback to basic mode if Gemini fails

### Logs and Debugging

The server uses Python logging. To see detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with MCP Clients

### Claude Desktop

To use with Claude Desktop, add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "colab-server": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Other MCP Clients

The server follows the standard MCP protocol and should work with any compatible client.

## Development

### Project Structure

```
my-first-mcp-server/
├── mcp_server.py          # Main MCP server
├── test_client.py         # Test client
├── demo_readme.py         # README generation demo
├── generate_token.py      # Google OAuth token generator
├── requirements.txt       # Flexible dependencies
├── requirements-lock.txt  # Locked dependencies
├── SETUP.md              # This file
├── .env                  # Environment variables
└── CREDENTIALS/          # Google OAuth credentials
    ├── client_secret.json
    └── token.json
```

### Adding New Tools

To add new MCP tools, use the FastMCP decorator pattern:

```python
@mcp.tool()
def my_new_tool(param: str):
    """Tool description"""
    return {"result": "success"}
```

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all dependencies are correctly installed
4. Verify Google API credentials and permissions 