from langchain.tools import BaseTool

from llms.factory import get_default_llm
from tools.base import tools_container
from tools.forms import leave_request, leave_tools, form_all_tools, form_skills
from langchain_skills_adapters import SkillsTool
from tools.knowledges import skills

def www():
    print("www")


def main():


   
    
    print(f"{form_skills}\n\n\n\n\n {skills}")
    


if __name__ == "__main__":
    main()
