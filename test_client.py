from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession
import asyncio
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_list_github_repos(session):
    """Test the list_github_repos tool with interactive options"""
    
    print("\n🐙 GitHub Repository List Tool")
    print("=" * 50)
    
    # Get user preferences for listing repos
    print("Repository filtering options:")
    print("1. All repositories (default)")
    print("2. Only repositories you own")
    print("3. Only repositories you're a member of")
    print("4. Only public repositories")
    print("5. Only private repositories")
    
    type_choice = input("Select repository type (1-5, default: 1): ").strip()
    repo_types = {"1": "all", "2": "owner", "3": "member", "4": "public", "5": "private"}
    repo_type = repo_types.get(type_choice, "all")
    
    print("\nSorting options:")
    print("1. Recently updated (default)")
    print("2. Recently created")
    print("3. Recently pushed")
    print("4. Alphabetical")
    
    sort_choice = input("Select sorting (1-4, default: 1): ").strip()
    sort_options = {"1": "updated", "2": "created", "3": "pushed", "4": "full_name"}
    sort = sort_options.get(sort_choice, "updated")
    
    per_page = input("Number of repositories to fetch (1-100, default: 30): ").strip()
    try:
        per_page = int(per_page) if per_page else 30
        if per_page < 1 or per_page > 100:
            per_page = 30
    except ValueError:
        per_page = 30
    
    print(f"\n🔍 Fetching repositories (type: {repo_type}, sort: {sort}, limit: {per_page})...")
    
    try:
        repos_result = await session.call_tool("list_github_repos", {
            "repo_type": repo_type,
            "sort": sort,
            "per_page": per_page
        })
        
        for content in repos_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if "error" in data:
                            print(f"❌ Error: {data['error']}")
                            return
                        
                        user_info = data.get("user_info", {})
                        repositories = data.get("repositories", [])
                        count = data.get("count", 0)
                        
                        # Display user information
                        print(f"\n👤 GitHub User: {user_info.get('username')} ({user_info.get('name', 'N/A')})")
                        print(f"📊 Total Public Repos: {user_info.get('total_public_repos', 'N/A')}")
                        print(f"🔒 Total Private Repos: {user_info.get('total_private_repos', 'N/A')}")
                        print(f"👥 Followers: {user_info.get('followers', 0)} | Following: {user_info.get('following', 0)}")
                        
                        if not repositories:
                            print("\n📭 No repositories found with the selected criteria.")
                            return
                        
                        # Display repositories
                        print(f"\n📁 Found {count} repositories:")
                        print("=" * 100)
                        
                        for i, repo in enumerate(repositories, 1):
                            print(f"{i:2d}. {repo.get('name')} {'🔒' if repo.get('private') else '🌐'}")
                            print(f"    📝 {repo.get('description', 'No description')}")
                            print(f"    🌐 {repo.get('url')}")
                            print(f"    💻 Language: {repo.get('language', 'N/A')} | ⭐ Stars: {repo.get('stars', 0)} | 🍴 Forks: {repo.get('forks', 0)}")
                            print(f"    📅 Updated: {repo.get('updated_at', 'N/A')[:10]}")
                            
                            if repo.get('archived'):
                                print("    📦 ARCHIVED")
                            if repo.get('disabled'):
                                print("    ⚠️  DISABLED")
                            
                            print()
                        
                        # Ask if user wants to explore a specific repository
                        explore_choice = input(f"Explore a specific repository (1-{count}) or press Enter to continue: ").strip()
                        if explore_choice:
                            try:
                                repo_index = int(explore_choice) - 1
                                if 0 <= repo_index < len(repositories):
                                    selected_repo = repositories[repo_index]
                                    await explore_repository_interactive(session, selected_repo)
                                else:
                                    print("❌ Invalid repository number")
                            except (ValueError, IndexError):
                                print("❌ Invalid repository number")
                        
                        break
                except json.JSONDecodeError:
                    print(f"❌ Could not parse response: {content.text}")
    
    except Exception as e:
        print(f"❌ Error listing repositories: {e}")

