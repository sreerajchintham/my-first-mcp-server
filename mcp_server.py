from mcp.server import FastMCP
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import google.generativeai as genai
from github import Github
import io
import json
from dotenv import load_dotenv
import os
import logging
from typing import Optional
import base64
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_CREDENTIALS_DIR = os.getenv("GOOGLE_CREDENTIALS_DIR")
GOOGLE_TOKEN_FILE = os.path.join(GOOGLE_CREDENTIALS_DIR, os.getenv("GOOGLE_TOKEN_FILE"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Initialize Google Drive API
try:
    logger.debug("Initializing Google Drive API")
    creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, ["https://www.googleapis.com/auth/drive.readonly"])
    drive_service = build("drive", "v3", credentials=creds)
    logger.debug("Google Drive API initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Google Drive API: {e}")
    raise

# Initialize Gemini API
try:
    if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
        logger.debug("Initializing Gemini API")
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        logger.debug("Gemini API initialized successfully")
    else:
        logger.warning("Gemini API key not configured. README generation will use basic mode.")
        gemini_model = None
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {e}")
    gemini_model = None

# Initialize GitHub API
try:
    if GITHUB_TOKEN:
        logger.debug("Initializing GitHub API")
        github_client = Github(GITHUB_TOKEN)
        # Test the connection
        user = github_client.get_user()
        logger.debug(f"GitHub API initialized successfully for user: {user.login}")
    else:
        logger.warning("GitHub token not configured. GitHub operations will not be available.")
        github_client = None
except Exception as e:
    logger.error(f"Failed to initialize GitHub API: {e}")
    github_client = None

# Create the FastMCP server
mcp = FastMCP(name="my-first-mcp-server")

@mcp.tool()
def ping():
    """Test server connectivity"""
    logger.debug("Ping tool called")
    return {"status": "pong"}

@mcp.tool()
def list_colab_files(folder_id: Optional[str] = None):
    """List Google Colab notebook files (.ipynb) in a Google Drive folder. If folder_id is None, search entire Drive."""
    logger.debug(f"Listing Colab files, folder_id: {folder_id}")
    try:
        query = "mimeType='application/vnd.google.colaboratory' and trashed=false"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        results = drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType, webViewLink)",
            pageSize=30
        ).execute()
        
        files = results.get("files", [])
        logger.debug(f"Found {len(files)} Colab files")
        return [{"id": f["id"]+"\n", "name": f["name"]+"\n", "link": f["webViewLink"]+"\n"} for f in files]
    except Exception as e:
        logger.error(f"Error in list_colab_files: {e}")
        return {"error": str(e)}

@mcp.tool()
def read_colab_notebook(file_id: str):
    """Read the content of a Google Colab notebook by file ID and return its metadata and cells."""
    logger.debug(f"Reading Colab notebook, file_id: {file_id}")
    try:
        # Download the .ipynb file
        request = drive_service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        # Parse the .ipynb content
        file_stream.seek(0)
        notebook_content = json.load(file_stream)
        
        # Extract basic metadata and cells
        metadata = {
            "name": notebook_content.get("metadata", {}).get("colab", {}).get("name", "Unknown"),
            "cell_count": len(notebook_content.get("cells", []))
        }
        cells = [
            {
                "cell_type": cell.get("cell_type"),
                "source": "".join(cell.get("source", [])) if cell.get("source") else ""
            }
            for cell in notebook_content.get("cells", [])
        ]
        
        logger.debug(f"Read notebook: {metadata['name']} with {metadata['cell_count']} cells")
        return {"metadata": metadata, "cells": cells}
    except Exception as e:
        logger.error(f"Error in read_colab_notebook: {e}")
        return {"error": str(e)}

