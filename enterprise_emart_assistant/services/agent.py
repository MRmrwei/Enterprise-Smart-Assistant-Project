import asyncio
import json
import re
from graphs.main_graph import main_graph
from services.sse import SSEContent


class AgentService:

    async def Chat(
        self, question: str, state: dict | None = None, config: dict | None = None
    ):
        round_num = 0
        async for model, data in main_graph.astream(
            state, config, stream_mode=["custom", "updates"]
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
            # elif model == "updates":

            #     # print(data)

            #     if "init_node" in data:
            #         pass
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
