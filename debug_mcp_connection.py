#!/usr/bin/env python3
"""
Debug script to test MCP server connection and tool availability
"""

import asyncio
import json
import subprocess
import sys
import os
from pathlib import Path

def check_python_environment():
    """Check if Python and required packages are available"""
    print("🔍 Checking Python Environment")
    print("=" * 50)
    
    # Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in the right directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Check if mcp_server.py exists
    mcp_server_path = current_dir / "mcp_server.py"
    print(f"MCP server exists: {mcp_server_path.exists()}")
    
    # Check required packages
    required_packages = [
        "mcp", "google-auth", "google-auth-oauthlib", 
        "google-auth-httplib2", "google-api-python-client",
        "google-generativeai", "PyGithub", "python-dotenv"
    ]
    
    print("\n📦 Checking Required Packages:")
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    return True

def test_mcp_server_directly():
    """Test if MCP server starts correctly"""
    print("\n🚀 Testing MCP Server Startup")
    print("=" * 50)
    
    try:
        # Try to start the server and see if it responds
        result = subprocess.run(
            [sys.executable, "mcp_server.py"],
            cwd=Path.cwd(),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        print("Server startup test:")
        if result.returncode == 0:
            print("✅ Server started successfully")
        else:
            print("❌ Server failed to start")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️  Server started but didn't exit (this is expected)")
        return True
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def check_credentials():
    """Check if API credentials are set up"""
    print("\n🔐 Checking API Credentials")
    print("=" * 50)
    
    # Check .env file
    env_file = Path.cwd() / ".env"
    if env_file.exists():
        print("✅ .env file exists")
        with open(env_file, 'r') as f:
            content = f.read()
            if "GITHUB_TOKEN" in content:
                print("✅ GITHUB_TOKEN found in .env")
            else:
                print("❌ GITHUB_TOKEN not found in .env")
            
            if "GEMINI_API_KEY" in content:
                print("✅ GEMINI_API_KEY found in .env")
            else:
                print("⚠️  GEMINI_API_KEY not found in .env (optional)")
    else:
        print("⚠️  .env file not found")
    
    # Check Google credentials
    creds_dir = Path.cwd() / "CREDENTIALS"
    if creds_dir.exists():
        print("✅ CREDENTIALS directory exists")
        
        token_file = creds_dir / "token.json"
        client_secret = creds_dir / "client_secret.json"
        
        if token_file.exists():
            print("✅ token.json exists")
        else:
            print("❌ token.json not found - run: python reauthorize_google_apis.py")
            
        if client_secret.exists():
            print("✅ client_secret.json exists")
        else:
            print("❌ client_secret.json not found")
    else:
        print("❌ CREDENTIALS directory not found")

def generate_cursor_config():
    """Generate the exact configuration for Cursor"""
    print("\n📝 Generating Cursor Configuration")
    print("=" * 50)
    
    current_dir = Path.cwd().resolve()
    python_executable = sys.executable
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        print(f"Python executable: {python_executable}")
    else:
        print("⚠️  No virtual environment detected")
        print("Consider using a virtual environment for better isolation")
    
    config = {
        "mcpServers": {
            "my-first-mcp-server": {
                "command": python_executable,
                "args": ["mcp_server.py"],
                "cwd": str(current_dir),
                "env": {
                    "GOOGLE_CREDENTIALS_DIR": "./CREDENTIALS",
                    "GOOGLE_TOKEN_FILE": "token.json",
                    "GITHUB_TOKEN": "your_github_token_here",
                    "GEMINI_API_KEY": "your_gemini_api_key_here"
                }
            }
        }
    }
    
    print("\n📋 Your Cursor Configuration:")
    print(json.dumps(config, indent=2))
    
    # Save to file
    config_file = current_dir / "cursor_mcp_config_generated.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {config_file}")
    
    # Show where to place it
    print("\n📍 Place this configuration at:")
    if sys.platform == "darwin":  # macOS
        print("~/Library/Application Support/Claude/claude_desktop_config.json")
    elif sys.platform == "win32":  # Windows
        print("%APPDATA%\\Claude\\claude_desktop_config.json")
    else:  # Linux
        print("~/.config/Claude/claude_desktop_config.json")

async def test_mcp_client():
    """Test MCP client connection"""
    print("\n🔄 Testing MCP Client Connection")
    print("=" * 50)
    
    try:
        from mcp.client.stdio import stdio_client
        from mcp import StdioServerParameters
        from mcp.client.session import ClientSession
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["mcp_server.py"],
            cwd=str(Path.cwd())
        )
        
        print("Attempting to connect to MCP server...")
        
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                await session.initialize()
                print("✅ MCP session initialized successfully")
                
                # List available tools
                tools_result = await session.list_tools()
                print(f"✅ Found {len(tools_result.tools)} tools:")
                
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")
                
                # Test ping tool
                try:
                    ping_result = await session.call_tool("ping", {})
                    print("✅ Ping tool works:", ping_result.content[0].text)
                except Exception as e:
                    print(f"❌ Ping tool failed: {e}")
                
                return True
                
    except Exception as e:
        print(f"❌ MCP client test failed: {e}")
        return False

def main():
    """Main debugging function"""
    print("🐛 MCP Server Debug Tool")
    print("=" * 50)
    
    # Step 1: Check Python environment
    if not check_python_environment():
        print("\n❌ Python environment check failed!")
        return
    
    # Step 2: Check credentials
    check_credentials()
    
    # Step 3: Test server startup
    if not test_mcp_server_directly():
        print("\n❌ MCP server startup failed!")
        return
    
    # Step 4: Generate configuration
    generate_cursor_config()
    
    # Step 5: Test MCP client connection
    print("\n🔄 Testing MCP client connection...")
    try:
        asyncio.run(test_mcp_client())
        print("\n✅ All tests passed! Your MCP server should work with Cursor.")
    except Exception as e:
        print(f"\n❌ MCP client test failed: {e}")
        print("This might be a configuration issue.")
    
    print("\n🎯 Next Steps:")
    print("1. Copy the generated configuration to Claude Desktop config")
    print("2. Replace 'your_github_token_here' with your actual GitHub token")
    print("3. Replace 'your_gemini_api_key_here' with your actual Gemini API key")
    print("4. Restart Cursor and Claude Desktop")
    print("5. Test by asking Claude: 'List my GitHub repositories'")

if __name__ == "__main__":
    main() 