# 🚀 MCP Multi-Service Server

A comprehensive **Model Context Protocol (MCP)** server that integrates **Google Colab**, **GitHub**, and **Google Docs** with **AI-powered analysis** for seamless development workflow automation.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-1.10.0%2B-green.svg)](https://github.com/modelcontextprotocol/python-sdk)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🌟 Features

### 🔗 **Multi-Platform Integration**
- **Google Colab** - Notebook management and analysis
- **GitHub** - Repository operations and code insights  
- **Google Docs** - Document management and resume building
- **AI Analysis** - Powered by Google Gemini API

### 🤖 **AI-Powered Capabilities**
- **Smart README Generation** - Create professional documentation from notebooks
- **Code Analysis** - Comprehensive repository insights and summaries
- **Resume Building** - Auto-generate project summaries for professional profiles
- **Intelligent Parsing** - Extract libraries, dependencies, and project structure

### ⚡ **Automation Features**
- **One-Click Repository Creation** - Convert Colab notebooks to GitHub repos
- **Interactive Testing** - Comprehensive test suite with user-friendly interface
- **Batch Processing** - Handle multiple files and repositories efficiently
- **Fallback Modes** - Graceful degradation when APIs are unavailable

## 🚀 Quick Start

### 1. **Clone and Install**
```bash
git clone <https://github.com/sreerajchintham/my-first-mcp-server>
cd my-first-mcp-server
pip install -r requirements.txt
```

### 2. **Configure APIs**
```bash
# Set up Google APIs
python reauthorize_google_apis.py

# Create .env file
cp .env.example .env
# Edit .env with your API keys
```

### 3. **Run the Server**
```bash
python mcp_server.py
```

### 4. **Test Everything**
```bash
python test_client.py
```

## 📋 Prerequisites

- **Python 3.8+**
- **Google Account** with Drive access
- **GitHub Account** with personal access token
- **Gemini API Key** (optional, for AI features)

## 🛠️ Installation

### **Option 1: Development Setup**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### **Option 2: Production Setup**
```bash
# Use locked versions for reproducibility
pip install -r requirements-lock.txt
```

## ⚙️ Configuration

### **1. Google APIs Setup**
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable **Drive API** and **Docs API**
3. Create **OAuth 2.0 credentials** (Desktop app)
4. Download `client_secret.json` → `CREDENTIALS/client_secret.json`
5. Run authorization: `python reauthorize_google_apis.py`

### **2. GitHub API Setup**
1. Go to [GitHub Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Create token with `repo` and `user` scopes
3. Add to `.env` file

### **3. Environment Variables**
```bash
# .env file
GOOGLE_CREDENTIALS_DIR=./CREDENTIALS
GOOGLE_TOKEN_FILE=token.json
GITHUB_TOKEN=your_github_token_here
GEMINI_API_KEY=your_gemini_api_key_here  # Optional
```

## 📚 Usage

### **Interactive Mode**
```bash
python test_client.py
```
- Browse and analyze GitHub repositories
- Generate AI-powered project summaries
- Create professional documentation
- Manage Google Docs integration

### **Programmatic Usage**
```python
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters

# Connect to MCP server
server_params = StdioServerParameters(
    command="python", 
    args=["mcp_server.py"]
)

# Use MCP tools
async with stdio_client(server_params) as (read, write):
    # ... MCP operations
```

## 🔧 Available Tools

### **Google Colab Tools**
- `list_colab_files()` - List notebooks in Google Drive
- `read_colab_notebook(file_id)` - Read notebook content
- `generate_readme(file_id, file_name)` - AI-powered README generation

### **GitHub Tools**
- `list_github_repos()` - List repositories with filters
- `read_github_repo_files(repo_name)` - Analyze repository files
- `analyze_github_repo_with_ai(repo_name)` - AI-powered analysis
- `create_github_repo()` - Create repo from Colab notebook

### **Google Docs Tools**
- `list_google_docs(search_term)` - Find Google Docs
- `add_to_google_doc(doc_id, content)` - Add content to documents

### **Utility Tools**
- `ping()` - Test server connectivity
- `summarize_repo_analysis_for_resume()` - Generate resume summaries

## 🤖 AI Analysis Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Comprehensive** | Full analysis of code, docs, and structure | Complete project overview |
| **README Only** | Focus on documentation and descriptions | Documentation review |
| **Code Only** | Deep dive into code structure and logic | Technical assessment |
| **Structure** | Project organization and architecture | Architecture review |

## 📊 Integration Examples

### **Claude Desktop Integration**
```json
{
  "mcpServers": {
    "multi-service-server": {
      "command": "python",
      "args": ["/path/to/mcp_server.py"],
      "cwd": "/path/to/project",
      "env": {
        "GOOGLE_CREDENTIALS_DIR": "/path/to/CREDENTIALS",
        "GITHUB_TOKEN": "your_token_here"
      }
    }
  }
}
```

### **Resume Building Workflow**
```python
# 1. Analyze repository
analysis = await analyze_github_repo_with_ai("user/repo", "comprehensive")

# 2. Generate resume summary
summary = await summarize_repo_analysis_for_resume(
    "user/repo", 
    analysis, 
    "technical"
)

# 3. Add to Google Doc
await add_to_google_doc("doc_id", summary, "Projects")
```

## 🏗️ Project Structure

```
my-first-mcp-server/
├── 📄 mcp_server.py              # Main MCP server
├── 🧪 test_client.py             # Interactive test suite
├── 🧪 test_github_tool.py        # GitHub tool testing
├── 🔧 debug_mcp_connection.py    # MCP connection debugging
├── 🔑 reauthorize_google_apis.py # Google OAuth setup
├── ✅ validate_setup.py          # Dependency validation
├── 📋 requirements.txt           # Python dependencies
├── 🔒 requirements-lock.txt      # Locked versions
├── 📖 README.md                  # Project documentation
├── 📖 SETUP.md                   # Detailed setup guide
├── 🌍 .env                       # Environment variables
├── 📁 CREDENTIALS/               # OAuth credentials
│   ├── client_secret.json
│   └── token.json
└── 📁 support files/             # Configuration and support files
    ├── claude_desktop_config.json
    ├── cursor_mcp_config.json
    ├── cursor_mcp_config_final.json
    ├── CURSOR_FIX_GUIDE.md
    ├── CURSOR_SETUP_GUIDE.md
    ├── demo_readme.py
    ├── presentation_outline.md
    ├── render_deployment_guide.md
    └── run_env.py
```

## 🔍 Troubleshooting

### **Common Issues**

| Issue | Solution |
|-------|----------|
| **Google Auth Error** | Run `python reauthorize_google_apis.py` |
| **GitHub API Error** | Check token permissions and expiration |
| **Gemini API Error** | Verify API key and quota limits |
| **Import Error** | Run `pip install -r requirements.txt` |

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### **Validation Check**
```bash
python validate_setup.py
```

## 🧪 Testing

### **Interactive Testing**
```bash
python test_client.py
```

### **README Generation Demo**
```bash
python demo_readme.py
```

### **Environment Verification**
```bash
python run_env.py
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Model Context Protocol** - For the excellent MCP framework
- **Google APIs** - For comprehensive service integration
- **GitHub API** - For repository management capabilities
- **Google Gemini** - For AI-powered analysis features

## 📞 Support

- 📖 **Documentation**: Check [SETUP.md](SETUP.md) for detailed setup
- 🐛 **Issues**: Report bugs via GitHub Issues
- 💬 **Discussions**: Use GitHub Discussions for questions
- 🧪 **Testing**: Run `python test_client.py` for interactive debugging

---

<div align="center">

**⭐ Star this repo if you find it helpful!**

Made with ❤️ by the MCP community

</div> 
