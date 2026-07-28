import asyncio
import json
import re  # 保留，可能其他地方用到，但推理部分不再使用
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
            "messages": [{"role": "user", "content": request.question}],
            "state": "employee",
            "role": "employee",
            "user_id": "user1",
            "answer": "",
        }
        async for chunk in main_graph.astream(state, config):
            for node_name, node_data in chunk.items():
                if node_data and isinstance(node_data, dict):
                    # --- 处理推理（完整内容一次性发送，不拆分） ---
                    if "messages" in node_data:
                        for message in node_data.get("messages"):
                            if isinstance(message, AIMessage):
                                reasoning_text = message.additional_kwargs.get(
                                    "reasoning_content"
                                )
                                if reasoning_text:
                                    # 直接发送完整的推理内容作为一个步骤
                                    yield ai_pb2.ChatResponse(
                                        message=reasoning_text,
                                        event="reasoning",
                                        is_end=True,  # 表示这个推理步骤完整
                                    )
                                    # 可以加一点延迟让前端有时间渲染
                                    await asyncio.sleep(0.02)

                    # --- 处理答案（逐字符发送，最后一块标记结束） ---
                    if "answer" in node_data and node_data.get("answer") != "":
                        answer_text = node_data.get("answer")
                        chunk_size = 2
                        total_len = len(answer_text)
                        for i in range(0, total_len, chunk_size):
                            chunk = answer_text[i : i + chunk_size]
                            is_last = i + chunk_size >= total_len
                            yield ai_pb2.ChatResponse(
                                message=chunk, event="answer", is_end=is_last
                            )
                            await asyncio.sleep(0.02)

        # 发送结束标志
        yield ai_pb2.ChatResponse(message="", event="end", is_end=True)


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