async def explore_repository_interactive(session, repo_info):
    """Comprehensive repository exploration interface"""
    
    print(f"\n🔍 Exploring Repository: {repo_info.get('full_name')}")
    print("=" * 70)
    
    while True:
        # Display repository summary
        print(f"\n📁 Repository: {repo_info.get('full_name')}")
        print(f"📝 Description: {repo_info.get('description', 'No description')}")
        print(f"💻 Language: {repo_info.get('language', 'N/A')} | ⭐ Stars: {repo_info.get('stars', 0)} | 🍴 Forks: {repo_info.get('forks', 0)}")
        print(f"🌐 URL: {repo_info.get('url')}")
        
        print("\n🔧 Exploration Options:")
        print("1. 📊 View detailed repository information")
        print("2. 📂 Read repository files")
        print("3. 🤖 AI Analysis - Comprehensive")
        print("4. 🤖 AI Analysis - README only")
        print("5. 🤖 AI Analysis - Code only")
        print("6. 🤖 AI Analysis - Structure only")
        print("7. 🔄 Combined: Read files + AI analysis")
        print("8. 🎯 Create resume summary and add to Google Docs")
        print("9. ⬅️  Back to repository list")
        
        choice = input("\nSelect exploration option (1-9): ").strip()
        
        if choice == "1":
            # Detailed repository info
            print(f"\n📖 Detailed Repository Information")
            print("=" * 60)
            print(f"Name: {repo_info.get('name')}")
            print(f"Full Name: {repo_info.get('full_name')}")
            print(f"Description: {repo_info.get('description', 'No description')}")
            print(f"URL: {repo_info.get('url')}")
            print(f"Clone URL: {repo_info.get('clone_url')}")
            print(f"SSH URL: {repo_info.get('ssh_url')}")
            print(f"Primary Language: {repo_info.get('language', 'N/A')}")
            print(f"Repository Size: {repo_info.get('size', 0)} KB")
            print(f"Stars: {repo_info.get('stars', 0)}")
            print(f"Forks: {repo_info.get('forks', 0)}")
            print(f"Open Issues: {repo_info.get('open_issues', 0)}")
            print(f"Default Branch: {repo_info.get('default_branch', 'N/A')}")
            print(f"Private Repository: {repo_info.get('private', False)}")
            print(f"Has Issues: {repo_info.get('has_issues', False)}")
            print(f"Has Wiki: {repo_info.get('has_wiki', False)}")
            print(f"Has GitHub Pages: {repo_info.get('has_pages', False)}")
            print(f"Created: {repo_info.get('created_at', 'N/A')}")
            print(f"Last Updated: {repo_info.get('updated_at', 'N/A')}")
            print(f"Last Push: {repo_info.get('pushed_at', 'N/A')}")
            print(f"Archived: {repo_info.get('archived', False)}")
            print(f"Disabled: {repo_info.get('disabled', False)}")
        
        elif choice == "2":
            # Read repository files
            print("\n📂 Reading Repository Files...")
            await read_repository_files_for_repo(session, repo_info.get('full_name'))
        
        elif choice in ["3", "4", "5", "6"]:
            # AI Analysis
            analysis_types = {
                "3": "comprehensive",
                "4": "readme_only", 
                "5": "code_only",
                "6": "structure"
            }
            analysis_type = analysis_types[choice]
            await analyze_repository_with_ai(session, repo_info.get('full_name'), analysis_type)
        
        elif choice == "7":
            # Combined analysis
            await combined_repository_analysis(session, repo_info.get('full_name'))
        
        elif choice == "8":
            # Create resume summary and add to Google Docs
            await create_resume_summary_for_repo(session, repo_info.get('full_name'))
        
        elif choice == "9":
            # Back to repository list
            print("⬅️ Returning to repository list...")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-9.")
        
        if choice != "8":
            input("\nPress Enter to continue exploring this repository...")

async def read_repository_files_for_repo(session, repo_name):
    """Streamlined file reading for a specific repository"""
    
    print(f"📂 Reading files from {repo_name}")
    
    # Get file type preference
    print("\nFile type options:")
    print("1. Default (Python, JS, TS, Java, Markdown, Text)")
    print("2. Documentation only (.md, .txt)")
    print("3. Code only (.py, .js, .ts, .java)")
    print("4. Custom")
    
    type_choice = input("Select file types (1-4, default: 1): ").strip()
    
    file_types_map = {
        "1": "py,js,ts,java,md,txt",
        "2": "md,txt,rst",
        "3": "py,js,ts,java,cpp,c,h",
        "4": None
    }
    
    if type_choice == "4":
        file_types = input("Enter file extensions (comma-separated): ").strip()
        if not file_types:
            file_types = "py,js,ts,java,md,txt"
    else:
        file_types = file_types_map.get(type_choice, "py,js,ts,java,md,txt")
    
    max_files = 30  # Reasonable default for exploration
    
    try:
        result = await session.call_tool("read_github_repo_files", {
            "repo_name": repo_name,
            "file_types": file_types,
            "max_files": max_files
        })
        
        for content in result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if "error" in data:
                            print(f"❌ Error: {data['error']}")
                            return
                        
                        files = data.get("files", [])
                        summary = data.get("summary", {})
                        
                        print(f"\n📊 Found {len(files)} files")
                        print("Files by type:")
                        for file_type, count in summary.get('files_by_type', {}).items():
                            print(f"  {file_type}: {count} files")
                        
                        if files:
                            # Show file list
                            print(f"\n📄 File List:")
                            for i, file_info in enumerate(files, 1):
                                print(f"{i:2d}. {file_info['path']} ({file_info['type']})")
                            
                            # Quick actions
                            print("\nQuick actions:")
                            print("1. Show all README files")
                            print("2. View specific file")
                            print("3. Show files by type")
                            
                            action = input("Select action (1-3) or press Enter to continue: ").strip()
                            
                            if action == "1":
                                readme_files = [f for f in files if f['type'] == 'README']
                                if readme_files:
                                    print("\n📚 README Files:")
                                    for readme in readme_files:
                                        print(f"\n--- {readme['path']} ---")
                                        print(readme['content'][:1000] + "..." if len(readme['content']) > 1000 else readme['content'])
                                else:
                                    print("No README files found")
                            
                            elif action == "2":
                                try:
                                    file_num = int(input(f"Enter file number (1-{len(files)}): "))
                                    if 1 <= file_num <= len(files):
                                        selected_file = files[file_num - 1]
                                        print(f"\n📖 {selected_file['path']}:")
                                        print("=" * 60)
                                        print(selected_file['content'])
                                        print("=" * 60)
                                except (ValueError, IndexError):
                                    print("Invalid file number")
                            
                            elif action == "3":
                                files_by_type = data.get("files_by_type", {})
                                for file_type, type_files in files_by_type.items():
                                    print(f"\n{file_type} Files:")
                                    for file_info in type_files:
                                        print(f"  📄 {file_info['path']}")
                        
                        break
                except json.JSONDecodeError:
                    print(f"❌ Could not parse response")
    
    except Exception as e:
        print(f"❌ Error reading files: {e}")

