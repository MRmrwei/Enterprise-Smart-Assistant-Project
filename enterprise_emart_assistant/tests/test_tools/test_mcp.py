import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient

from tools.base import tools_container


def test_mcp():
    client = MultiServerMCPClient(
        {
            "mcp": {
                "url": "http://localhost:8888/mcp",
                "transport": "streamable_http",
            }
        }
    )
    tools = asyncio.run(client.get_tools())
    tools_container.register(tools)
    tool = tools_container.get_tools("employee_info")
    print(f"Tools: {tool}")
