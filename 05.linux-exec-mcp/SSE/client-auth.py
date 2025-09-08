import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
import sys

async def connect_to_sse_server(server_url: str):
    """Connect to an MCP server running with SSE transport"""
    # Store the context managers so they stay alive
    async with sse_client(url=server_url,headers={"Authorization": f"Bearer 123456"}) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # List available tools
            tools = await session.list_tools()
            print("Tools:", tools)

            # call a tool
            result = await session.call_tool(name="linux_exec_cmd",arguments={"cmd": "ls -l"})

            print("result: ", result)

async def main():
    if len(sys.argv) < 2:
        print("Usage: uv run client.py <URL of SSE MCP server (i.e. http://localhost:8000/sse)>")
        sys.exit(1)
    
    await connect_to_sse_server(server_url=sys.argv[1])

if __name__ == "__main__":
    asyncio.run(main())