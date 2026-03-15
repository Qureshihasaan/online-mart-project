from starlette.config import Config
from starlette.datastructures import Secret
import logging

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
PRODUCT_SERVICE_DATABASE_URL = config("PRODUCT_SERVICE_DATABASE_URL", cast=Secret, default="postgresql://user:password@localhost:5432/products_db")
KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str, default="localhost:9092")
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str, default="product-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str, default="product-group")

# Optional AI Services
try:
    GEMINI_API_KEY = config("GEMINI_API_KEY", cast=Secret)
except:
    GEMINI_API_KEY = None
    logger.warning("GEMINI_API_KEY not found, AI features may be disabled")

try:
    PINECONE_API_KEY = config("PINECONE_API_KEY", cast=Secret)
except:
    PINECONE_API_KEY = None
    logger.warning("PINECONE_API_KEY not found, Pinecone features may be disabled")

PINECONE_INDEX_NAME = config("PINECONE_INDEX_NAME", cast=str, default="online-mart-products")

# Security settings
SECRET_KEY = config("SECRET_KEY", cast=str, default="dev-secret-key-change-in-production")
ALGORITHMS = config("ALGORITHMS", cast=str, default="HS256")

logger.info(f"DATABASE_URL loaded: {str(PRODUCT_SERVICE_DATABASE_URL)[:50]}...")  # Print first 50 chars
logger.info(f"BOOTSTRAP_SERVER: {KAFKA_BOOTSTRAP_SERVER}")