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

# Define all required Google API scopes
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/drive",           # Full Drive access
    "https://www.googleapis.com/auth/documents",       # Google Docs access
    "https://www.googleapis.com/auth/drive.file"       # File creation access
]

# Initialize Google APIs with comprehensive scopes
try:
    logger.debug("Initializing Google APIs")
    creds = Credentials.from_authorized_user_file(GOOGLE_TOKEN_FILE, GOOGLE_SCOPES)
    
    # Initialize Drive API
    drive_service = build("drive", "v3", credentials=creds)
    logger.debug("Google Drive API initialized successfully")
    
    # Initialize Docs API
    docs_service = build("docs", "v1", credentials=creds)
    docs_drive_service = drive_service  # Use same service instance
    logger.debug("Google Docs API initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize Google APIs: {e}")
    logger.error("You may need to re-authorize with expanded scopes. Run: python reauthorize_google_apis.py")
    drive_service = None
    docs_service = None
    docs_drive_service = None

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

@mcp.tool()
def list_github_repos(repo_type: str = "all", sort: str = "updated", per_page: int = 30):
    """List GitHub repositories for the authenticated user.
    
    Args:
        repo_type: Type of repos to list ('all', 'owner', 'member', 'public', 'private'). Default: 'all'
        sort: Sort order ('created', 'updated', 'pushed', 'full_name'). Default: 'updated'  
        per_page: Number of repos per page (max 100). Default: 30
    """
    logger.debug(f"Listing GitHub repos: type={repo_type}, sort={sort}, per_page={per_page}")
    
    if not github_client:
        return {"error": "GitHub API not configured. Please set GITHUB_TOKEN in .env file."}
    
    try:
        # Get the authenticated user
        user = github_client.get_user()
        
        # Validate repo_type parameter
        valid_types = ['all', 'owner', 'member', 'public', 'private']
        if repo_type not in valid_types:
            return {"error": f"Invalid repo_type '{repo_type}'. Must be one of: {', '.join(valid_types)}"}
        
        # Validate sort parameter
        valid_sorts = ['created', 'updated', 'pushed', 'full_name']
        if sort not in valid_sorts:
            return {"error": f"Invalid sort '{sort}'. Must be one of: {', '.join(valid_sorts)}"}
        
        # Validate per_page parameter
        if per_page < 1 or per_page > 100:
            return {"error": "per_page must be between 1 and 100"}
        
        # Get repositories based on type
        if repo_type == "all":
            repos = user.get_repos(sort=sort)
        elif repo_type == "owner":
            repos = user.get_repos(type="owner", sort=sort)
        elif repo_type == "member":
            repos = user.get_repos(type="member", sort=sort)
        elif repo_type == "public":
            repos = user.get_repos(type="public", sort=sort)
        elif repo_type == "private":
            repos = user.get_repos(type="private", sort=sort)
        
        # Convert repositories to list with relevant information
        repo_list = []
        count = 0
        for repo in repos:
            if count >= per_page:
                break
            repo_info = {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "No description",
                "url": repo.html_url,
                "clone_url": repo.clone_url,
                "ssh_url": repo.ssh_url,
                "private": repo.private,
                "language": repo.language,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "size": repo.size,  # in KB
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "pushed_at": repo.pushed_at.isoformat() if repo.pushed_at else None,
                "default_branch": repo.default_branch,
                "archived": repo.archived,
                "disabled": repo.disabled,
                "has_issues": repo.has_issues,
                "has_wiki": repo.has_wiki,
                "has_pages": repo.has_pages,
                "open_issues": repo.open_issues_count
            }
            repo_list.append(repo_info)
            count += 1
        
        # Get user information
        user_info = {
            "username": user.login,
            "name": user.name,
            "total_public_repos": user.public_repos,
            "total_private_repos": user.total_private_repos if hasattr(user, 'total_private_repos') else "N/A",
            "followers": user.followers,
            "following": user.following
        }
        
        logger.debug(f"Retrieved {len(repo_list)} repositories for user {user.login}")
        return {
            "user_info": user_info,
            "repositories": repo_list,
            "count": len(repo_list),
            "filters": {
                "repo_type": repo_type,
                "sort": sort,
                "per_page": per_page
            }
        }
        
    except Exception as e:
        logger.error(f"Error listing GitHub repositories: {e}")
        return {"error": str(e)}

