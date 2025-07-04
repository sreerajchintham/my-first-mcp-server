from mcp import StdioServer, Tool
import asyncio

async def ping():
    return {"status": "pong"}

tools = [
    Tool(name="ping", func=ping, description="Test server connectivity")
]

async def main():
    server = StdioServer(tools=tools, command="python", args=["mcp_server.py"])
    async with server:
        await server.run()

if __name__ == "__main__":
    asyncio.run(main())