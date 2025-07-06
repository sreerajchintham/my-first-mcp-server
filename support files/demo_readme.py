#!/usr/bin/env python3
"""
Demo script to showcase the enhanced README generation capabilities
"""

import asyncio
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from mcp.client.session import ClientSession

async def demo_readme_generation():
    """Demo the enhanced README generation with and without Gemini API"""
    
    print("🚀 Enhanced README Generation Demo")
    print("="*50)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python", 
        args=["mcp_server.py"]
    )
    
    try:
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                
                # Get the first Colab file
                files_result = await session.call_tool("list_colab_files", {"folder_id": None})
                
                if files_result.content:
                    # Parse the first file
                    first_file = None
                    for content in files_result.content:
                        if hasattr(content, 'text'):
                            import json
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
                    
                    if first_file:
                        print(f"📝 Generating README for: {first_file['name']}")
                        print(f"🔗 Colab Link: {first_file['link']}")
                        print("-" * 50)
                        
                        # Generate README
                        result = await session.call_tool(
                            "generate_readme", 
                            {"file_id": first_file["id"], "file_name": first_file["name"]}
                        )
                        
                        # Display the result
                        for content in result.content:
                            if hasattr(content, 'text'):
                                try:
                                    readme_data = json.loads(content.text)
                                    if isinstance(readme_data, dict) and "readme" in readme_data:
                                        print("📄 Generated README:")
                                        print("=" * 50)
                                        print(readme_data["readme"])
                                        print("=" * 50)
                                        
                                        # Show features
                                        print("\n✨ Enhanced Features:")
                                        print("• AI-powered content analysis (with Gemini API)")
                                        print("• Automatic library detection")
                                        print("• Professional formatting")
                                        print("• Comprehensive structure analysis")
                                        print("• Usage instructions")
                                        print("• Fallback mode for reliability")
                                        
                                        return
                                except:
                                    continue
                        
                        print("❌ Could not parse README response")
                    else:
                        print("❌ No Colab files found")
                else:
                    print("❌ No files returned from server")
                    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(demo_readme_generation()) 