async def analyze_repository_with_ai(session, repo_name, analysis_type):
    """AI analysis for a specific repository"""
    
    analysis_names = {
        "comprehensive": "Comprehensive Analysis",
        "readme_only": "README & Documentation Analysis", 
        "code_only": "Code Analysis",
        "structure": "Project Structure Analysis"
    }
    
    print(f"\n🤖 {analysis_names.get(analysis_type, 'AI Analysis')} for {repo_name}")
    print("This may take a moment...")
    
    try:
        result = await session.call_tool("analyze_github_repo_with_ai", {
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "max_files_to_analyze": 25
        })
        
        for content in result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if "error" in data:
                            print(f"❌ Error: {data['error']}")
                            return
                        
                        files_analyzed = data.get("files_analyzed", {})
                        ai_analysis = data.get("ai_analysis", "")
                        
                        print(f"\n📊 Analysis Summary:")
                        print(f"  Files analyzed: {files_analyzed.get('total_files', 0)}")
                        print(f"  README files: {files_analyzed.get('readme_files', 0)}")
                        print(f"  Code files: {files_analyzed.get('code_files', 0)}")
                        print(f"  Other files: {files_analyzed.get('other_files', 0)}")
                        
                        print(f"\n🤖 AI Analysis Results:")
                        print("=" * 80)
                        print(ai_analysis)
                        print("=" * 80)
                        
                        break
                except json.JSONDecodeError:
                    print(f"❌ Could not parse analysis response")
    
    except Exception as e:
        print(f"❌ Error in AI analysis: {e}")

async def combined_repository_analysis(session, repo_name):
    """Combined file reading and AI analysis"""
    
    print(f"\n🔄 Combined Analysis for {repo_name}")
    print("Reading files and performing AI analysis...")
    
    # First read files
    print("\n📂 Step 1: Reading repository files...")
    try:
        files_result = await session.call_tool("read_github_repo_files", {
            "repo_name": repo_name,
            "file_types": "py,js,ts,java,md,txt,json",
            "max_files": 30
        })
        
        files_data = None
        for content in files_result.content:
            if hasattr(content, 'text'):
                try:
                    files_data = json.loads(content.text)
                    break
                except json.JSONDecodeError:
                    continue
        
        if files_data and "error" not in files_data:
            files = files_data.get("files", [])
            summary = files_data.get("summary", {})
            
            print(f"✅ Found {len(files)} files")
            print("File types:", ", ".join(summary.get('files_by_type', {}).keys()))
            
            # Then perform AI analysis
            print("\n🤖 Step 2: AI Analysis...")
            await analyze_repository_with_ai(session, repo_name, "comprehensive")
            
            # Provide file access option
            print(f"\n📋 Step 3: Quick File Access")
            readme_files = [f for f in files if f['type'] == 'README']
            if readme_files:
                print("📚 README files found:")
                for readme in readme_files:
                    print(f"  📄 {readme['path']}")
                
                show_readme = input("Show README content? (y/N): ").strip().lower()
                if show_readme in ['y', 'yes']:
                    for readme in readme_files:
                        print(f"\n📖 {readme['path']}:")
                        print("-" * 50)
                        print(readme['content'][:2000] + "..." if len(readme['content']) > 2000 else readme['content'])
                        print("-" * 50)
        else:
            print("❌ Failed to read repository files")
    
    except Exception as e:
        print(f"❌ Error in combined analysis: {e}")

async def list_google_docs_interactive(session):
    """Interactive Google Docs listing to find resume"""
    
    print("\n📄 Google Docs Finder")
    print("=" * 40)
    
    search_term = input("Search term (default: 'resume'): ").strip()
    if not search_term:
        search_term = "resume"
    
    try:
        result = await session.call_tool("list_google_docs", {"search_term": search_term})
        
        for content in result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if "error" in data:
                            print(f"❌ Error: {data['error']}")
                            return
                        
                        documents = data.get("documents", [])
                        count = data.get("count", 0)
                        
                        if not documents:
                            print(f"📭 No Google Docs found with search term '{search_term}'")
                            return
                        
                        print(f"\n📄 Found {count} Google Docs documents:")
                        print("=" * 60)
                        
                        for i, doc in enumerate(documents, 1):
                            print(f"{i:2d}. {doc.get('name')}")
                            print(f"    📅 Modified: {doc.get('modified', 'Unknown')[:10]}")
                            print(f"    👤 Owners: {', '.join(doc.get('owners', ['Unknown']))}")
                            print(f"    🌐 Link: {doc.get('link')}")
                            print(f"    🆔 ID: {doc.get('id')}")
                            print()
                        
                        # Ask if user wants to copy a document ID
                        copy_choice = input("Copy document ID for use? (enter number or press Enter to skip): ").strip()
                        if copy_choice:
                            try:
                                doc_index = int(copy_choice) - 1
                                if 0 <= doc_index < len(documents):
                                    selected_doc = documents[doc_index]
                                    print(f"\n📋 Document ID copied: {selected_doc.get('id')}")
                                    print(f"Document Name: {selected_doc.get('name')}")
                                    print("You can use this ID to add content to the document.")
                                else:
                                    print("❌ Invalid document number")
                            except ValueError:
                                print("❌ Invalid input")
                        
                        break
                except json.JSONDecodeError:
                    print(f"❌ Could not parse response")
    
    except Exception as e:
        print(f"❌ Error listing Google Docs: {e}")

