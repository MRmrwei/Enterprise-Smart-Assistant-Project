import asyncio

from enums.roles import Role
from graphs.main_graph import main_graph
from graphs.state import AgentState
from langgraph.types import interrupt, Command


async def main():

    config = {"configurable": {"thread_id": "user1"}}
    while True:
        print("\n👋 欢迎使用深度 seek ！")
        q = input("问题: ")
        # q = r"帮我上传文档到知识库，文档路径为：C:\Users\宝🐖\Desktop\向量数据库11.doc"
        # q = "我感冒了帮我请假"
        # q = "公司周六日休息吗"
        # q = "我们公司经营什么业务"

        if q in ["exit", "quit", "e", "q"]:
            print("\n👋 用户中断，程序退出")
            break

        if q == "":
            continue

        print("正在思考...")
        result = await main_graph.ainvoke(
            {
                "messages": [
                    {"role": "user", "content": q},
                ],
                "state": "employee",
                "role": "employee",
                "user_id": "user1",
                "answer": "",
            },
            config,
        )

        while "__interrupt__" in result:
            interrupt_data = result["__interrupt__"][0].value
            print(f"{interrupt_data}")
            q = input("请输入你的答案：")
            result = await main_graph.ainvoke(Command(resume=q), config)

        answer = result["answer"]
        print(f"🤖 助手回复: {answer}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户中断，程序退出")
