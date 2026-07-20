from functools import singledispatchmethod
from langchain.tools import BaseTool
from langgraph.prebuilt import tools_condition

from tools.forms import form_all_tools_skills


class ToolContainer:
    tools: dict[str, BaseTool]

    def __init__(self):
        self.tools = {}
        self._init_register()

    def _init_register(self):
        self.register(form_all_tools_skills)

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
    def _get_tools_list(self, tools: list):
        return [
            self.tools[tool.name]
            for tool in tools
            if tool.name in self.tools and isinstance(tool, BaseTool)
        ]

    @get_tools.register
    def _get_tools_str(self, *tools: str | BaseTool):
        print(2222)
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