async def analyze_and_add_to_resume(session):
    """Complete workflow: analyze repository and add to resume"""
    
    print("\n🎯 Repository Analysis + Resume Update")
    print("=" * 50)
    
    # Step 1: Get repository name
    repo_name = input("Enter repository name (owner/repo): ").strip()
    if not repo_name or '/' not in repo_name:
        print("❌ Please enter repository in format 'owner/repo'")
        return
    
    # Step 2: Choose analysis type
    print("\n🤖 AI Analysis Options:")
    print("1. Comprehensive analysis")
    print("2. README & documentation only")
    print("3. Code analysis only")
    print("4. Project structure analysis")
    
    analysis_choice = input("Select analysis type (1-4, default: 1): ").strip()
    analysis_types = {"1": "comprehensive", "2": "readme_only", "3": "code_only", "4": "structure"}
    analysis_type = analysis_types.get(analysis_choice, "comprehensive")
    
    # Step 3: Choose resume focus
    print("\n🎯 Resume Focus:")
    print("1. Technical skills & technologies")
    print("2. Leadership & collaboration")
    print("3. Impact & achievements")
    print("4. Learning & growth")
    
    focus_choice = input("Select resume focus (1-4, default: 1): ").strip()
    focus_types = {"1": "technical", "2": "leadership", "3": "impact", "4": "learning"}
    focus_area = focus_types.get(focus_choice, "technical")
    
    print(f"\n🔍 Step 1: Analyzing {repo_name} ({analysis_type} analysis)...")
    
    try:
        # Perform AI analysis
        analysis_result = await session.call_tool("analyze_github_repo_with_ai", {
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "max_files_to_analyze": 25
        })
        
        ai_analysis_text = ""
        for content in analysis_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict) and "error" not in data:
                        ai_analysis_text = data.get("ai_analysis", "")
                        print("✅ AI analysis completed")
                        break
                    elif "error" in data:
                        print(f"❌ Analysis error: {data['error']}")
                        return
                except json.JSONDecodeError:
                    continue
        
        if not ai_analysis_text:
            print("❌ Failed to get AI analysis")
            return
        
        print(f"\n📝 Step 2: Creating resume summary (focus: {focus_area})...")
        
        # Generate resume summary
        summary_result = await session.call_tool("summarize_repo_analysis_for_resume", {
            "repo_name": repo_name,
            "analysis_text": ai_analysis_text,
            "focus_area": focus_area
        })
        
        resume_summary = ""
        bullet_points = []
        
        for content in summary_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict) and "error" not in data:
                        resume_summary = data.get("formatted_summary", "")
                        bullet_points = data.get("bullet_points", [])
                        print("✅ Resume summary generated")
                        break
                    elif "error" in data:
                        print(f"❌ Summary error: {data['error']}")
                        return
                except json.JSONDecodeError:
                    continue
        
        if not resume_summary:
            print("❌ Failed to generate resume summary")
            return
        
        # Display the generated summary
        print(f"\n📋 Generated Resume Summary:")
        print("=" * 50)
        print(resume_summary)
        print("=" * 50)
        
        # Ask if user wants to add to Google Doc
        add_to_doc = input("\n📄 Add to Google Docs resume? (Y/n): ").strip().lower()
        if add_to_doc in ['n', 'no']:
            print("✅ Summary generated successfully (not added to document)")
            return
        
        print("\n📄 Step 3: Finding your resume document...")
        
        # List Google Docs to find resume
        docs_result = await session.call_tool("list_google_docs", {"search_term": "resume"})
        
        documents = []
        for content in docs_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict) and "error" not in data:
                        documents = data.get("documents", [])
                        break
                except json.JSONDecodeError:
                    continue
        
        if not documents:
            print("📭 No resume documents found. Please create one first or enter document ID manually.")
            doc_id = input("Enter Google Docs document ID manually (or press Enter to skip): ").strip()
            if not doc_id:
                print("📋 Summary ready to copy manually:")
                print(resume_summary)
                return
        else:
            print(f"📄 Found {len(documents)} resume documents:")
            for i, doc in enumerate(documents, 1):
                print(f"{i:2d}. {doc.get('name')}")
                print(f"    🆔 ID: {doc.get('id')}")
            
            # Select document
            doc_choice = input(f"Select document (1-{len(documents)}) or enter custom ID: ").strip()
            
            try:
                if doc_choice.isdigit() and 1 <= int(doc_choice) <= len(documents):
                    selected_doc = documents[int(doc_choice) - 1]
                    doc_id = selected_doc.get('id')
                    doc_name = selected_doc.get('name')
                else:
                    doc_id = doc_choice
                    doc_name = "Custom Document"
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return
        
        print(f"\n📝 Step 4: Adding content to document...")
        
        # Add to Google Doc
        section_title = f"GitHub Repository Analysis - {repo_name}"
        add_result = await session.call_tool("add_to_google_doc", {
            "doc_id": doc_id,
            "content": resume_summary,
            "section_title": section_title
        })
        
        for content in add_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if data.get("success"):
                            doc_info = data.get("document_info", {})
                            print("🎉 Successfully added to your resume!")
                            print("=" * 50)
                            print(f"📄 Document: {doc_info.get('title', 'Unknown')}")
                            print(f"🌐 Link: {doc_info.get('web_view_link')}")
                            print(f"📝 Section: {section_title}")
                            print("\n📋 Added content:")
                            print(resume_summary)
                        elif "error" in data:
                            print(f"❌ Error adding to document: {data['error']}")
                            print("📋 Summary ready to copy manually:")
                            print(resume_summary)
                        break
                except json.JSONDecodeError:
                    continue
    
    except Exception as e:
        print(f"❌ Error in analysis workflow: {e}")

