from starlette.config import config
from starlette.datastructures import Secret


try: 
    config = Config(".env")
except FileNotFoundError:
    config = Config()


PINE_CONE_API_KEY= config()
PINECONE_INDEX = config()

GEMINI_API_KEY = config("GEMINI_API_KEY", cast=Secret)