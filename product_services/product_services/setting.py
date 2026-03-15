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

# Load environment variables with validation
try:
    PRODUCT_SERVICE_DATABASE_URL = config("PRODUCT_SERVICE_DATABASE_URL", cast=Secret)
    if not PRODUCT_SERVICE_DATABASE_URL:
        raise ValueError("PRODUCT_SERVICE_DATABASE_URL is required")
except Exception as e:
    logger.error(f"Missing or invalid PRODUCT_SERVICE_DATABASE_URL: {e}")
    raise

try:
    KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)
    if not KAFKA_BOOTSTRAP_SERVER:
        raise ValueError("KAFKA_BOOTSTRAP_SERVER is required")
except Exception as e:
    logger.error(f"Missing or invalid KAFKA_BOOTSTRAP_SERVER: {e}")
    raise

try:
    KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
    if not KAFKA_PRODUCT_TOPIC:
        raise ValueError("KAFKA_PRODUCT_TOPIC is required")
except Exception as e:
    logger.error(f"Missing or invalid KAFKA_PRODUCT_TOPIC: {e}")
    raise

try:
    KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)
    if not KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT:
        raise ValueError("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT is required")
except Exception as e:
    logger.error(f"Missing or invalid KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT: {e}")
    raise

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
try:
    SECRET_KEY = config("SECRET_KEY", cast=str)
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is required")
except Exception as e:
    logger.error(f"Missing or invalid SECRET_KEY: {e}")
    raise

try:
    ALGORITHMS = config("ALGORITHMS", cast=str)
    if not ALGORITHMS:
        raise ValueError("ALGORITHMS is required")
except Exception as e:
    logger.error(f"Missing or invalid ALGORITHMS: {e}")
    raise

# Additional Kafka configuration for Azure Event Hubs (if provided)
try:
    KAFKA_SASL_MECHANISM = config("KAFKA_SASL_MECHANISM", cast=str, default="")
except:
    KAFKA_SASL_MECHANISM = ""

try:
    KAFKA_SECURITY_PROTOCOL = config("KAFKA_SECURITY_PROTOCOL", cast=str, default="SASL_SSL")
except:
    KAFKA_SECURITY_PROTOCOL = "SASL_SSL"

try:
    KAFKA_SASL_JAAS_CONFIG = config("KAFKA_SASL_JAAS_CONFIG", cast=str, default="")
except:
    KAFKA_SASL_JAAS_CONFIG = ""

logger.info(f"DATABASE_URL loaded: {str(PRODUCT_SERVICE_DATABASE_URL)[:50]}...")  # Print first 50 chars
logger.info(f"BOOTSTRAP_SERVER: {KAFKA_BOOTSTRAP_SERVER}")
logger.info(f"SASL_MECHANISM: {KAFKA_SASL_MECHANISM}")
logger.info(f"SECURITY_PROTOCOL: {KAFKA_SECURITY_PROTOCOL}")