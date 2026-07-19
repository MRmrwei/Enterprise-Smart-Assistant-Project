from langchain_core.tools import tool
from langchain_skills_adapters import SkillsTool


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

@tool
def cancel_request(response: str):
    """
    填单过程中用户表达取消的意图，请使用该工具
    Args:
        response (str): 用户取消的原因,根据用户表达填写。如果用户没填请自行根据实际原因填写，必填。
    """

    return f"申请中断，原因：{response}"

@tool
def reimbursement_request(
    expense_type: str, expense_amount: float, expense_date: str, expense_reason: str
):
    """
    员工报销申请单
    
    Args:
        expense_type (str): 报销类型，必填。可选值：
            - "meal"  = 餐饮
            - "travel"= 差旅
            - "other" = 其他
        expense_amount (float): 报销金额，必填。
        expense_date (str): 报销日期，必填。格式必须为 "YYYY-MM-DD"
        expense_reason (str): 报销原因，根据用户意图描述和用户原话填写，必填。

    """

    if expense_amount < 0 or expense_amount > 1000:
        return "申请金额不符合要求，报销失败！"

    return "报销申请成功，等待审批！"


leave_skills = SkillsTool(skills_path="./skills/form/")

# leave_skills.verbose = True
form_skills = [leave_skills]
leave_tools = [leave_request]
reimbursement_tools = [reimbursement_request]
form_all_tools = leave_tools + [cancel_request] + reimbursement_tools
