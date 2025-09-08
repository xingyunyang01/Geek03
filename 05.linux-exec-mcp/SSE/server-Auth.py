import subprocess
from mcp.server.fastmcp import FastMCP
import uvicorn
from fastapi.responses import JSONResponse

# Stateless server (no session persistence)
mcp = FastMCP("StatelessServer", stateless_http=False)

# Add an get score tool
@mcp.tool()
def linux_exec_cmd(cmd: str) -> str:
    """执行linux命令"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True).stdout

if __name__ == "__main__":
    app = mcp.sse_app()
    
    # 添加认证中间件到所有路由
    @app.middleware("http")
    async def auth_middleware(request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            if auth_header.split(" ")[1] == "123456":
                return await call_next(request)
            else:
                return JSONResponse(content={"error": "Invalid token"}, status_code=401)
        return await call_next(request)
    
    uvicorn.run(app, host="0.0.0.0", port=8000,
                ssl_keyfile="/etc/letsencrypt/live/www.xyymcp.top/privkey.pem",
                ssl_certfile="/etc/letsencrypt/live/www.xyymcp.top/fullchain.pem")