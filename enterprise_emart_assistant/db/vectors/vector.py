
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from configs.config import config, ROOT_DIR


def get_vector_store():
    dir = str(ROOT_DIR / config.get("PERSIST_DIR"))
    return Chroma(
        persist_directory=dir,
        embedding_function=OllamaEmbeddings(
            model=config.get("EMBEDDING_MODEL"),
        ),
    )

vector_store = get_vector_store()