async def create_resume_summary_for_repo(session, repo_name):
    """Create resume summary for a specific repository from the exploration interface"""
    
    print(f"\n🎯 Creating Resume Summary for {repo_name}")
    print("=" * 60)
    
    # Choose analysis type
    print("\n🤖 Analysis Type:")
    print("1. Comprehensive analysis")
    print("2. README & documentation only")
    print("3. Code analysis only")
    print("4. Project structure analysis")
    
    analysis_choice = input("Select analysis type (1-4, default: 1): ").strip()
    analysis_types = {"1": "comprehensive", "2": "readme_only", "3": "code_only", "4": "structure"}
    analysis_type = analysis_types.get(analysis_choice, "comprehensive")
    
    # Choose resume focus
    print("\n🎯 Resume Focus:")
    print("1. Technical skills & technologies")
    print("2. Leadership & collaboration")
    print("3. Impact & achievements")
    print("4. Learning & growth")
    
    focus_choice = input("Select resume focus (1-4, default: 1): ").strip()
    focus_types = {"1": "technical", "2": "leadership", "3": "impact", "4": "learning"}
    focus_area = focus_types.get(focus_choice, "technical")
    
    try:
        # Perform analysis and create resume summary
        print(f"\n🔍 Analyzing {repo_name}...")
        
        # Get AI analysis
        analysis_result = await session.call_tool("analyze_github_repo_with_ai", {
            "repo_name": repo_name,
            "analysis_type": analysis_type,
            "max_files_to_analyze": 20
        })
        
        ai_analysis_text = ""
        for content in analysis_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict) and "error" not in data:
                        ai_analysis_text = data.get("ai_analysis", "")
                        break
                    elif "error" in data:
                        print(f"❌ Analysis error: {data['error']}")
                        return
                except json.JSONDecodeError:
                    continue
        
        if not ai_analysis_text:
            print("❌ Failed to get AI analysis")
            return
        
        print(f"📝 Creating resume summary...")
        
        # Generate resume summary
        summary_result = await session.call_tool("summarize_repo_analysis_for_resume", {
            "repo_name": repo_name,
            "analysis_text": ai_analysis_text,
            "focus_area": focus_area
        })
        
        resume_summary = ""
        for content in summary_result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict) and "error" not in data:
                        resume_summary = data.get("formatted_summary", "")
                        break
                    elif "error" in data:
                        print(f"❌ Summary error: {data['error']}")
                        return
                except json.JSONDecodeError:
                    continue
        
        if not resume_summary:
            print("❌ Failed to generate resume summary")
            return
        
        # Display the summary
        print(f"\n📋 Generated Resume Summary:")
        print("=" * 60)
        print(resume_summary)
        print("=" * 60)
        
        # Ask about adding to Google Docs
        add_choice = input("\n📄 Add to Google Docs? (Y/n): ").strip().lower()
        if add_choice not in ['n', 'no']:
            # Find resume document
            docs_result = await session.call_tool("list_google_docs", {"search_term": "resume"})
            
            documents = []
            for content in docs_result.content:
                if hasattr(content, 'text'):
                    try:
                        data = json.loads(content.text)
                        if isinstance(data, dict) and "error" not in data:
                            documents = data.get("documents", [])
                            break
                    except json.JSONDecodeError:
                        continue
            
            if documents:
                print(f"\n📄 Found resume documents:")
                for i, doc in enumerate(documents, 1):
                    print(f"{i:2d}. {doc.get('name')}")
                
                doc_choice = input(f"Select document (1-{len(documents)}): ").strip()
                try:
                    doc_index = int(doc_choice) - 1
                    if 0 <= doc_index < len(documents):
                        selected_doc = documents[doc_index]
                        doc_id = selected_doc.get('id')
                        
                        # Add to document
                        section_title = f"GitHub Repository Analysis - {repo_name}"
                        add_result = await session.call_tool("add_to_google_doc", {
                            "doc_id": doc_id,
                            "content": resume_summary,
                            "section_title": section_title
                        })
                        
                        for content in add_result.content:
                            if hasattr(content, 'text'):
                                try:
                                    data = json.loads(content.text)
                                    if isinstance(data, dict) and data.get("success"):
                                        print("🎉 Successfully added to your resume!")
                                        break
                                except json.JSONDecodeError:
                                    continue
                    else:
                        print("❌ Invalid document selection")
                except ValueError:
                    print("❌ Invalid input")
            else:
                print("📭 No resume documents found")
                print("📋 Summary ready to copy manually:")
                print(resume_summary)
        else:
            print("✅ Resume summary generated (not added to document)")
    
    except Exception as e:
        print(f"❌ Error creating resume summary: {e}")

