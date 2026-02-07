from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config()
    print("✗ .env file NOT found, using environment variables")


PINE_CONE_API_KEY = config("...")
PINECONE_INDEX = config("...")

GEMINI_API_KEY = config("GEMINI_API_KEY", cast=Secret)
