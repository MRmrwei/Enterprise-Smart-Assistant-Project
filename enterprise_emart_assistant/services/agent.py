import asyncio
import json
import re
from graphs.main_graph import main_graph
from services.sse import SSEContent
from langgraph.types import Command
from db.caches.client import cache


class AgentService:

    async def Chat(
        self, question: str, state: dict | None = None, config: dict | None = None
    ):
        thread_id = config.get("configurable", {}).get("thread_id")
        interrupt = cache.get(f"{thread_id}:interrupts", None)
        if interrupt is not None:
            print("进入    interrupts")
            cache.delete(f"{thread_id}:interrupts")
            """
            交互流程
            """
            round_num = 0
            async for namespace, model, data in main_graph.astream(
                Command(resume=question),
                config=config,
                stream_mode=["custom", "updates"],
                subgraphs=True,
            ):
                if model == "custom":
                    content = data.get("content")
                    type = data.get("type")
                    print(f"content {content}")

                    async for char in self.intelligentStreamer(content, type):
                        if type == "reasoning":
                            char["index"] = round_num
                        yield SSEContent(char)

                    if type == "reasoning":
                        round_num += 1

            current_state = await main_graph.aget_state(config)
            if current_state.interrupts:
                interrupt = current_state.interrupts[0]
                cache.set(f"{thread_id}:interrupts", interrupt.id)
                async for char in self.intelligentStreamer(interrupt.value, "answer"):
                    yield SSEContent(char)

        else:
            round_num = 0
            async for namespace, model, data in main_graph.astream(
                state, config, stream_mode=["custom", "updates"], subgraphs=True
            ):
                if model == "custom":
                    content = data.get("content")
                    type = data.get("type")
                    print(f"content {content}")

                    async for char in self.intelligentStreamer(content, type):
                        if type == "reasoning":
                            char["index"] = round_num
                        yield SSEContent(char)

                    if type == "reasoning":
                        round_num += 1

            current_state = await main_graph.aget_state(config)
            if current_state.interrupts:
                interrupt = current_state.interrupts[0]
                cache.set(f"{thread_id}:interrupts", interrupt.id)
                async for char in self.intelligentStreamer(interrupt.value, "answer"):
                    yield SSEContent(char)

        yield SSEContent("{}", "end")

    async def intelligentStreamer(self, full_text: str, type: str):
        """
        智能流式输出器：
        - 标点符号处自动停顿稍长（模拟呼吸）
        - 短句快速连发，长句适度拆分
        """
        segments = re.split(r"([，。！？；：、\n])", full_text)

        buffer = ""
        for seg in segments:
            buffer += seg
            if seg in ["。", "！", "？", "\n"]:
                yield {"content": buffer, "type": type}
                buffer = ""
                await asyncio.sleep(0.3)
            elif seg in ["，", "；", "："]:
                pass
            else:
                # 普通文字，积累到一定长度再发
                if len(buffer) >= 3:  # 改为 3 个字发送一次
                    yield {"content": buffer, "type": type}
                    buffer = ""
                    await asyncio.sleep(0.06)

        if buffer:
            yield {"content": buffer, "type": type}