async def test_read_github_repo_files(session):
    """Test the read_github_repo_files tool with interactive options"""
    
    print("\n📂 GitHub Repository File Reader")
    print("=" * 50)
    
    # Get repository name
    print("Enter repository details:")
    repo_name = input("Repository name (format: owner/repo, e.g., 'microsoft/vscode'): ").strip()
    
    if not repo_name:
        print("❌ Repository name is required")
        return
    
    if '/' not in repo_name:
        print("❌ Repository name must be in format 'owner/repo'")
        return
    
    # Get file types
    print("\nFile type options:")
    print("1. Default (Python, JS, TS, Java, Markdown, Text)")
    print("2. Python only (.py)")
    print("3. JavaScript/TypeScript (.js, .ts)")
    print("4. Java (.java)")
    print("5. Documentation (.md, .txt, .rst)")
    print("6. Custom (specify your own)")
    
    type_choice = input("Select file types (1-6, default: 1): ").strip()
    
    file_types_map = {
        "1": "py,js,ts,java,md,txt",
        "2": "py",
        "3": "js,ts",
        "4": "java",
        "5": "md,txt,rst",
    }
    
    if type_choice == "6":
        file_types = input("Enter file extensions (comma-separated, e.g., 'py,js,cpp'): ").strip()
        if not file_types:
            file_types = "py,js,ts,java,md,txt"
    else:
        file_types = file_types_map.get(type_choice, "py,js,ts,java,md,txt")
    
    # Get max files
    max_files_input = input("Maximum number of files to read (1-200, default: 50): ").strip()
    try:
        max_files = int(max_files_input) if max_files_input else 50
        if max_files < 1 or max_files > 200:
            max_files = 50
    except ValueError:
        max_files = 50
    
    print(f"\n🔍 Reading files from {repo_name}")
    print(f"📁 File types: {file_types}")
    print(f"📊 Max files: {max_files}")
    print("\nThis may take a moment for large repositories...")
    
    try:
        result = await session.call_tool("read_github_repo_files", {
            "repo_name": repo_name,
            "file_types": file_types,
            "max_files": max_files
        })
        
        for content in result.content:
            if hasattr(content, 'text'):
                try:
                    data = json.loads(content.text)
                    if isinstance(data, dict):
                        if "error" in data:
                            print(f"❌ Error: {data['error']}")
                            return
                        
                        repository = data.get("repository", {})
                        summary = data.get("summary", {})
                        files = data.get("files", [])
                        files_by_type = data.get("files_by_type", {})
                        
                        # Display repository information
                        print(f"\n📁 Repository: {repository.get('full_name')}")
                        print(f"📝 Description: {repository.get('description', 'No description')}")
                        print(f"🌐 URL: {repository.get('url')}")
                        print(f"💻 Primary Language: {repository.get('language', 'N/A')}")
                        print(f"⭐ Stars: {repository.get('stars', 0)} | 🍴 Forks: {repository.get('forks', 0)}")
                        print(f"🔒 Private: {repository.get('private', False)}")
                        
                        # Display summary
                        print(f"\n📊 File Summary:")
                        print(f"   Total files found: {summary.get('total_files_found', 0)}")
                        print(f"   Search depth: {summary.get('search_depth', 'N/A')}")
                        print("   Files by type:")
                        for file_type, count in summary.get('files_by_type', {}).items():
                            print(f"     {file_type}: {count} files")
                        
                        if not files:
                            print("\n📭 No files found matching the specified criteria.")
                            return
                        
                        # Ask user what they want to do with the files
                        print(f"\n🔧 Options for {len(files)} files:")
                        print("1. Show file list only")
                        print("2. Show specific file content")
                        print("3. Show all README files")
                        print("4. Show files by type")
                        print("5. Save all files to local directory")
                        
                        action = input("Select action (1-5): ").strip()
                        
                        if action == "1":
                            print(f"\n📄 File List ({len(files)} files):")
                            print("=" * 80)
                            for i, file_info in enumerate(files, 1):
                                print(f"{i:2d}. {file_info['path']} ({file_info['type']}) - {file_info['size']} bytes")
                        
                        elif action == "2":
                            print(f"\n📄 Available files:")
                            for i, file_info in enumerate(files, 1):
                                print(f"{i:2d}. {file_info['path']} ({file_info['type']})")
                            
                            try:
                                file_choice = int(input(f"Select file number (1-{len(files)}): ").strip())
                                if 1 <= file_choice <= len(files):
                                    selected_file = files[file_choice - 1]
                                    print(f"\n📖 Content of {selected_file['path']}:")
                                    print("=" * 80)
                                    print(selected_file['content'])
                                    print("=" * 80)
                                    print(f"File URL: {selected_file['url']}")
                                else:
                                    print("❌ Invalid file number")
                            except ValueError:
                                print("❌ Invalid input")
                        
                        elif action == "3":
                            readme_files = [f for f in files if f['type'] == 'README']
                            if readme_files:
                                print(f"\n📚 README Files ({len(readme_files)}):")
                                print("=" * 80)
                                for readme in readme_files:
                                    print(f"\n📖 {readme['path']}:")
                                    print("-" * 60)
                                    print(readme['content'])
                                    print("-" * 60)
                            else:
                                print("\n📭 No README files found")
                        
                        elif action == "4":
                            print(f"\n📁 Files organized by type:")
                            for file_type, type_files in files_by_type.items():
                                print(f"\n{file_type} Files ({len(type_files)}):")
                                print("-" * 40)
                                for file_info in type_files:
                                    print(f"  📄 {file_info['path']} ({file_info['size']} bytes)")
                            
                            # Ask if user wants to see content of a specific type
                            type_choice = input(f"\nShow content for which type? ({', '.join(files_by_type.keys())}) or 'none': ").strip()
                            if type_choice in files_by_type:
                                type_files = files_by_type[type_choice]
                                print(f"\n📖 Content of all {type_choice} files:")
                                print("=" * 80)
                                for file_info in type_files:
                                    print(f"\n--- {file_info['path']} ---")
                                    print(file_info['content'])
                                    print()
                        
                        elif action == "5":
                            save_dir = input("Enter directory name to save files (default: 'downloaded_repo'): ").strip()
                            if not save_dir:
                                save_dir = "downloaded_repo"
                            
                            print(f"\n💾 Saving {len(files)} files to '{save_dir}' directory...")
                            
                            import os
                            # Create directory if it doesn't exist
                            os.makedirs(save_dir, exist_ok=True)
                            
                            saved_count = 0
                            for file_info in files:
                                try:
                                    # Create subdirectories if needed
                                    file_path = os.path.join(save_dir, file_info['path'])
                                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                                    
                                    # Write file content
                                    with open(file_path, 'w', encoding='utf-8') as f:
                                        f.write(file_info['content'])
                                    saved_count += 1
                                    print(f"✅ Saved: {file_info['path']}")
                                except Exception as e:
                                    print(f"❌ Failed to save {file_info['path']}: {e}")
                            
                            print(f"\n🎉 Successfully saved {saved_count}/{len(files)} files to '{save_dir}'")
                        
                        break
                except json.JSONDecodeError:
                    print(f"❌ Could not parse response: {content.text}")
    
    except Exception as e:
        print(f"❌ Error reading repository files: {e}")

