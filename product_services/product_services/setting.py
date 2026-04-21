from starlette.config import Config
from starlette.datastructures import Secret
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    config = Config(".env")
    logger.info("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    logger.warning("✗ .env file NOT found, using environment variables from system")

# Load environment variables with defaults for local development
PRODUCT_SERVICE_DATABASE_URL = config("PRODUCT_SERVICE_DATABASE_URL", cast=Secret)


KAFKA_BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER")


KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config(
    "KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str
)


GEMINI_API_KEY = config("GEMINI_API_KEY", cast=Secret)


PINECONE_API_KEY = config("PINECONE_API_KEY", cast=Secret)

PINECONE_INDEX_NAME = config("PINECONE_INDEX_NAME", cast=str)

# Security settings
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHMS = config("ALGORITHMS", cast=str)
