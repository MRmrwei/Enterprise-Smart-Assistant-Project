import asyncio

from enums.roles import Role
from graphs.main_graph import main_graph
from graphs.state import AgentState
from langgraph.types import interrupt, Command


async def main():

    config = {"configurable": {"thread_id": "user1"}}
    is_interrupt = False
    while True:
        print("\n👋 欢迎使用深度 seek ！")
        q = input("问题: ")

        if q in ["exit", "quit", "e", "q"]:
            print("\n👋 用户中断，程序退出")
            break

        if q == "":
            continue
        state = {"question": q}

        if is_interrupt:
            state = Command(resume=state.get("question"))
            is_interrupt = False

        print("正在思考...")

        result = await main_graph.ainvoke(
            state,
            config,
        )

        if result.get("__interrupt__", None):
            interrupt_data = result["__interrupt__"][0].value
            print(f"{interrupt_data}")
            is_interrupt = True

        answer = result["answer"]
        if not result["answer"]:
            print(f"🤖 助手回复: {answer}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户中断，程序退出")
