import asyncio

import langchain_mcp_adapters
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import MCPToolCallRequest

from tools.base import tools_container


# 定义拦截器 - 必须返回修改后的 request
async def auth_interceptor(request: MCPToolCallRequest, call_args):
    """
    认证拦截器 - 在工具调用前添加认证头，然后执行真正的调用
    """
    print(f"🔐 拦截器: 处理工具 '{request.name}'")
    
    # 1. 确保 headers 存在
    if request.headers is None:
        request.headers = {}
    
    # 2. 添加认证头
    request.headers["Authorization"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTcyMjE5OTEsImlhdCI6MTc4NTY4NTk5MSwibmFtZSI6IuiAgeadvyIsInVpZCI6MX0.FFki-dFYvnCYHmhWwjNzLViFSQOFYXq8kj4_LPDirpY"
    # request.headers["X-User-Id"] = "test_user"
    
    print(f"✅ 已添加认证头: {request.headers}")
    
    # 3. ⚠️ 关键：调用 call_args 执行真正的工具调用
    # call_args 是真正执行工具的函数
    result = await call_args(request)
    # 4. 返回执行结果
    return result

def test_mcp():
    # print(f"版本: {langchain_mcp_adapters.__version__}")
    client = MultiServerMCPClient(
        {
            "mcp": {
                "url": "http://localhost:8888/mcp",
                "transport": "streamable_http",
            }
        },
        tool_interceptors=[auth_interceptor],  # 注册拦截器
    )
    tools = asyncio.run(client.get_tools())

    tool = tools[0]
    result = asyncio.run(tool.ainvoke({}))

    # tools_container.register(tools)
    # tool = tools_container.get_tools("employee_info")

    print(f"result: {result}")
