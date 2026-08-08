from datetime import datetime

from enums.intentions import Intentions

from agents.list import agents


def get_intention_system_prompt() -> str:

    intentions = "\n".join(
        [f"- {agent.get_key()}: {agent.get_description()}" for agent in agents]
    )

    return f"""
        你是一位意图分析专家。请根据用户输入判断其意图，并输出JSON格式的分析结果。
        ## 背景信息：
            - 今天日期：{datetime.now().strftime("%Y-%m-%d")}
        ## 可选的意图类型：{intentions}
        ## file_path字段的注意事项：
            - 如果用户输入中没有文件路径和意图不是"{Intentions.KNOWLEDGE_INGEST.value}"请填""。
            - 如果有路径必须要自动转成正斜杠
            
        ## 输出格式（严格JSON）：
            {{
                "type": "意图类型的key",
                "description": "意图描述",
                "vital_content": "总结出人物，目的，时间等重要的信息"
                "file_path": 文件路径。
            }}

        ## 注意：
            - 不要输出任何JSON以外的内容
    """