@mcp.tool()
def read_github_repo_files(repo_name: str, file_types: str = "py,js,ts,java,md,txt", max_files: int = 50):
    """Read files from a specific GitHub repository.
    
    Args:
        repo_name: Repository name in format 'owner/repo' (e.g., 'microsoft/vscode')
        file_types: Comma-separated file extensions to read (e.g., 'py,js,ts,java,md'). Default: 'py,js,ts,java,md,txt'
        max_files: Maximum number of files to read (to prevent overwhelming responses). Default: 50
    """
    logger.debug(f"Reading files from repo: {repo_name}, file_types: {file_types}, max_files: {max_files}")
    
    if not github_client:
        return {"error": "GitHub API not configured. Please set GITHUB_TOKEN in .env file."}
    
    try:
        # Parse repository name
        if '/' not in repo_name:
            return {"error": "Repository name must be in format 'owner/repo' (e.g., 'microsoft/vscode')"}
        
        # Get the repository
        try:
            repo = github_client.get_repo(repo_name)
        except Exception as e:
            return {"error": f"Repository '{repo_name}' not found or not accessible: {str(e)}"}
        
        # Parse file types
        allowed_extensions = [ext.strip().lower() for ext in file_types.split(',')]
        if not allowed_extensions:
            allowed_extensions = ['py', 'js', 'ts', 'java', 'md', 'txt']
        
        # Validate max_files
        if max_files < 1 or max_files > 200:
            max_files = 50
        
        # Get repository information
        repo_info = {
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "No description",
            "url": repo.html_url,
            "language": repo.language,
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "default_branch": repo.default_branch,
            "private": repo.private
        }
        
        # Function to recursively get files from repository
        def get_files_recursive(path="", current_depth=0, max_depth=5):
            """Recursively get files from repository with depth limit"""
            if current_depth > max_depth:
                return []
            
            files_found = []
            try:
                contents = repo.get_contents(path)
                if not isinstance(contents, list):
                    contents = [contents]
                
                for content in contents:
                    if len(files_found) >= max_files:
                        break
                        
                    if content.type == "file":
                        # Check if file extension matches our criteria
                        file_name = content.name.lower()
                        file_extension = file_name.split('.')[-1] if '.' in file_name else ''
                        
                        # Special handling for README files
                        is_readme = file_name.startswith('readme')
                        
                        if file_extension in allowed_extensions or is_readme:
                            try:
                                # Get file content (decode from base64)
                                file_content = content.decoded_content.decode('utf-8', errors='ignore')
                                
                                # Limit content size to prevent overwhelming responses
                                max_content_size = 10000  # 10KB per file
                                if len(file_content) > max_content_size:
                                    file_content = file_content[:max_content_size] + f"\n\n... [Content truncated - file is {len(file_content)} characters total]"
                                
                                files_found.append({
                                    "name": content.name,
                                    "path": content.path,
                                    "size": content.size,
                                    "type": "README" if is_readme else file_extension.upper(),
                                    "content": file_content,
                                    "url": content.html_url,
                                    "download_url": content.download_url
                                })
                            except Exception as e:
                                # If we can't decode the file, skip it
                                logger.warning(f"Could not read file {content.path}: {e}")
                                continue
                    
                    elif content.type == "dir" and current_depth < max_depth:
                        # Recursively get files from subdirectory
                        subdir_files = get_files_recursive(content.path, current_depth + 1, max_depth)
                        files_found.extend(subdir_files)
                        
                        if len(files_found) >= max_files:
                            break
                            
            except Exception as e:
                logger.warning(f"Error accessing path '{path}': {e}")
            
            return files_found[:max_files]
        
        # Get all matching files
        logger.debug("Starting recursive file collection...")
        files = get_files_recursive()
        
        # Organize files by type
        files_by_type = {}
        for file_info in files:
            file_type = file_info["type"]
            if file_type not in files_by_type:
                files_by_type[file_type] = []
            files_by_type[file_type].append(file_info)
        
        # Create summary
        summary = {
            "total_files_found": len(files),
            "files_by_type": {file_type: len(file_list) for file_type, file_list in files_by_type.items()},
            "file_types_requested": allowed_extensions,
            "search_depth": "5 levels (max)"
        }
        
        logger.debug(f"Found {len(files)} files in repository {repo_name}")
        return {
            "repository": repo_info,
            "summary": summary,
            "files": files,
            "files_by_type": files_by_type
        }
        
    except Exception as e:
        logger.error(f"Error reading repository files: {e}")
        return {"error": str(e)}

