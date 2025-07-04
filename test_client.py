from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters, load_mcp_tools
from aiohttp import ClientSession
import asyncio
import json

async def test_mcp_server():
    server_params = StdioServerParameters(command="python", args=["mcp_server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read=read, write=write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            print("Available tools:", [tool["name"] for tool in tools])
            result = await session.call_tool("ping", {})
            print("Ping result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_mcp_server())