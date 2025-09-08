import subprocess
from mcp.server.fastmcp import FastMCP
import uvicorn

# Stateless server (no session persistence)
mcp = FastMCP("StatelessServer", stateless_http=False)

# Add an get score tool
@mcp.tool()
def linux_exec_cmd(cmd: str) -> str:
    """执行linux命令"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout


# Run server with streamable_http transport
#mcp.run(transport="streamable-http")
app = mcp.streamable_http_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)