@mcp.tool()
def analyze_github_repo_with_ai(repo_name: str, analysis_type: str = "comprehensive", max_files_to_analyze: int = 20):
    """Analyze a GitHub repository using AI to provide insights and summaries.
    
    Args:
        repo_name: Repository name in format 'owner/repo' (e.g., 'microsoft/vscode')
        analysis_type: Type of analysis ('comprehensive', 'readme_only', 'code_only', 'structure'). Default: 'comprehensive'
        max_files_to_analyze: Maximum number of files to analyze with AI (to manage API costs). Default: 20
    """
    logger.debug(f"AI analyzing repo: {repo_name}, analysis_type: {analysis_type}, max_files: {max_files_to_analyze}")
    
    if not github_client:
        return {"error": "GitHub API not configured. Please set GITHUB_TOKEN in .env file."}
    
    if not gemini_model:
        return {"error": "Gemini AI not configured. Please set GEMINI_API_KEY in .env file."}
    
    try:
        # First, read repository files
        file_types = "py,js,ts,java,md,txt,json,yml,yaml" if analysis_type in ["comprehensive", "code_only"] else "md,txt"
        max_files = min(max_files_to_analyze, 50)  # Limit to prevent overwhelming the AI
        
        files_result = read_github_repo_files(repo_name, file_types, max_files)
        
        if "error" in files_result:
            return files_result
        
        repository = files_result.get("repository", {})
        files = files_result.get("files", [])
        summary = files_result.get("summary", {})
        
        if not files:
            return {"error": "No files found in repository for analysis"}
        
        # Prepare content for AI analysis
        analysis_content = f"""Repository: {repository.get('full_name')}
Description: {repository.get('description', 'No description')}
Primary Language: {repository.get('language', 'N/A')}
Stars: {repository.get('stars', 0)} | Forks: {repository.get('forks', 0)}

Files Summary:
- Total files analyzed: {len(files)}
- File types: {', '.join(summary.get('files_by_type', {}).keys())}

"""
        
        # Add file contents based on analysis type
        readme_files = []
        code_files = []
        other_files = []
        
        for file_info in files:
            if file_info.get('type') == 'README':
                readme_files.append(file_info)
            elif file_info.get('type') in ['PY', 'JS', 'TS', 'JAVA']:
                code_files.append(file_info)
            else:
                other_files.append(file_info)
        
        # Create analysis prompt based on type
        if analysis_type == "readme_only":
            if readme_files:
                analysis_content += "\n=== README FILES ===\n"
                for readme in readme_files:
                    analysis_content += f"\n--- {readme['path']} ---\n{readme['content']}\n"
            prompt = f"""
Please analyze this GitHub repository's README and documentation files and provide:

1. **Project Overview**: What does this project do?
2. **Key Features**: Main functionality and capabilities
3. **Technology Stack**: Technologies and frameworks used
4. **Target Audience**: Who would use this project?
5. **Getting Started**: How to use or contribute to the project
6. **Project Status**: Is it actively maintained? Production ready?

Repository Information:
{analysis_content}
"""
        
        elif analysis_type == "code_only":
            if code_files:
                analysis_content += "\n=== CODE FILES ===\n"
                for code_file in code_files[:max_files_to_analyze]:  # Limit for API efficiency
                    analysis_content += f"\n--- {code_file['path']} ---\n{code_file['content'][:2000]}...\n"  # Limit content per file
            prompt = f"""
Please analyze this GitHub repository's code files and provide:

1. **Code Architecture**: Overall structure and organization
2. **Programming Patterns**: Design patterns and coding style used
3. **Key Functions/Classes**: Most important code components
4. **Dependencies**: External libraries and frameworks used
5. **Code Quality**: Assessment of code organization and practices
6. **Functionality**: What the code actually does

Repository Information:
{analysis_content}
"""
        
        elif analysis_type == "structure":
            file_structure = []
            for file_info in files:
                file_structure.append(f"{file_info['path']} ({file_info['type']}) - {file_info['size']} bytes")
            
            analysis_content += f"\n=== PROJECT STRUCTURE ===\n"
            analysis_content += "\n".join(file_structure)
            
            prompt = f"""
Please analyze this GitHub repository's structure and organization:

1. **Project Structure**: How is the project organized?
2. **File Organization**: Patterns in directory and file structure
3. **Project Type**: What kind of project is this? (web app, library, tool, etc.)
4. **Build System**: What build tools or configuration files are present?
5. **Development Workflow**: Evidence of testing, CI/CD, documentation practices
6. **Project Maturity**: How mature/complete does the project appear?

Repository Information:
{analysis_content}
"""
        
        else:  # comprehensive
            # Include samples from all file types
            analysis_content += "\n=== README FILES ===\n"
            for readme in readme_files:
                analysis_content += f"\n--- {readme['path']} ---\n{readme['content'][:1500]}...\n"
            
            analysis_content += "\n=== CODE FILES (SAMPLE) ===\n"
            for code_file in code_files[:5]:  # Just first 5 for comprehensive analysis
                analysis_content += f"\n--- {code_file['path']} ---\n{code_file['content'][:1000]}...\n"
            
            analysis_content += "\n=== OTHER FILES ===\n"
            for other_file in other_files[:3]:  # Just first 3
                analysis_content += f"\n--- {other_file['path']} ---\n{other_file['content'][:500]}...\n"
            
            prompt = f"""
Please provide a comprehensive analysis of this GitHub repository:

1. **Project Overview**: What is this project and what does it do?
2. **Technology Stack**: Languages, frameworks, and tools used
3. **Architecture & Structure**: How is the project organized?
4. **Key Features**: Main functionality and capabilities
5. **Code Quality & Practices**: Assessment of development practices
6. **Usage & Audience**: Who would use this and how?
7. **Project Health**: Activity level, maintenance status, maturity
8. **Getting Started**: How someone could use or contribute to this project
9. **Notable Insights**: Anything interesting or unique about this project

Repository Information:
{analysis_content}
"""
        
        # Limit prompt size for API efficiency
        if len(prompt) > 25000:  # Reasonable limit for Gemini
            prompt = prompt[:25000] + "\n\n[Content truncated for analysis efficiency]"
        
        # Generate AI analysis
        logger.debug("Generating AI analysis using Gemini")
        response = gemini_model.generate_content(prompt)
        
        if not response.text:
            return {"error": "AI analysis failed to generate content"}
        
        # Create comprehensive result
        result = {
            "repository_info": repository,
            "analysis_type": analysis_type,
            "files_analyzed": {
                "total_files": len(files),
                "readme_files": len(readme_files),
                "code_files": len(code_files),
                "other_files": len(other_files),
                "file_types": summary.get('files_by_type', {})
            },
            "ai_analysis": response.text,
            "analysis_metadata": {
                "model_used": "gemini-2.5-flash",
                "max_files_analyzed": max_files_to_analyze,
                "analysis_timestamp": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""),
                "content_size_analyzed": len(analysis_content)
            }
        }
        
        logger.debug(f"AI analysis completed for {repo_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error in AI repository analysis: {e}")
        return {"error": str(e)}

