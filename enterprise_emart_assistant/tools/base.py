from functools import singledispatchmethod
from typing import List
from langchain.tools import BaseTool
from langgraph.prebuilt import tools_condition

from tools.forms import form_all_tools_skills
from tools.qa import qa_query


class ToolContainer:
    tools: dict[str, BaseTool]

    def __init__(self):
        self.tools = {}
        self._init_register()

    def _init_register(self):
        self.register(
            form_all_tools_skills + [qa_query]
        )

    @singledispatchmethod
    def register(self, tool):
        pass

    @register.register
    def _register_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    @register.register
    def _register_list(self, tools: list):
        for tool in tools:
            if isinstance(tool, BaseTool):
                self.tools[tool.name] = tool

    @singledispatchmethod
    def get_tools(self, tools) -> list[BaseTool]:
        pass

    @get_tools.register
    def _get_tools_list(self, tool_list: list):

        tools = []
        for tool in tool_list:
            if isinstance(tool, BaseTool):
                if tool.name in self.tools:
                    tools.append(self.tools[tool.name])
            elif isinstance(tool, str) and tool in self.tools:
                tools.append(self.tools[tool])

        return tools

    @get_tools.register
    def _get_tools_str(self, *tools: str | BaseTool):
        tools_list = []
        for tool in tools:
            if isinstance(tool, str) and tool in self.tools:
                tools_list.append(self.tools[tool])
            elif isinstance(tool, BaseTool) and tool.name in self.tools:
                tools_list.append(self.tools[tool.name])
            else:
                raise ValueError(f"Invalid tool type {tool}")
        return tools_list


tools_container = ToolContainer()