async def interactive_github_uploader(session):
    """Interactive tool to select and upload Colab notebooks to GitHub"""
    
    print("\n🚀 Interactive Colab to GitHub Uploader")
    print("=" * 60)
    
    # Get all Colab files
    print("📁 Fetching your Colab notebooks...")
    try:
        files_result = await session.call_tool("list_colab_files", {"folder_id": None})
        
        files = []
        for content in files_result.content:
            if isinstance(content, list):
                for file in content:
                    clean_file = {
                        'id': file['id'].strip(),
                        'name': file['name'].strip(),
                        'link': file['link'].strip()
                    }
                    files.append(clean_file)
            elif hasattr(content, 'text'):
                try:
                    files_data = json.loads(content.text)
                    if isinstance(files_data, list):
                        for file in files_data:
                            clean_file = {
                                'id': file['id'].strip(),
                                'name': file['name'].strip(),
                                'link': file['link'].strip()
                            }
                            files.append(clean_file)
                    elif isinstance(files_data, dict) and all(key in files_data for key in ['id', 'name', 'link']):
                        clean_file = {
                            'id': files_data['id'].strip(),
                            'name': files_data['name'].strip(),
                            'link': files_data['link'].strip()
                        }
                        files.append(clean_file)
                except json.JSONDecodeError:
                    pass
        
        if not files:
            print("❌ No Colab notebooks found in your Google Drive")
            return
        
        # Display numbered list of files
        print(f"\n📋 Found {len(files)} Colab notebooks:")
        print("-" * 80)
        for i, file in enumerate(files, 1):
            print(f"{i:2d}. {file['name']}")
            print(f"    ID: {file['id']}")
            print(f"    Link: {file['link']}")
            print()
        
        # Get user selection
        while True:
            try:
                selection = input(f"Select a notebook (1-{len(files)}) or 'q' to quit: ").strip()
                
                if selection.lower() == 'q':
                    return
                
                file_index = int(selection) - 1
                if 0 <= file_index < len(files):
                    selected_file = files[file_index]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(files)}")
            except ValueError:
                print("❌ Please enter a valid number or 'q' to quit")
        
        print(f"\n🎯 Selected: {selected_file['name']}")
        print(f"📄 File ID: {selected_file['id']}")
        
        # Ask if user wants to preview the notebook
        preview = input("\n📖 Would you like to preview the notebook content? (y/N): ").strip().lower()
        if preview in ['y', 'yes', '1']:
            print("\n📋 Reading notebook content...")
            try:
                read_result = await session.call_tool("read_colab_notebook", {"file_id": selected_file['id']})
                
                for content in read_result.content:
                    if hasattr(content, 'text'):
                        try:
                            data = json.loads(content.text)
                            if isinstance(data, dict) and "metadata" in data:
                                metadata = data.get("metadata", {})
                                cells = data.get("cells", [])
                                print(f"📊 Notebook Info:")
                                print(f"   Name: {metadata.get('name', 'Unknown')}")
                                print(f"   Cells: {metadata.get('cell_count', 0)}")
                                print(f"   Code cells: {len([c for c in cells if c.get('cell_type') == 'code'])}")
                                print(f"   Markdown cells: {len([c for c in cells if c.get('cell_type') == 'markdown'])}")
                                break
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"⚠️  Could not read notebook: {e}")
        
        # Ask if user wants to generate README preview
        readme_preview = input("\n📝 Would you like to preview the AI-generated README? (y/N): ").strip().lower()
        if readme_preview in ['y', 'yes', '1']:
            print("\n🤖 Generating README with AI...")
            try:
                readme_result = await session.call_tool("generate_readme", {
                    "file_id": selected_file['id'],
                    "file_name": selected_file['name']
                })
                
                for content in readme_result.content:
                    if hasattr(content, 'text'):
                        try:
                            data = json.loads(content.text)
                            if isinstance(data, dict) and "readme" in data:
                                readme_text = data["readme"]
                                print("\n" + "="*80)
                                print("📄 GENERATED README PREVIEW:")
                                print("="*80)
                                # Show first 500 characters
                                if len(readme_text) > 500:
                                    print(readme_text[:500] + "\n...\n[Content truncated for preview]")
                                else:
                                    print(readme_text)
                                print("="*80)
                                break
                        except json.JSONDecodeError:
                            pass
            except Exception as e:
                print(f"⚠️  Could not generate README: {e}")
        
        # GitHub repository creation
        print("\n🐙 GitHub Repository Creation")
        print("-" * 40)
        
        # Generate default repository name
        base_name = selected_file['name'].replace('.ipynb', '').replace(' ', '-').lower()
        safe_name = ''.join(c for c in base_name if c.isalnum() or c in '-_')
        
        # Get repository details
        repo_name = input(f"Repository name (default: {safe_name}): ").strip() or safe_name
        repo_description = input("Repository description (optional): ").strip()
        
        # Ask about privacy
        is_private_input = input("Make repository private? (y/N): ").strip().lower()
        is_private = is_private_input in ['y', 'yes', '1']
        
        # Confirmation
        print(f"\n🔧 Repository Configuration:")
        print(f"   Name: {repo_name}")
        print(f"   Description: {repo_description or 'None'}")
        print(f"   Private: {is_private}")
        print(f"   Source file: {selected_file['name']}")
        
        confirm = input("\n🚀 Create GitHub repository? (Y/n): ").strip().lower()
        if confirm in ['n', 'no', '0']:
            print("❌ Repository creation cancelled")
            return
        
        # Create the repository
        print("\n🚀 Creating GitHub repository...")
        try:
            github_result = await session.call_tool("create_github_repo", {
                "file_id": selected_file['id'],
                "file_name": selected_file['name'],
                "repo_name": repo_name,
                "repo_description": repo_description,
                "is_private": is_private
            })
            
            # Process the result
            for content in github_result.content:
                if hasattr(content, 'text'):
                    try:
                        data = json.loads(content.text)
                        if isinstance(data, dict):
                            if "success" in data and data["success"]:
                                print("\n🎉 Repository created successfully!")
                                print("=" * 60)
                                
                                repo_info = data.get("repository", {})
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
                                
                            elif "error" in data:
                                print(f"\n❌ Error: {data['error']}")
                            else:
                                print(f"\n🤔 Unexpected response: {data}")
                        break
                    except json.JSONDecodeError:
                        print(f"❌ Could not parse response: {content.text}")
        
        except Exception as e:
            print(f"❌ Error creating repository: {e}")
        
    except Exception as e:
        print(f"❌ Error fetching files: {e}")