@mcp.tool()
def summarize_repo_analysis_for_resume(repo_name: str, analysis_text: str, focus_area: str = "technical"):
    """Summarize repository analysis into 3 resume-worthy bullet points using AI.
    
    Args:
        repo_name: Repository name (e.g., 'microsoft/vscode')
        analysis_text: The AI analysis text to summarize
        focus_area: Focus of the summary ('technical', 'leadership', 'impact', 'learning'). Default: 'technical'
    """
    logger.debug(f"Creating resume summary for {repo_name}, focus: {focus_area}")
    
    if not gemini_model:
        return {"error": "Gemini AI not configured. Please set GEMINI_API_KEY in .env file."}
    
    try:
        # Create focused prompt based on area
        focus_prompts = {
            "technical": "technical skills, programming languages, frameworks, and software engineering practices",
            "leadership": "project leadership, collaboration, open source contribution, and community impact", 
            "impact": "business impact, user benefits, scalability, and measurable outcomes",
            "learning": "learning experiences, skill development, problem-solving, and growth opportunities"
        }
        
        focus_description = focus_prompts.get(focus_area, focus_prompts["technical"])
        
        prompt = f"""
Based on the following analysis of GitHub repository '{repo_name}', create exactly 3 professional bullet points suitable for a resume.

Focus on: {focus_description}

Requirements:
1. Each bullet point should be 1-2 lines maximum
2. Use action words and quantifiable achievements where possible
3. Make them relevant for a software engineer's resume
4. Format each point starting with a strong action verb
5. Be specific about technologies, patterns, or practices mentioned
6. Make them sound professional and impactful

Repository Analysis:
{analysis_text[:8000]}

Please provide exactly 3 bullet points in this format:
• [First bullet point]
• [Second bullet point]  
• [Third bullet point]
"""
        
        # Generate summary using Gemini
        logger.debug("Generating resume summary using Gemini")
        response = gemini_model.generate_content(prompt)
        
        if not response.text:
            return {"error": "AI failed to generate resume summary"}
        
        # Clean up the response to extract bullet points
        summary_text = response.text.strip()
        
        # Extract bullet points
        bullet_points = []
        lines = summary_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                # Clean up the bullet point
                clean_point = line[1:].strip()  # Remove bullet symbol
                if clean_point:
                    bullet_points.append(clean_point)
        
        # Ensure we have exactly 3 points
        if len(bullet_points) < 3:
            # If we didn't get proper bullet points, try to split the response
            sentences = summary_text.replace('•', '\n').replace('-', '\n').replace('*', '\n').split('\n')
            bullet_points = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10][:3]
        
        bullet_points = bullet_points[:3]  # Take only first 3
        
        # Ensure we have at least 3 points
        while len(bullet_points) < 3:
            bullet_points.append(f"Analyzed and studied {repo_name} repository architecture and implementation")
        
        result = {
            "repository": repo_name,
            "focus_area": focus_area,
            "bullet_points": bullet_points,
            "formatted_summary": "\n".join([f"• {point}" for point in bullet_points]),
            "original_analysis_length": len(analysis_text),
            "summary_metadata": {
                "generated_at": str(logger.handlers[0].formatter.formatTime(logger.makeRecord("", 0, "", 0, "", (), None)) if logger.handlers else ""),
                "focus_area": focus_area,
                "model_used": "gemini-2.5-flash"
            }
        }
        
        logger.debug(f"Generated {len(bullet_points)} resume bullet points for {repo_name}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating resume summary: {e}")
        return {"error": str(e)}

