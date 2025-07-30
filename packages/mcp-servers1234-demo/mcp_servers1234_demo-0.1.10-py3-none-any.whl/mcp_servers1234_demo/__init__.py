import httpx
# 用于创建 MCP 服务
from mcp.server.fastmcp import FastMCP
# 初始化一个MCP服务实例，服务名称就是test_mcp_server，这将作为 MCP 客户端或大模型识别服务的标识
mcp = FastMCP("test_mcp_server")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 获取当前本地 ip 地址
@mcp.tool()
async def fetch_current_ip() -> str:
    """fetch current ip"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://ipinfo.io/ip")
        return response.text
    

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()