async def main_menu():
    """Main menu for testing MCP tools"""
    
    print("🔧 MCP Server Test Client")
    print("=" * 40)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python", 
        args=["mcp_server.py"]
    )
    
    # Connect to the MCP server
    logger.info("Connecting to MCP server...")
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            # Create a client session
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the session
                await session.initialize()
                
                # Test server connectivity
                print("📡 Testing server connectivity...")
                try:
                    ping_result = await session.call_tool("ping", {})
                    print("✅ Server is online and responsive")
                except Exception as e:
                    print(f"❌ Server connectivity failed: {e}")
                    return
                
                while True:
                    print("\n" + "="*50)
                    print("🔧 MCP Server Tools Menu")
                    print("="*50)
                    print("1. 🚀 Upload Colab notebook to GitHub")
                    print("2. 📋 List your GitHub repositories")
                    print("3. 📂 Read files from GitHub repository")
                    print("4. 🤖 AI Analysis of GitHub repository")
                    print("5. 📄 List Google Docs (find resume)")
                    print("6. 🎯 Analyze repo + Add to resume")
                    print("7. 📁 List Colab notebooks")
                    print("8. 📖 Read specific Colab notebook")
                    print("9. 📝 Generate README for notebook")
                    print("10. 🏓 Test server ping")
                    print("11. ❌ Exit")
                    
                    choice = input("\nSelect an option (1-11): ").strip()
                    
                    if choice == "1":
                        await interactive_github_uploader(session)
                    elif choice == "2":
                        await test_list_github_repos(session)
                    elif choice == "3":
                        await test_read_github_repo_files(session)
                    elif choice == "4":
                        repo_name = input("Enter repository name (owner/repo): ").strip()
                        if repo_name and '/' in repo_name:
                            print("\n🤖 AI Analysis Options:")
                            print("1. Comprehensive analysis")
                            print("2. README & documentation only")
                            print("3. Code analysis only")
                            print("4. Project structure analysis")
                            
                            analysis_choice = input("Select analysis type (1-4, default: 1): ").strip()
                            analysis_types = {"1": "comprehensive", "2": "readme_only", "3": "code_only", "4": "structure"}
                            analysis_type = analysis_types.get(analysis_choice, "comprehensive")
                            
                            await analyze_repository_with_ai(session, repo_name, analysis_type)
                        else:
                            print("❌ Please enter repository in format 'owner/repo'")
                    elif choice == "5":
                        await list_google_docs_interactive(session)
                    elif choice == "6":
                        await analyze_and_add_to_resume(session)
                    elif choice == "7":
                        print("\n📁 Listing Colab notebooks...")
                        try:
                            files_result = await session.call_tool("list_colab_files", {"folder_id": None})
                            for content in files_result.content:
                                if hasattr(content, 'text'):
                                    try:
                                        files = json.loads(content.text)
                                        if isinstance(files, list):
                                            print(f"Found {len(files)} Colab notebooks:")
                                            for i, file in enumerate(files, 1):
                                                print(f"{i:2d}. {file.get('name', 'N/A')}")
                                        break
                                    except json.JSONDecodeError:
                                        pass
                        except Exception as e:
                            print(f"❌ Error: {e}")
                    elif choice == "8":
                        file_id = input("Enter notebook file ID: ").strip()
                        if file_id:
                            try:
                                read_result = await session.call_tool("read_colab_notebook", {"file_id": file_id})
                                for content in read_result.content:
                                    if hasattr(content, 'text'):
                                        try:
                                            data = json.loads(content.text)
                                            if "metadata" in data:
                                                metadata = data["metadata"]
                                                print(f"📊 Notebook: {metadata.get('name', 'Unknown')}")
                                                print(f"📝 Cells: {metadata.get('cell_count', 0)}")
                                            break
                                        except json.JSONDecodeError:
                                            pass
                            except Exception as e:
                                print(f"❌ Error: {e}")
                    elif choice == "9":
                        file_id = input("Enter notebook file ID: ").strip()
                        file_name = input("Enter notebook file name: ").strip()
                        if file_id and file_name:
                            try:
                                readme_result = await session.call_tool("generate_readme", {
                                    "file_id": file_id,
                                    "file_name": file_name
                                })
                                for content in readme_result.content:
                                    if hasattr(content, 'text'):
                                        try:
                                            data = json.loads(content.text)
                                            if "readme" in data:
                                                print("\n" + "="*60)
                                                print("📄 GENERATED README:")
                                                print("="*60)
                                                print(data["readme"])
                                                print("="*60)
                                            break
                                        except json.JSONDecodeError:
                                            pass
                            except Exception as e:
                                print(f"❌ Error: {e}")
                    elif choice == "10":
                        try:
                            ping_result = await session.call_tool("ping", {})
                            print("🏓 Pong! Server is responsive.")
                        except Exception as e:
                            print(f"❌ Ping failed: {e}")
                    elif choice == "11":
                        print("👋 Goodbye!")
                        return
                    else:
                        print("❌ Invalid choice. Please select 1-11.")
                    
                    input("\nPress Enter to continue...")
                    
    except Exception as e:
        logger.error(f"Client error: {e}")
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    print("⚠️  Prerequisites:")
    print("  1. GITHUB_TOKEN configured in .env")
    print("  2. Google Drive API credentials set up")
    print("  3. At least one Colab notebook in your Drive")
    print()
    
    asyncio.run(main_menu())