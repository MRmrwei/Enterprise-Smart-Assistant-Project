import asyncio
import grpc.aio
from langchain.messages import AIMessage
import ai_pb2_grpc
from graphs.main_graph import main_graph
from rpc.agents import AgentRpc
from services.agent import AgentService


async def serve():
    server = grpc.aio.server()
    ai_pb2_grpc.add_aiServicer_to_server(AgentRpc(AgentService()), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    print("🚀 服务已启动，监听 50051 ...")
    await server.wait_for_termination()
   


def main():

    # asyncio.run(AgentService().Chat("你好"))

    # return
    """主入口函数"""
    asyncio.run(serve())


if __name__ == "__main__":
    try:
        """启动 gRPC 异步服务器"""
        main()
    except Exception as e:
        print(f"❌ 启动服务时发生错误：{e}")
    except (KeyboardInterrupt, EOFError):
        print("\n👋 用户中断，程序退出")
