from langchain.tools import BaseTool

from llms.factory import get_default_llm
from tools.base import tools_container
from tools.forms import leave_request, leave_tools, form_all_tools, form_skills


def www():
    print("www")


def main():


    # llm = get_default_llm().bind_tools([tools.get_tool("leave_request")], strict=True)

    # res = llm.invoke("你现在有什么工具")
    tools_container.register(form_all_tools + form_skills)
    print(len(tools_container.get_tools(form_all_tools + form_skills)))


if __name__ == "__main__":
    main()
