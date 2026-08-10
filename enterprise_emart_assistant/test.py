import asyncio
from langchain.messages import HumanMessage
from core.boot import init_mcp_tools
from graphs.main_graph import build_graph
from agents.form.agent import FormDataAgent
from langgraph.types import Command


def get_main_graph():
    return build_graph()


async def main():
    await init_mcp_tools()
    config = {"configurable": {"thread_id": "1"}}
    agent = get_main_graph()
    try:

        q = input("问题: ")
        # q = "调取我的员工信息"
        q = "你好"
        state = {"question": q}
        print("正在思考...")

        async for model, data in agent.astream(state, config, stream_mode=["custom"]):
            if model == "custom":
                print(data)
    except Exception as e:
        import traceback

        print(f"错误信息: {e}")
        print(f"完整堆栈:\n{traceback.format_exc()}")


if __name__ == "__main__":

    asyncio.run(main())