@mcp.tool()
def list_google_docs(search_term: str = "resume"):
    """List Google Docs documents, optionally filtered by search term.
    
    Args:
        search_term: Search term to filter documents (default: 'resume')
    """
    logger.debug(f"Listing Google Docs with search term: {search_term}")
    
    if not docs_drive_service:
        return {"error": "Google Docs API not configured. Please check your credentials and permissions."}
    
    try:
        # Search for Google Docs documents
        query = f"mimeType='application/vnd.google-apps.document' and trashed=false"
        if search_term:
            query += f" and name contains '{search_term}'"
        
        results = docs_drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType, webViewLink, modifiedTime, owners)",
            pageSize=20
        ).execute()
        
        files = results.get("files", [])
        
        docs_list = []
        for file in files:
            doc_info = {
                "id": file["id"],
                "name": file["name"],
                "link": file["webViewLink"],
                "modified": file.get("modifiedTime", "Unknown"),
                "owners": [owner.get("displayName", "Unknown") for owner in file.get("owners", [])]
            }
            docs_list.append(doc_info)
        
        logger.debug(f"Found {len(docs_list)} Google Docs documents")
        return {
            "search_term": search_term,
            "documents": docs_list,
            "count": len(docs_list)
        }
        
    except Exception as e:
        logger.error(f"Error listing Google Docs: {e}")
        return {"error": str(e)}

@mcp.tool()
def add_to_google_doc(doc_id: str, content: str, section_title: str = "GitHub Repository Analysis"):
    """Add content to a Google Docs document.
    
    Args:
        doc_id: Google Docs document ID
        content: Content to add (should include bullet points)
        section_title: Title for the section being added (default: 'GitHub Repository Analysis')
    """
    logger.debug(f"Adding content to Google Doc: {doc_id}")
    
    if not docs_service:
        return {"error": "Google Docs API not configured. Please check your credentials and permissions."}
    
    try:
        # First, get the current document to find the end
        doc = docs_service.documents().get(documentId=doc_id).execute()
        doc_content = doc.get('body', {})
        
        # Get the end index of the document
        end_index = doc_content.get('content', [{}])[-1].get('endIndex', 1) - 1
        
        # Prepare the content to insert
        formatted_content = f"\n\n{section_title}\n{content}\n"
        
        # Create the requests for inserting content
        requests = [
            {
                'insertText': {
                    'location': {
                        'index': end_index,
                    },
                    'text': formatted_content
                }
            }
        ]
        
        # Apply the updates
        result = docs_service.documents().batchUpdate(
            documentId=doc_id,
            body={'requests': requests}
        ).execute()
        
        # Get document info for response
        doc_info = {
            "document_id": doc_id,
            "title": doc.get('title', 'Unknown'),
            "content_added": content,
            "section_title": section_title,
            "insertion_index": end_index,
            "web_view_link": f"https://docs.google.com/document/d/{doc_id}/edit"
        }
        
        logger.debug(f"Successfully added content to Google Doc: {doc.get('title', 'Unknown')}")
        return {
            "success": True,
            "message": f"Content added to document '{doc.get('title', 'Unknown')}'",
            "document_info": doc_info,
            "batch_update_result": result
        }
        
    except Exception as e:
        logger.error(f"Error adding content to Google Doc: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    logger.debug("Starting MCP server")
    try:
        mcp.run()
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        raise