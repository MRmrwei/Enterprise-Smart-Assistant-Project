import asyncio
import json
import re
from graphs.main_graph import main_graph
from services.sse import SSEContent


class AgentService:

    async def Chat(
        self, question: str, state: dict | None = None, config: dict | None = None
    ):

        async for model, data in main_graph.astream(
            state, config, stream_mode=["custom", "updates"]
        ):
            if model == "custom":
                content = data.get("content")
                type = data.get("type")

                yield SSEContent(json.dumps({"is_end": False}), type)
                async for char in self.intelligentStreamer(content):
                    yield SSEContent(char)
                yield SSEContent(json.dumps({"is_end": True}), type)

            # elif model == "updates":

            #     # print(data)

            #     if "init_node" in data:
            #         pass
        yield SSEContent("{}", "end")

    async def intelligentStreamer(self, full_text: str):
        """
        智能流式输出器：
        - 标点符号处自动停顿稍长（模拟呼吸）
        - 短句快速连发，长句适度拆分
        """
        # 第一步：按标点切成"意群"（语义块）
        # 保留标点符号作为分隔符
        segments = re.split(r"([，。！？；：、\n])", full_text)

        buffer = ""  # 累积缓冲区
        for seg in segments:
            buffer += seg
            # 如果遇到句号/问号/感叹号/换行，说明一个完整语义块结束，立即发送
            if seg in ["。", "！", "？", "\n"]:
                yield json.dumps({"content": buffer})
                buffer = ""  # 清空
                await asyncio.sleep(0.3)  # 句末停顿 300ms，模拟换气
            elif seg in ["，", "；", "："]:
                # 逗号等只积累，不立即发送（等凑够一小句再发）
                pass
            else:
                # 普通文字，积累到一定长度再发
                if len(buffer) >= 5:  # 每 3 个字发一次
                    yield json.dumps({"content": buffer})
                    buffer = ""
                    await asyncio.sleep(0.06)  # 正常速度 60ms

        # 最后把残余的 buffer 发掉
        if buffer:
            yield json.dumps({"content": buffer})
