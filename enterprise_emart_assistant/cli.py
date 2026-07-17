import asyncio

from graphs.main_graph import main_graph
from graphs.state import AgentState


async def main():

    config = {"configurable": {"thread_id": "user1"}}

    while True:
        q = input("问题: ")

        if q in ["exit", "quit", "e", "q"]:
            print("\n👋 用户中断，程序退出")
            break

        print("正在思考...")
        async for chunk in main_graph.astream(
            {
                "messages": [
                    {"role": "user", "content": q},
                ],
                "state": "employee",
                "user_id": "user1",
            },
            config,
        ):
            messages = chunk.get("messages", [])
            if messages:
                last_msg = messages[-1]
                # 如果 last_msg 是 BaseMessage 对象，有 content 属性
                print("chunk: ", last_msg.content, "\n")
            else:
                # 如果没有消息，可能打印其他状态字段
                print("chunk: ", chunk)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户中断，程序退出")
