from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
import stamina
from tools.base import tools_container
from core.context import context
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import MCPToolCallRequest
from configs.config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")

    try:
        await init_mcp_tools()
    except Exception as e:
        # 处理其他异常
        raise Exception(f"MCP 启动失败: {e}")

    init_routes(app)

    yield

    print("Shutting down")


def init_routes(app: FastAPI):
    from app.controllers import chat
    app.include_router(chat.router)


@stamina.retry(attempts=3, on=Exception)
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
        ctx = context.get()
        if ctx is None:
            raise Exception("用户未登录，无法调用工具！")
        else:
            token = ctx.token

        # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MTcyMjE5OTEsImlhdCI6MTc4NTY4NTk5MSwibmFtZSI6IuiAgeadvyIsInVpZCI6MX0.FFki-dFYvnCYHmhWwjNzLViFSQOFYXq8kj4_LPDirpY"
        # 3. 添加认证头
        request.headers["Authorization"] = token

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

    try:
        tools = await client.get_tools()
        tools_container.register(tools)
    except Exception as e:
        # 处理其他异常
        raise Exception(f"MCP 服务器连接失败: {e}")
