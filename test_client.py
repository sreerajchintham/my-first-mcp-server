from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession
import asyncio
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_mcp_server():
    # Create server parameters
    server_params = StdioServerParameters(
        command="python", 
        args=["mcp_server.py"]
    )
    
    # Connect to the MCP server
    logger.debug("Connecting to MCP server")
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Create a client session
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                logger.debug("Initializing client session")
                await session.initialize()
                
                # List available tools
                logger.debug("Listing available tools")
                tools_result = await session.list_tools()
                print("Available tools:")
                if tools_result.tools:
                    for tool in tools_result.tools:
                        print(f" TOOL NAME - {tool.name}\n  TOOL DESCRIPTION - {tool.description}\n\n")
                else:
                    print("  No tools found")
                
                # Test the ping tool
                if any(tool.name == "ping" for tool in tools_result.tools):
                    logger.debug("Calling ping tool")
                    print("\nTesting ping tool...")
                    result = await session.call_tool("ping", {})
                    print("Ping result:")
                    for content in result.content:
                        if hasattr(content, 'text'):
                            print(f"  Text: {content.text}")
                        else:
                            print(f"  Content: {content}")
                
                # Test the list_colab_files tool
                if any(tool.name == "list_colab_files" for tool in tools_result.tools):
                    logger.debug("Calling list_colab_files tool")
                    print("\nTesting list_colab_files tool...")
                    result = await session.call_tool("list_colab_files", {"folder_id": None})
                    print("Colab files:")
                    files = []
                    for content in result.content:
                        if isinstance(content, list):
                            if content:
                                for file in content:
                                    # Clean the file data
                                    clean_file = {
                                        'id': file['id'].strip(),
                                        'name': file['name'].strip(),
                                        'link': file['link'].strip()
                                    }
                                    print(f" FILE NAME - {clean_file['name']} \n FILE ID - {clean_file['id']} \n FILE LINK - {clean_file['link']}\n\n")
                                    files.append(clean_file)
                            else:
                                print("  No Colab files found")
                        elif hasattr(content, 'text'):
                            try:
                                files_data = json.loads(content.text)
                                if isinstance(files_data, dict) and "error" in files_data:
                                    print(f"  Error: {files_data['error']}")
                                elif isinstance(files_data, list):
                                    if files_data:
                                        for file in files_data:
                                            # Clean the file data
                                            clean_file = {
                                                'id': file['id'].strip(),
                                                'name': file['name'].strip(),
                                                'link': file['link'].strip()
                                            }
                                            print(f"  - {clean_file['name']} (ID: {clean_file['id']}, Link: {clean_file['link']})")
                                            files.append(clean_file)
                                    else:
                                        print("  No Colab files found")
                                elif isinstance(files_data, dict) and all(key in files_data for key in ['id', 'name', 'link']):
                                    # Single file response
                                    clean_file = {
                                        'id': files_data['id'].strip(),
                                        'name': files_data['name'].strip(),
                                        'link': files_data['link'].strip()
                                    }
                                    print(f" FILE NAME - {clean_file['name']} \n FILE ID - {clean_file['id']} \n FILE LINK - {clean_file['link']}\n\n")
                                    files.append(clean_file)
                                else:
                                    print(f"  Unexpected response: {files_data}")
                            except json.JSONDecodeError:
                                print(f"  Invalid JSON: {content.text}")
                        else:
                            print(f"  Unexpected content: {content}")
                
                # Test the read_colab_notebook tool
                if any(tool.name == "read_colab_notebook" for tool in tools_result.tools):
                    logger.debug("Calling read_colab_notebook tool")
                    print("\nTesting read_colab_notebook tool...")
                    file_id = (files[0]["id"] if files else "1oRjsGE_ndKocKtIo_6qK2Wsslgfw46yo").strip()
                    result = await session.call_tool("read_colab_notebook", {"file_id": file_id})
                    print("Notebook content:")
                    for content in result.content:
                        if isinstance(content, dict):
                            if "error" in content:
                                print(f"  Error: {content['error']}")
                            else:
                                metadata = content.get("metadata", {})
                                cells = content.get("cells", [])
                                print(f"  Metadata: Name={metadata.get('name', 'Unknown')}, Cell Count={metadata.get('cell_count', 0)}")
                                print("  First few cells:")
                                for i, cell in enumerate(cells[:3]):
                                    print(f"    Cell {i+1} ({cell['cell_type']}): {cell['source'][:100]}...")
                        elif hasattr(content, 'text'):
                            try:
                                data = json.loads(content.text)
                                if isinstance(data, dict) and "error" in data:
                                    print(f"  Error: {data['error']}")
                                elif isinstance(data, dict):
                                    metadata = data.get("metadata", {})
                                    cells = data.get("cells", [])
                                    print(f"  Metadata: Name={metadata.get('name', 'Unknown')}, Cell Count={metadata.get('cell_count', 0)}")
                                    print("  First few cells:")
                                    for i, cell in enumerate(cells[:3]):
                                        print(f"    Cell {i+1} ({cell['cell_type']}): {cell['source'][:100]}...")
                                else:
                                    print(f"  Unexpected response: {data}")
                            except json.JSONDecodeError:
                                print(f"  Invalid JSON: {content.text}")
                        else:
                            print(f"  Unexpected content: {content}")
                
                # Test the generate_readme tool
                if any(tool.name == "generate_readme" for tool in tools_result.tools):
                    logger.debug("Calling generate_readme tool")
                    print("\nTesting generate_readme tool...")
                    file_id = (files[0]["id"] if files else "1oRjsGE_ndKocKtIo_6qK2Wsslgfw46yo").strip()
                    file_name = (files[0]["name"] if files else "cdist2.ipynb").strip()
                    result = await session.call_tool("generate_readme", {"file_id": file_id, "file_name": file_name})
                    print("README content:")
                    for content in result.content:
                        if isinstance(content, dict):
                            if "error" in content:
                                print(f"  Error: {content['error']}")
                            else:
                                readme = content.get("readme", "")
                                print(f"  README:\n{readme}")
                        elif hasattr(content, 'text'):
                            try:
                                data = json.loads(content.text)
                                if isinstance(data, dict) and "error" in data:
                                    print(f"  Error: {data['error']}")
                                elif isinstance(data, dict):
                                    readme = data.get("readme", "")
                                    print(f"  README:\n{readme}")
                                else:
                                    print(f"  Unexpected response: {data}")
                            except json.JSONDecodeError:
                                print(f"  Invalid JSON: {content.text}")
                        else:
                            print(f"  Unexpected content: {content}")
                
                # Test the create_github_repo tool
                if any(tool.name == "create_github_repo" for tool in tools_result.tools):
                    logger.debug("Calling create_github_repo tool")
                    print("\nTesting create_github_repo tool...")
                    
                    # Use first file or default for testing
                    file_id = (files[0]["id"] if files else "1oRjsGE_ndKocKtIo_6qK2Wsslgfw46yo").strip()
                    file_name = (files[0]["name"] if files else "cdist2.ipynb").strip()
                    
                    # Generate a test repository name
                    import time
                    timestamp = str(int(time.time()))
                    base_name = file_name.replace('.ipynb', '').replace(' ', '-').lower()
                    safe_name = ''.join(c for c in base_name if c.isalnum() or c in '-_')
                    test_repo_name = f"test-{safe_name}-{timestamp}"
                    
                    print(f"  Creating test repository: {test_repo_name}")
                    print(f"  Using file: {file_name} (ID: {file_id})")
                    print(f"  Note: This will create a real GitHub repository!")
                    
                    # Ask for confirmation in non-automated mode
                    should_create_repo = False
                    try:
                        # Try to get user input, but don't block if running in automated mode
                        import sys
                        if sys.stdin.isatty():  # Only ask if running interactively
                            confirm = input("  Do you want to create the GitHub repository? (y/N): ").strip().lower()
                            if confirm in ['y', 'yes', '1']:
                                should_create_repo = True
                            else:
                                print("  Skipping GitHub repository creation.")
                        else:
                            print("  Skipping GitHub repository creation (non-interactive mode).")
                    except:
                        # If we can't get input, skip the GitHub test
                        print("  Skipping GitHub repository creation (non-interactive mode).")
                    
                    if should_create_repo:
                        # Call the GitHub tool
                        result = await session.call_tool("create_github_repo", {
                            "file_id": file_id,
                            "file_name": file_name,
                            "repo_name": test_repo_name,
                            "repo_description": f"Test repository created from {file_name}",
                            "is_private": False
                        })
                        
                        print("GitHub repository creation result:")
                        for content in result.content:
                            if isinstance(content, dict):
                                if "error" in content:
                                    print(f"  Error: {content['error']}")
                                elif "success" in content and content["success"]:
                                    print(f"  ✅ Success: {content['message']}")
                                    repo_info = content.get("repository", {})
                                    print(f"  📁 Repository: {repo_info.get('repo_name')}")
                                    print(f"  🌐 URL: {repo_info.get('repo_url')}")
                                    print(f"  👤 Owner: {repo_info.get('owner')}")
                                    print(f"  🔒 Private: {repo_info.get('is_private')}")
                                    files_uploaded = repo_info.get('files_uploaded', [])
                                    print(f"  📄 Files uploaded: {', '.join(files_uploaded)}")
                                else:
                                    print(f"  Unexpected response: {content}")
                            elif hasattr(content, 'text'):
                                try:
                                    data = json.loads(content.text)
                                    if isinstance(data, dict) and "error" in data:
                                        print(f"  Error: {data['error']}")
                                    elif isinstance(data, dict) and "success" in data and data["success"]:
                                        print(f"  ✅ Success: {data['message']}")
                                        repo_info = data.get("repository", {})
                                        print(f"  📁 Repository: {repo_info.get('repo_name')}")
                                        print(f"  🌐 URL: {repo_info.get('repo_url')}")
                                        print(f"  👤 Owner: {repo_info.get('owner')}")
                                        print(f"  🔒 Private: {repo_info.get('is_private')}")
                                        files_uploaded = repo_info.get('files_uploaded', [])
                                        print(f"  📄 Files uploaded: {', '.join(files_uploaded)}")
                                    else:
                                        print(f"  Unexpected response: {data}")
                                except json.JSONDecodeError:
                                    print(f"  Invalid JSON: {content.text}")
                            else:
                                print(f"  Unexpected content: {content}")
    except Exception as e:
        logger.error(f"Client error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())