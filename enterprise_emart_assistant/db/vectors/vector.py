from langchain_chroma import Chroma
from langchain_core.stores import V
from langchain_ollama import OllamaEmbeddings
from configs.config import config, ROOT_DIR

VECTOR_STORE = None


def create_vector_store():
    dir = str(ROOT_DIR / config.get("PERSIST_DIR"))
    return Chroma(
        persist_directory=dir,
        embedding_function=OllamaEmbeddings(
            model=config.get("EMBEDDING_MODEL"),
        ),
    )


def get_vector_store():
    global VVECTOR_STORE
    if VECTOR_STORE is None:
        VECTOR_STORE = create_vector_store()
    return VECTOR_STORE
