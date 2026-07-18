from langchain_core.tools import tool
from langchain_skills_adapters import SkillsTool

form_skills = SkillsTool(skills_path="./skills/form/")
@tool
def leave_request(
    response: str, leave_type: str, start_date: str, end_date: str, day_num: float
) -> str:
    """
    员工假期申请单

    日期格式要求：
    - 必须使用 "YYYY-MM-DD" 格式，例如 "2026-07-18"
    - 如果用户说"明天"，请使用今天+1天的日期
    - 如果用户说"后天"，请使用今天+2天的日期

    请假天数要求：
    -根据 start_date 和 end_date 自动计算：
    - 同一天请假：0.5 天（半天）或 1 天（全天）
    - 跨天请假：(end_date - start_date) + 1，即包含首尾两天
    - 例如：2026-07-18 到 2026-07-19 = 2 天
    - 例如：2026-07-18 到 2026-07-18 = 1 天（或 0.5 天，根据用户描述判断）

    Args:
        response (str): 请假原因，可根据意图描述和用户原话润色后填写，必填。
        leave_type (str): 请假类型,根据用户提供的意图描述和用户原话自动帮填，必填。可选值：
            - "annual"  = 年假
            - "sick"    = 病假
            - "personal"= 事假
            注意：调用工具时必须使用英文值（annual/sick/personal），但向用户展示时用中文。
        start_date (str): 开始日期，必填。格式必须为 "YYYY-MM-DD"，且不能早于今天。
        end_date (str): 结束日期，必填。格式必须为 "YYYY-MM-DD"，且必须 >= start_date。
        day_num (float): 请假天数，必填。最少0.5天并且不能超过 30 天。
    """
    if day_num < 0.5 or day_num > 30:
        return "请假天数不符合要求"

    return "申请成功"
