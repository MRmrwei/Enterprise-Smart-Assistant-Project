from os import getenv
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        pass
    def get(seff, key: str | None, default: any = None) -> any:
        return getenv(key, default)
    
config = Config()