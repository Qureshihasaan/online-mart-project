from starlette.config import Config
from starlette.datastructures import Secret


try: 
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    print("✗ .env file NOT found, using empty config")
    

PRODUCT_SERVICE_DATABASE_URL = config("PRODUCT_SERVICE_DATABASE_URL", cast=Secret)
KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)

# AI Services

GEMINI_API_KEY = config("GEMINI_API_KEY", cast=Secret)
PINECONE_API_KEY = config("PINECONE_API_KEY", cast=Secret)
PINECONE_INDEX_NAME = config("PINECONE_INDEX_NAME", cast=str, default="online-mart-products")


print(f"DATABASE_URL loaded: {str(PRODUCT_SERVICE_DATABASE_URL)[:50]}...")  # Print first 50 chars
print(f"BOOTSTRAP_SERVER: {KAFKA_BOOTSTRAP_SERVER}")