@mcp.tool()
def generate_readme(file_id: str, file_name: str):
    """Generate a comprehensive README.md string for a Colab notebook using AI analysis of its content."""
    logger.debug(f"Generating README for file_id: {file_id}, file_name: {file_name}")
    try:
        # Read notebook content
        notebook_data = read_colab_notebook(file_id)
        if "error" in notebook_data:
            return {"error": notebook_data["error"]}
        
        metadata = notebook_data.get("metadata", {})
        cells = notebook_data.get("cells", [])
        
        # Use file_name as fallback if metadata name is "Unknown"
        title = metadata.get("name", file_name) if metadata.get("name") != "Unknown" else file_name
        
        # If Gemini API is available, use it for intelligent README generation
        if gemini_model:
            try:
                # Prepare notebook content for analysis
                notebook_content = ""
                for i, cell in enumerate(cells):
                    cell_type = cell.get("cell_type", "unknown")
                    source = cell.get("source", "")
                    if source:
                        notebook_content += f"=== Cell {i+1} ({cell_type}) ===\n{source}\n\n"
                
                # Limit content length for API call
                if len(notebook_content) > 15000:  # Reasonable limit for API
                    notebook_content = notebook_content[:15000] + "\n\n... (content truncated)"
                
                # Create a comprehensive prompt
                prompt = f"""
Analyze this Google Colab notebook and generate a comprehensive README.md file.

Notebook Title: {title}
Number of Cells: {len(cells)}

Notebook Content:
{notebook_content}

Please generate a professional README.md that includes:
1. A clear title and brief description
2. Overview of what the notebook does
3. Key features and functionality
4. Technologies/libraries used
5. Main sections or steps in the analysis
6. Key insights or results (if apparent)
7. How to use/run the notebook

Format the response as proper markdown with appropriate headers, bullet points, and code blocks where relevant.
Make it informative but concise, suitable for a GitHub repository.
"""
                
                # Generate README using Gemini
                logger.debug("Using Gemini API to generate README")
                response = gemini_model.generate_content(prompt)
                
                if response.text:
                    logger.debug(f"Generated AI-powered README for {title}")
                    return {"readme": response.text}
                else:
                    logger.warning("Gemini API returned empty response, falling back to basic mode")
                    
            except Exception as e:
                logger.error(f"Error using Gemini API: {e}, falling back to basic mode")
        
        # Fallback to basic README generation
        logger.debug("Using basic README generation")
        
        # Extract markdown cells for description
        description = ""
        code_summary = ""
        libraries_used = set()
        
        for cell in cells:
            if cell.get("cell_type") == "markdown" and cell.get("source"):
                description += cell["source"] + "\n\n"
            elif cell.get("cell_type") == "code" and cell.get("source"):
                code = cell["source"]
                # Extract import statements
                for line in code.split('\n'):
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        if 'import' in line:
                            parts = line.split()
                            if len(parts) >= 2:
                                lib = parts[1].split('.')[0]
                                libraries_used.add(lib)
        
        # Generate README content
        readme_content = f"# {title}\n\n"
        readme_content += f"## Overview\n"
        readme_content += f"This is a Google Colab notebook with {len(cells)} cells containing data analysis and machine learning code.\n\n"
        
        if description:
            readme_content += "## Description\n" + description[:1000] + ("..." if len(description) > 1000 else "") + "\n\n"
        
        if libraries_used:
            readme_content += "## Libraries Used\n"
            for lib in sorted(libraries_used):
                readme_content += f"- {lib}\n"
            readme_content += "\n"
        
        readme_content += "## How to Use\n"
        readme_content += "1. Open the notebook in Google Colab\n"
        readme_content += "2. Run the cells sequentially\n"
        readme_content += "3. Make sure to install any required dependencies\n\n"
        
        readme_content += "## Structure\n"
        readme_content += f"The notebook contains {len([c for c in cells if c.get('cell_type') == 'code'])} code cells and {len([c for c in cells if c.get('cell_type') == 'markdown'])} markdown cells.\n"
        
        logger.debug(f"Generated basic README for {title}")
        return {"readme": readme_content}
        
    except Exception as e:
        logger.error(f"Error in generate_readme: {e}")
        return {"error": str(e)}

