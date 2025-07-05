#!/usr/bin/env python3
"""
Validation script to check if all dependencies are correctly installed
"""

import sys
import importlib
from typing import List, Tuple

def check_import(module_name: str, package_name: str = None) -> Tuple[bool, str]:
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        return True, f"✅ {package_name or module_name}"
    except ImportError as e:
        return False, f"❌ {package_name or module_name}: {str(e)}"

def validate_dependencies() -> None:
    """Validate all required dependencies"""
    
    print("🔍 Validating MCP Google Colab Server Dependencies")
    print("=" * 60)
    
    # Core dependencies
    dependencies = [
        ("mcp", "MCP (Model Context Protocol)"),
        ("mcp.server", "MCP Server"),
        ("mcp.client.stdio", "MCP Client"),
        
        # Google APIs
        ("google.auth", "Google Auth"),
        ("google_auth_oauthlib", "Google OAuth"),
        ("googleapiclient", "Google API Client"),
        ("google.generativeai", "Google Generative AI (Gemini)"),
        
        # GitHub API
        ("github", "PyGithub (GitHub API)"),
        
        # Environment and utilities
        ("dotenv", "Python Dotenv"),
        ("pydantic", "Pydantic"),
        ("anyio", "AnyIO"),
        
        # Standard library (should always work)
        ("json", "JSON"),
        ("asyncio", "AsyncIO"),
        ("logging", "Logging"),
        ("os", "OS"),
        ("io", "IO"),
    ]
    
    success_count = 0
    total_count = len(dependencies)
    
    for module_name, display_name in dependencies:
        success, message = check_import(module_name, display_name)
        print(message)
        if success:
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Results: {success_count}/{total_count} dependencies available")
    
    if success_count == total_count:
        print("🎉 All dependencies are correctly installed!")
        print("\n🚀 You can now run:")
        print("   python mcp_server.py     # Start the MCP server")
        print("   python test_client.py    # Test the server")
        print("   python demo_readme.py    # Demo README generation")
    else:
        print("⚠️  Some dependencies are missing.")
        print("\n🔧 To fix this, run:")
        print("   pip install -r requirements.txt")
        print("   # or")
        print("   pip install -r requirements-lock.txt")
        
        # Check for specific issues
        missing_core = not check_import("mcp")[0]
        missing_google = not check_import("googleapiclient")[0]
        missing_gemini = not check_import("google.generativeai")[0]
        missing_github = not check_import("github")[0]
        
        if missing_core:
            print("\n❗ MCP is missing - this is required for the server to work")
        if missing_google:
            print("❗ Google API client is missing - required for Drive access")
        if missing_gemini:
            print("ℹ️  Gemini API is missing - README generation will use fallback mode")
        if missing_github:
            print("ℹ️  PyGithub is missing - GitHub repository creation unavailable")

def check_environment() -> None:
    """Check environment setup"""
    
    print("\n🔧 Environment Configuration Check")
    print("-" * 40)
    
    import os
    from pathlib import Path
    
    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        
        # Load and check environment variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            credentials_dir = os.getenv("GOOGLE_CREDENTIALS_DIR")
            token_file = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
            gemini_key = os.getenv("GEMINI_API_KEY")
            github_token = os.getenv("GITHUB_TOKEN")
            
            if credentials_dir:
                cred_path = Path(credentials_dir)
                if cred_path.exists():
                    print(f"✅ Credentials directory: {cred_path}")
                    
                    # Check for token file
                    token_path = cred_path / token_file
                    if token_path.exists():
                        print(f"✅ Token file found: {token_path}")
                    else:
                        print(f"⚠️  Token file missing: {token_path}")
                        print("   Run: python generate_token.py")
                        
                    # Check for client secret
                    client_secret = cred_path / "client_secret.json"
                    if client_secret.exists():
                        print(f"✅ Client secret found: {client_secret}")
                    else:
                        print(f"❌ Client secret missing: {client_secret}")
                        print("   Download from Google Cloud Console")
                else:
                    print(f"❌ Credentials directory not found: {cred_path}")
            else:
                print("⚠️  GOOGLE_CREDENTIALS_DIR not set in .env")
                
            if gemini_key and gemini_key != "your_gemini_api_key_here":
                print("✅ Gemini API key configured")
            else:
                print("ℹ️  Gemini API key not configured (optional)")
                
            if github_token:
                print("✅ GitHub token configured")
            else:
                print("ℹ️  GitHub token not configured (GitHub operations unavailable)")
                
        except Exception as e:
            print(f"❌ Error loading .env: {e}")
    else:
        print("⚠️  .env file not found")
        print("   Create .env file with configuration (see SETUP.md)")

if __name__ == "__main__":
    print(f"🐍 Python version: {sys.version}")
    print()
    
    validate_dependencies()
    check_environment()
    
    print("\n📚 For detailed setup instructions, see SETUP.md") 