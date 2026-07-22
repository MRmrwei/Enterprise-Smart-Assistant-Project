from langchain.tools import BaseTool

from llms.factory import get_default_llm
from services.knowledge import upload_knowledge
from tools.base import tools_container
from tools.forms import leave_request, leave_tools, form_all_tools, form_skills
from langchain_skills_adapters import SkillsTool
from tools.knowledges import skills
from db.vector import vector_store


def www():
    print("www")


def main():
    res = vector_store.similarity_search("腾讯", k=3, filter={"chunk_index": 1})
    print(res)
    # upload_knowledge("./data/1.txt", id="1")


if __name__ == "__main__":
    main()
