import asyncio
import random
import re
import string
from collections.abc import AsyncIterable

from graphs.main_graph import main_graph
from pydantics.sse import SSEContent
from langgraph.types import Command
from db.caches.client import cache


class AgentService:
    """智能助手核心服务：管理对话流式输出、人机交互中断恢复、会话 ID 生成。"""

    # ── 流式输出节奏参数（类常量，方便统一调优） ──
    _CHUNK_SIZE = 3          # 普通文字每 N 个字切一片
    _PAUSE_SHORT = 0.06      # 片间短停顿（秒），模拟逐字键入
    _PAUSE_LONG = 0.3        # 句末长停顿（秒），模拟呼吸节奏

    # ─────────────────────────────────────────────────────────────
    #  公开接口
    # ─────────────────────────────────────────────────────────────

    async def Chat(
        self, state: dict | None = None, config: dict | None = None
    ) -> AsyncIterable[SSEContent]:
        """
        处理一轮对话的主入口。

        工作流程（两段式）：
        1. 流式输出 Agent 的思考 / 回答内容（custom 事件）
        2. 若 Agent 需要用户交互（interrupt），则流式输出中断提示

        Args:
            state: 用户输入，新对话时形如 {"question": "..."}
            config: LangGraph 配置，需含 {"configurable": {"thread_id": ...}}

        Yields:
            SSEContent: 服务端推送事件，前端逐条消费
        """
        thread_id = config.get("configurable", {}).get("thread_id")

        # ── 0. 判断是「恢复中断」还是「全新对话」 ──
        interrupt = cache.get(f"{thread_id}:interrupts", None)
        if interrupt is not None:
            print("进入    interrupts")
            cache.delete(f"{thread_id}:interrupts")
            # 恢复：把用户本次回复作为 resume 值注入
            stream_input = Command(resume=state.get("question"))
        else:
            # 新对话：直接把用户输入传给主图
            stream_input = state

        # reasoning_index 给每个思考块编号，前端据此区分不同的思维链段落
        reasoning_index = 0

        # ── 阶段 1：流式输出 Agent 内容 ──
        async for namespace, model, data in main_graph.astream(
            stream_input,
            config=config,
            stream_mode=["custom", "updates"],
            subgraphs=True,
        ):
            if model == "custom":
                content = data.get("content")
                content_type = data.get("type")
                print(f"content {content}")

                async for char in self._intelligent_stream(content, content_type):
                    # 为 reasoning 块打上索引
                    if content_type == "reasoning":
                        char["index"] = reasoning_index
                    yield SSEContent(data=char)

                # 一个 reasoning 块结束 → 索引递增
                if content_type == "reasoning":
                    reasoning_index += 1

        # ── 阶段 2：检测并处理中断（人机交互） ──
        current_state = await main_graph.aget_state(config)
        if current_state.interrupts:
            interrupt = current_state.interrupts[0]
            # 缓存中断 ID，下次用户回复时恢复执行
            cache.set(f"{thread_id}:interrupts", interrupt.id)
            # 将中断提示文本流式推送给前端
            async for char in self._intelligent_stream(interrupt.value, "answer"):
                yield SSEContent(data=char)

        # 本轮结束信号
        yield SSEContent(event="end")

    # ─────────────────────────────────────────────────────────────
    #  内部方法
    # ─────────────────────────────────────────────────────────────

    async def _intelligent_stream(self, full_text: str, content_type: str):
        """
        智能流式输出器。

        按语义边界切分文本，模拟人类打字节奏逐段推送：

        ┌──────────────┬──────────────────────────────────────────┐
        │ 字符类型      │ 行为                                     │
        ├──────────────┼──────────────────────────────────────────┤
        │ 。！？ / 换行 │ 吐出缓冲 → 长停顿 0.3s（模拟呼吸）        │
        │ ，；：        │ 留在缓冲，不单独停顿                       │
        │ 、           │ 视为普通文字，随文字片段一起输出             │
        │ 普通文字      │ 每 3 个字切一片 → 短停顿 0.06s（模拟逐字） │
        └──────────────┴──────────────────────────────────────────┘

        Args:
            full_text: 待流式输出的完整文本
            content_type: 内容类型标签，如 "reasoning" / "answer"

        Yields:
            dict: {"content": "文本片段", "type": content_type}
        """
        # 按中文标点切分 — 分组 (...) 让分隔符也保留在列表中
        segments = re.split(r"([，。！？；：、\n])", full_text)

        buffer = ""
        for seg in segments:
            if not seg:
                continue

            buffer += seg

            # ① 句末标点 / 换行 → 整段输出 + 长停顿
            if seg in ("。", "！", "？", "\n"):
                yield {"content": buffer, "type": content_type}
                buffer = ""
                await asyncio.sleep(self._PAUSE_LONG)

            # ② 句中分隔符 → 静默累积，不触发输出
            elif seg in ("，", "；", "："):
                pass

            # ③ 普通文字（含顿号） → 达到阈值就切一片
            else:
                if len(buffer) >= self._CHUNK_SIZE:
                    yield {"content": buffer, "type": content_type}
                    buffer = ""
                    await asyncio.sleep(self._PAUSE_SHORT)

        # 兜底：吐出缓冲中剩余的文本
        if buffer:
            yield {"content": buffer, "type": content_type}

    # ─────────────────────────────────────────────────────────────
    #  工具方法
    # ─────────────────────────────────────────────────────────────

    @staticmethod
    def get_thread_id(uid: int) -> str:
        """
        生成唯一的会话线程 ID。

        格式：{12 位随机字母数字}_{用户 ID}
        随机部分使用 62 字符空间（a-z, A-Z, 0-9），碰撞概率极低。

        Args:
            uid: 用户 ID

        Returns:
            str: 线程唯一标识
        """
        chars = string.ascii_letters + string.digits
        random_part = "".join(random.choice(chars) for _ in range(12))
        return f"{random_part}_{uid}"
