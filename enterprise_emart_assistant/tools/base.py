from functools import singledispatchmethod
from types import FunctionType, MethodType
from langchain.tools import BaseTool


class ToolContainer:
    tools: dict[str, BaseTool]

    def __init__(self):
        self.tools = {}

    @singledispatchmethod
    def register(self, tool):
        pass

    @register.register
    def register_tool(self, tool: BaseTool):
        self.tools[tool.name] = tool

    @register.register
    def register_list(self, tools: list):
        for tool in tools:
            if isinstance(tool, BaseTool):
                self.tools[tool.name] = tool

    def get_tools(self, *tools: str|BaseTool) -> list[BaseTool]:
        tools_list = []
        for tool in tools:
            if isinstance(tool, str):
                tools_list.append(self.tools[tool])
            elif isinstance(tool, BaseTool):
                tools_list.append(self.tools[tool.name])
            else:
                raise ValueError("Invalid tool type")
        return tools_list
