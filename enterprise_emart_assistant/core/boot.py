from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from tools.base import tools_container
from langchain_mcp_adapters.client import MultiServerMCPClient
from core.context import context
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import MCPToolCallRequest
from configs.config import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    await init_mcp_tools()
    
    init_routes(app)
    
    yield

    print("Shutting down")


def init_routes(app: FastAPI):
    from routes import chat
    app.include_router(chat.router)



async def init_mcp_tools():

    async def auth_interceptor(request: MCPToolCallRequest, call_args):
        """
        认证拦截器 - 在工具调用前添加认证头，然后执行真正的调用
        """
        print(f"🔐 拦截器: 处理工具 '{request.name}'")

        # 1. 确保 headers 存在
        if request.headers is None:
            request.headers = {}

        # 2. 添加认证头
        request.headers["Authorization"] = (
            context.get().token if context.get().token else ""
        )
        # request.headers["X-User-Id"] = "test_user"

        print(f"✅ 已添加认证头: {request.headers}")

        # 3. ⚠️ 关键：调用 call_args 执行真正的工具调用
        # call_args 是真正执行工具的函数
        result = await call_args(request)
        # 4. 返回执行结果
        return result
    mcp_url = config.get("MCP_ADDR")
    client = MultiServerMCPClient(
        {
            "mcp": {
                "url": mcp_url,
                "transport": "streamable_http",
            }
        },
        tool_interceptors=[auth_interceptor],  # 注册拦截器
    )
    tools = await client.get_tools()
    tools_container.register(tools)
    
