# 🚀 Cursor MCP Server Setup Guide

## Overview
This guide will help you integrate your MCP Multi-Service Server with Cursor IDE to access Google Colab, GitHub, and Google Docs functionality directly from your editor.

## 📋 Prerequisites

Before setting up the MCP server with Cursor, ensure you have:

1. **Python 3.8+** installed
2. **Cursor IDE** installed
3. **MCP server dependencies** installed (`pip install -r requirements.txt`)
4. **API credentials** configured (Google, GitHub, Gemini)

## 🛠️ Setup Steps

### Step 1: Locate Claude Desktop Configuration

The configuration file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```bash
~/.config/Claude/claude_desktop_config.json
```

### Step 2: Create or Update Configuration File

Create the configuration file if it doesn't exist, or merge with existing configuration:

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "your_github_token_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here"
      }
    }
  }
}
```

### Step 3: Customize the Configuration

**Update the following values:**

1. **`cwd`**: Change to your actual project path
   ```json
   "cwd": "/path/to/your/my-first-mcp-server"
   ```

2. **`GITHUB_TOKEN`**: Replace with your actual GitHub token
   ```json
   "GITHUB_TOKEN": "ghp_your_actual_github_token_here"
   ```

3. **`GEMINI_API_KEY`**: Replace with your actual Gemini API key
   ```json
   "GEMINI_API_KEY": "your_actual_gemini_api_key_here"
   ```

### Step 4: Environment Variables Setup

You can also use a `.env` file in your project directory instead of hardcoding in the JSON:

```bash
# .env file in your project directory
GOOGLE_CREDENTIALS_DIR=./CREDENTIALS
GOOGLE_TOKEN_FILE=token.json
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here
```

If using `.env`, your configuration becomes:

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server"
    }
  }
}
```

### Step 5: Verify Python Environment

Make sure your Python environment has all dependencies:

```bash
cd /path/to/your/my-first-mcp-server
pip install -r requirements.txt
```

### Step 6: Test the Configuration

Test your MCP server before adding to Cursor:

```bash
cd /path/to/your/my-first-mcp-server
python test_client.py
```

## 🔧 Complete Configuration Examples

### Example 1: With Environment Variables in Config

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx",
        "GEMINI_API_KEY": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Example 2: Multiple MCP Servers

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx",
        "GEMINI_API_KEY": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    },
    "other-mcp-server": {
      "command": "python",
      "args": ["other_server.py"],
      "cwd": "/path/to/other/server"
    }
  }
}
```

### Example 3: Using Virtual Environment

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server/.venv/bin/python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxx",
        "GEMINI_API_KEY": "AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

## 🚀 After Configuration

### 1. Restart Cursor/Claude Desktop
After updating the configuration, restart Cursor and Claude Desktop for changes to take effect.

### 2. Available Tools in Cursor
Once configured, you'll have access to these MCP tools:

**Google Colab Tools:**
- `list_colab_files()` - List notebooks in Google Drive
- `read_colab_notebook()` - Read notebook content
- `generate_readme()` - AI-powered README generation

**GitHub Tools:**
- `list_github_repos()` - List repositories
- `read_github_repo_files()` - Analyze repository files
- `analyze_github_repo_with_ai()` - AI-powered analysis
- `create_github_repo()` - Create repo from Colab notebook

**Google Docs Tools:**
- `list_google_docs()` - Find Google Docs
- `add_to_google_doc()` - Add content to documents

### 3. Using the Tools in Cursor
You can now ask Claude in Cursor to:
- "List my Google Colab notebooks"
- "Analyze this GitHub repository: microsoft/vscode"
- "Create a GitHub repo from my Colab notebook"
- "Generate a README for my project"
- "Add this project summary to my resume in Google Docs"

## 🔍 Troubleshooting

### Common Issues:

1. **"Command not found" error**
   - Ensure Python is in your PATH
   - Use absolute path to Python executable
   - Check if virtual environment is activated

2. **"Permission denied" error**
   - Check file permissions on mcp_server.py
   - Ensure Python executable has proper permissions

3. **"Module not found" error**
   - Run `pip install -r requirements.txt`
   - Check if you're using the correct Python environment

4. **API authentication errors**
   - Verify your API keys are correct
   - Check Google OAuth token is valid
   - Ensure GitHub token has proper scopes

### Debug Mode:
To enable debug logging, add to your configuration:

```json
{
  "mcpServers": {
    "my-first-mcp-server": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
        "GOOGLE_TOKEN_FILE": "token.json",
        "GITHUB_TOKEN": "your_github_token_here",
        "GEMINI_API_KEY": "your_gemini_api_key_here",
        "PYTHONPATH": "/Users/raj/Documents/Sreeraj%20-%20guthib/my-first-mcp-server",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## 🎯 Next Steps

1. **Test Integration**: Try asking Claude to list your GitHub repos
2. **Explore Features**: Test the AI analysis capabilities
3. **Automate Workflows**: Set up automated repository creation
4. **Customize**: Modify the server for your specific needs

## 📧 Support

If you encounter issues:
1. Check the logs in your terminal
2. Verify all API credentials are correct
3. Test the server independently with `python test_client.py`
4. Review the SETUP.md for detailed API configuration steps 