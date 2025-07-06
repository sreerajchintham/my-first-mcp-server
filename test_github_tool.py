#!/usr/bin/env python3
"""
Test script for the GitHub repository creation tool
"""

import asyncio
import json
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

async def test_github_repo_creation():
    """Test the create_github_repo tool"""
    
    print("🚀 Testing GitHub Repository Creation Tool")
    print("=" * 60)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python", 
        args=["mcp_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # List available tools to confirm GitHub tool is available
                tools_result = await session.list_tools()
                github_tool_available = any(tool.name == "create_github_repo" for tool in tools_result.tools)
                
                if not github_tool_available:
                    print("❌ create_github_repo tool not found!")
                    return
                
                print("✅ create_github_repo tool is available")
                
                # Get a Colab file to use for testing
                print("\n📁 Getting Colab files...")
                files_result = await session.call_tool("list_colab_files", {"folder_id": None})
                
                # Parse the first file
                first_file = None
                for content in files_result.content:
                    if hasattr(content, 'text'):
                        try:
                            file_data = json.loads(content.text)
                            if isinstance(file_data, list) and file_data:
                                first_file = file_data[0]  # Get the first file from the list
                                break
                            elif isinstance(file_data, dict) and 'id' in file_data:
                                first_file = file_data
                                break
                        except:
                            continue
                
                if not first_file:
                    print("❌ No Colab files found for testing")
                    return
                
                print(f"📝 Using file: {first_file['name']}")
                print(f"🆔 File ID: {first_file['id']}")
                
                # Ask user for repository details
                print("\n" + "="*60)
                print("📋 Repository Configuration")
                print("="*60)
                
                # Generate a safe repository name from the file name
                base_name = first_file['name'].replace('.ipynb', '').replace(' ', '-').lower()
                # Remove any special characters
                safe_name = ''.join(c for c in base_name if c.isalnum() or c in '-_')
                
                repo_name = input(f"Repository name (default: {safe_name}): ").strip() or safe_name
                repo_description = input(f"Repository description (optional): ").strip()
                is_private_input = input("Make repository private? (y/N): ").strip().lower()
                is_private = is_private_input in ['y', 'yes', '1', 'true']
                
                print(f"\n🔧 Creating repository '{repo_name}'...")
                print(f"📄 Description: {repo_description or 'None'}")
                print(f"🔒 Private: {is_private}")
                print(f"📓 Source file: {first_file['name']}")
                
                # Confirm before creating
                confirm = input("\nProceed with creation? (Y/n): ").strip().lower()
                if confirm in ['n', 'no', '0', 'false']:
                    print("❌ Repository creation cancelled")
                    return
                
                # Create the repository
                print("\n🚀 Creating GitHub repository...")
                try:
                    result = await session.call_tool("create_github_repo", {
                        "file_id": first_file["id"],
                        "file_name": first_file["name"], 
                        "repo_name": repo_name,
                        "repo_description": repo_description,
                        "is_private": is_private
                    })
                    
                    # Display the result
                    for content in result.content:
                        if hasattr(content, 'text'):
                            try:
                                response_data = json.loads(content.text)
                                
                                if response_data.get("success"):
                                    print("\n🎉 Repository created successfully!")
                                    print("=" * 60)
                                    
                                    repo_info = response_data.get("repository", {})
                                    print(f"📁 Repository: {repo_info.get('repo_name')}")
                                    print(f"🌐 URL: {repo_info.get('repo_url')}")
                                    print(f"📡 Clone URL: {repo_info.get('clone_url')}")
                                    print(f"🔑 SSH URL: {repo_info.get('ssh_url')}")
                                    print(f"👤 Owner: {repo_info.get('owner')}")
                                    print(f"🔒 Private: {repo_info.get('is_private')}")
                                    print(f"📅 Created: {repo_info.get('created_at')}")
                                    
                                    files_uploaded = repo_info.get('files_uploaded', [])
                                    print(f"\n📄 Files uploaded ({len(files_uploaded)}):")
                                    for file in files_uploaded:
                                        print(f"  ✅ {file}")
                                    
                                    print("\n🎯 Next steps:")
                                    print(f"1. Visit: {repo_info.get('repo_url')}")
                                    print(f"2. Clone: git clone {repo_info.get('clone_url')}")
                                    print("3. Start coding!")
                                    
                                elif "error" in response_data:
                                    print(f"\n❌ Error: {response_data['error']}")
                                else:
                                    print(f"\n🤔 Unexpected response: {response_data}")
                                    
                            except json.JSONDecodeError:
                                print(f"❌ Could not parse response: {content.text}")
                            except Exception as e:
                                print(f"❌ Error processing response: {e}")
                        else:
                            print(f"❌ Unexpected content type: {type(content)}")
                
                except Exception as e:
                    print(f"❌ Error calling create_github_repo: {e}")
                    
    except Exception as e:
        print(f"❌ Client error: {e}")

if __name__ == "__main__":
    print("⚠️  Make sure you have:")
    print("  1. GITHUB_TOKEN configured in .env")
    print("  2. GitHub API access permissions")
    print("  3. At least one Colab notebook in your Drive")
    print()
    
    asyncio.run(test_github_repo_creation()) 