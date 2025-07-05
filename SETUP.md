# MCP Multi-Service Server Setup Guide

This guide will help you set up and run the MCP (Model Context Protocol) server for comprehensive Google Colab, GitHub, and Google Docs management with AI-powered analysis.

## Overview

This MCP server provides integrated access to:
- **Google Colab** - Notebook management and README generation
- **GitHub** - Repository management, file analysis, and AI-powered insights
- **Google Docs** - Document management and resume building
- **AI Analysis** - Powered by Google Gemini API for comprehensive code analysis

## Prerequisites

- Python 3.8 or higher
- Google account with Google Drive access
- GitHub account with personal access token
- (Optional) Gemini API key for enhanced AI analysis

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

### 4. Set Up Google APIs

#### 4.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Docs API

#### 4.2 Create OAuth 2.0 Credentials
1. Go to "Credentials" in the Google Cloud Console
2. Click "Create Credentials" → "OAuth 2.0 Client IDs"
3. Choose "Desktop application"
4. Download the JSON file and save it as `CREDENTIALS/client_secret.json`

#### 4.3 Generate Authentication Token
```bash
python reauthorize_google_apis.py
```
Follow the browser prompts to authenticate and grant permissions for Drive and Docs access.

### 5. Set Up GitHub API

#### 5.1 Create GitHub Personal Access Token
1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" → "Generate new token (classic)"
3. Select the following scopes:
   - `repo` (Full control of private repositories)
   - `user:email` (Access user email addresses)
   - `read:user` (Read access to user profile)
4. Generate and copy the token

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
GOOGLE_CREDENTIALS_DIR=./CREDENTIALS
GOOGLE_TOKEN_FILE=token.json

# GitHub API configuration
GITHUB_TOKEN=your_github_token_here

# Optional: For enhanced AI analysis
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 6.1 Get Gemini API Key (Optional)
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
# Run comprehensive interactive test
python test_client.py

# Run README generation demo
python demo_readme.py
```

### 3. Available Tools

The MCP server provides the following tools:

#### Core Tools
- **`ping`**: Test server connectivity

#### Google Colab Tools
- **`list_colab_files`**: List Google Colab notebooks in Drive
- **`read_colab_notebook`**: Read notebook content and metadata
- **`generate_readme`**: Generate comprehensive README files using AI

#### GitHub Tools
- **`list_github_repos`**: List GitHub repositories with filtering options
- **`read_github_repo_files`**: Read and analyze repository files
- **`analyze_github_repo_with_ai`**: AI-powered repository analysis
- **`create_github_repo`**: Create new GitHub repository from Colab notebook
- **`summarize_repo_analysis_for_resume`**: Generate resume-ready project summaries

#### Google Docs Tools
- **`list_google_docs`**: Find Google Docs (e.g., resumes)
- **`add_to_google_doc`**: Add content to existing Google Docs

## Features

### Enhanced README Generation

The server generates comprehensive README files with:
- **AI-Powered Analysis** (with Gemini API): Intelligent code understanding and documentation
- **Automatic Library Detection**: Identifies and documents dependencies
- **Professional Formatting**: Clean, structured markdown output
- **Usage Instructions**: Generated based on code analysis
- **Fallback Mode**: Smart parsing when AI is unavailable

### GitHub Integration

- **Repository Management**: List, analyze, and create repositories
- **File Analysis**: Read and understand repository structure
- **AI-Powered Insights**: Comprehensive code analysis and documentation
- **Resume Integration**: Generate professional project summaries

### Google Docs Integration

- **Document Management**: List and update Google Docs
- **Resume Building**: Automatically add project analyses to resume documents
- **Professional Formatting**: Clean, structured content addition

## Interactive Testing

The `test_client.py` provides a comprehensive interactive interface:

```bash
python test_client.py
```

Features include:
- **Repository Explorer**: Browse and analyze GitHub repositories
- **AI Analysis Options**: Multiple analysis types (comprehensive, code-only, structure, etc.)
- **Google Docs Integration**: Add analyses directly to resume documents
- **Colab Integration**: Generate and manage notebook documentation

## Troubleshooting

### Common Issues

1. **Google API Authentication Errors**
   ```bash
   # Re-authorize with expanded scopes
   python reauthorize_google_apis.py
   ```

2. **GitHub API Errors**
   - Verify your personal access token has correct permissions
   - Check token expiration date
   - Ensure token includes `repo` and `user` scopes

3. **Permission Issues**
   - Ensure Google account has access to target files
   - Check OAuth scope includes `drive` and `documents`
   - Verify GitHub token has repository access

4. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install --upgrade -r requirements.txt
   ```

5. **Gemini API Errors**
   - Verify API key is correct and has quota
   - Server automatically falls back to basic mode if Gemini fails

### Logs and Debugging

The server uses comprehensive logging. To see detailed logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration with MCP Clients

### Claude Desktop

Add this configuration to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "multi-service-server": {
      "command": "python",
      "args": ["/path/to/your/mcp_server.py"],
      "cwd": "/path/to/your/project",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "/path/to/your/project/CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "your_github_token_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

### Other MCP Clients

The server follows the standard MCP protocol and works with any compatible client.

## Development

### Project Structure

```
my-first-mcp-server/
├── mcp_server.py              # Main MCP server
├── test_client.py             # Comprehensive interactive test client
├── demo_readme.py             # README generation demo
├── reauthorize_google_apis.py # Google OAuth token generator
├── validate_setup.py          # Setup validation
├── run_env.py                 # Environment runner
├── requirements.txt           # Flexible dependencies
├── requirements-lock.txt      # Locked dependencies
├── SETUP.md                   # This file
├── .env                       # Environment variables
└── CREDENTIALS/               # Google OAuth credentials
    ├── client_secret.json     # OAuth client secrets
    └── token.json             # Generated access token
```

### Adding New Tools

To add new MCP tools, use the FastMCP decorator pattern:

```python
@mcp.tool()
def my_new_tool(param: str):
    """Tool description"""
    return {"result": "success"}
```

### API Integrations

The server integrates with:
- **Google Drive API v3** - File management
- **Google Docs API v1** - Document management
- **GitHub API v3** - Repository management
- **Google Gemini API** - AI analysis

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs for error details
3. Ensure all dependencies are correctly installed
4. Verify API credentials and permissions
5. Test with `python test_client.py` for interactive debugging 