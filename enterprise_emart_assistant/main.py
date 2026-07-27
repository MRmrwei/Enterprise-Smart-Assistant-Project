# main.py
import asyncio
import json
import grpc.aio
from langchain.messages import AIMessage
import ai_pb2
import ai_pb2_grpc
from graphs.main_graph import main_graph


class RpcServicer(ai_pb2_grpc.aiServicer):
    """
    实现 rpc 服务中定义的 Chat 方法（服务端流式）
    """

    async def Chat(self, request, context: grpc.aio.ServicerContext):
        config = {"configurable": {"thread_id": "user1"}}
        state = {
            "messages": [
                {"role": "user", "content": request.question},
            ],
            "state": "employee",
            "role": "employee",
            "user_id": "user1",
            "answer": "",
        }
        async for chunk in main_graph.astream(state, config):
            for node_name, node_data in chunk.items():
                if node_data and isinstance(node_data, dict):

                    if "messages" in node_data:
                        for message in node_data.get("messages"):
                            if isinstance(message, AIMessage):
                                yield ai_pb2.ChatResponse(
                                    message=message.additional_kwargs.get(
                                        "reasoning_content"
                                    ),
                                    event="reasoning",
                                )

                    if "answer" in node_data and node_data.get("answer") != "":
                        yield ai_pb2.ChatResponse(
                            message=node_data.get("answer"), event="answer"
        #                 )
        # 发送结束标志
        yield ai_pb2.ChatResponse(message="", event="end")


async def serve():
   try:
        """启动 gRPC 异步服务器"""
        server = grpc.aio.server()
        ai_pb2_grpc.add_aiServicer_to_server(RpcServicer(), server)
        server.add_insecure_port("[::]:50051")
        await server.start()
        print("🚀 服务已启动，监听 50051 ...")
        await server.wait_for_termination()
   except Exception as e:
        print(e)


def main():
    """主入口函数"""
    asyncio.run(serve())


if __name__ == "__main__":
    main()