@mcp.tool()
def create_github_repo(file_id: str, file_name: str, repo_name: str, repo_description: str = "", is_private: bool = False):
    """Create a GitHub repository and upload a Colab notebook with generated README."""
    logger.debug(f"Creating GitHub repo: {repo_name} for file: {file_name}")
    
    if not github_client:
        return {"error": "GitHub API not configured. Please set GITHUB_TOKEN in .env file."}
    
    try:
        # Get the authenticated user
        user = github_client.get_user()
        
        # Check if repo already exists
        try:
            existing_repo = user.get_repo(repo_name)
            return {"error": f"Repository '{repo_name}' already exists at {existing_repo.html_url}"}
        except:
            # Repo doesn't exist, we can create it
            pass
        
        # Create the repository
        logger.debug(f"Creating repository: {repo_name}")
        
        # Sanitize description to remove control characters
        clean_description = repo_description or f"Google Colab notebook: {file_name}"
        # Remove control characters except space and basic punctuation
        clean_description = ''.join(char for char in clean_description if ord(char) >= 32 or char in '\t\n\r')
        # Remove any remaining problematic characters and limit length
        clean_description = clean_description.strip().replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        # Collapse multiple spaces into single space
        clean_description = re.sub(r'\s+', ' ', clean_description)
        # Limit to GitHub's description length limit (100 characters)
        clean_description = clean_description[:100]
        
        repo = user.create_repo(
            name=repo_name,
            description=clean_description,
            private=is_private,
            auto_init=False,  # We'll add our own files
            has_issues=True,
            has_wiki=True,
            has_downloads=True
        )
        
        # Generate README content
        logger.debug("Generating README content")
        readme_result = generate_readme(file_id, file_name)
        if "error" in readme_result:
            # Clean up the created repo if README generation fails
            repo.delete()
            return {"error": f"Failed to generate README: {readme_result['error']}"}
        
        readme_content = readme_result["readme"]
        
        # Download the Colab notebook content
        logger.debug("Downloading Colab notebook content")
        notebook_result = read_colab_notebook(file_id)
        if "error" in notebook_result:
            # Clean up the created repo if notebook download fails
            repo.delete()
            return {"error": f"Failed to read notebook: {notebook_result['error']}"}
        
        # Get the original notebook file content as JSON
        request = drive_service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_stream.seek(0)
        notebook_json = file_stream.read().decode('utf-8')
        
        # Create and upload README.md
        logger.debug("Uploading README.md")
        repo.create_file(
            path="README.md",
            message="Add README with notebook description",
            content=readme_content
        )
        
        # Create and upload the notebook file
        logger.debug(f"Uploading {file_name}")
        # Ensure file_name has .ipynb extension
        if not file_name.endswith('.ipynb'):
            file_name += '.ipynb'
            
        repo.create_file(
            path=file_name,
            message=f"Add {file_name} notebook",
            content=notebook_json
        )
        
        # Create a simple .gitignore for Python projects
        gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Jupyter Notebook checkpoints
.ipynb_checkpoints

# Google Colab
.colab/
"""
        
        repo.create_file(
            path=".gitignore",
            message="Add .gitignore for Python projects",
            content=gitignore_content
        )
        
        # Get repository stats
        repo_info = {
            "repo_name": repo.name,
            "repo_url": repo.html_url,
            "clone_url": repo.clone_url,
            "ssh_url": repo.ssh_url,
            "description": repo.description,
            "is_private": repo.private,
            "files_uploaded": [
                "README.md",
                file_name,
                ".gitignore"
            ],
            "created_at": repo.created_at.isoformat(),
            "owner": user.login
        }
        
        logger.debug(f"Successfully created repository: {repo.html_url}")
        return {
            "success": True,
            "message": f"Repository '{repo_name}' created successfully!",
            "repository": repo_info
        }
        
    except Exception as e:
        logger.error(f"Error creating GitHub repository: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.debug("Starting MCP server")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise