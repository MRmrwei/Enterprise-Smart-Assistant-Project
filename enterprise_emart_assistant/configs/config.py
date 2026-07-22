from os import getenv
from dotenv import load_dotenv
from pathlib import Path


ROOT_DIR = Path(__file__).parent.parent.parent

class Config:
    def __init__(self):
        load_dotenv()
        pass
    def get(seff, key: str | None, default: any = None) -> any:
        return getenv(key, default)
    
config = Config()