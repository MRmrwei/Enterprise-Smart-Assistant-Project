import asyncio

import stamina

from llms.factory import get_default_llm

def test_retry():
    llm = get_default_llm()
    try:
        for attempt in stamina.retry_context(on=Exception, attempts=3):
                with attempt:
                    print(f"attempt = {attempt}")
                    res = asyncio.run(llm.ainvoke({"hello"}))
                    print(res)
    except Exception as e:
        print(f"AI 决策 JSON 解析失败（已重试 {attempt.num} 次）: {e}")
