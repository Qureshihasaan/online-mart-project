"""
Shared Kafka configuration module for Aiven Kafka production deployment.
This module provides configuration for Kafka connections with Aiven Cloud Kafka.
"""

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


def get_kafka_config() -> dict:
    """
    Get Kafka configuration dictionary for Aiven Kafka production deployment.

    Returns:
        dict: Kafka configuration suitable for AIOKafkaProducer/Consumer
    
    Raises:
        ValueError: If AIVEN_KAFKA_BOOTSTRAP_SERVER is not configured
    """
    # Aiven Kafka configuration (required for production)
    aiven_bootstrap_server = config("AIVEN_KAFKA_BOOTSTRAP_SERVER", default="")

    if not aiven_bootstrap_server:
        raise ValueError(
            "AIVEN_KAFKA_BOOTSTRAP_SERVER must be set for production deployment. "
            "Please configure Aiven Kafka credentials in your .env file."
        )

    kafka_config = {
        "bootstrap_servers": aiven_bootstrap_server,
        "security_protocol": "SASL_SSL",
        "sasl_mechanism": "PLAIN",
        "sasl_plain_username": config("AIVEN_KAFKA_USERNAME", default=""),
        "sasl_plain_password": config("AIVEN_KAFKA_PASSWORD", default=""),
        "ssl_cafile": config("AIVEN_SSL_CA_FILE", default=None),
        "ssl_certfile": config("AIVEN_SSL_CERT_FILE", default=None),
        "ssl_keyfile": config("AIVEN_SSL_KEY_FILE", default=None),
    }

    logger.info("✓ Aiven Kafka configuration loaded (SASL_SSL enabled)")

    return kafka_config


# Get bootstrap server (required for production)
KAFKA_BOOTSTRAP_SERVER = config("AIVEN_KAFKA_BOOTSTRAP_SERVER", default="")
if not KAFKA_BOOTSTRAP_SERVER:
    logger.warning(
        "⚠ AIVEN_KAFKA_BOOTSTRAP_SERVER is not set. "
        "Kafka features will not work without Aiven configuration."
    )

# Topic configurations (with defaults for development)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", default="product-topic")
KAFKA_INVENTORY_TOPIC = config("KAFKA_INVENTORY_TOPIC", default="inventory-topic")
KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", default="order-topic")
KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", default="payment-topic")
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", default="user-topic")
KAFKA_DESIGN_TOPIC = config("KAFKA_DESIGN_TOPIC", default="design-topic")

# Consumer group IDs
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", default="product-group")
KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY = config("KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY", default="inventory-group")
KAFKA_CONSUMER_GROUP_ID_FOR_ORDER = config("KAFKA_CONSUMER_GROUP_ID_FOR_ORDER", default="order-group")
KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT", default="payment-group")
KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", default="user-group")
KAFKA_CONSUMER_GROUP_ID_FOR_DESIGN = config("KAFKA_CONSUMER_GROUP_ID_FOR_DESIGN", default="design-group")

logger.info(f"KAFKA_BOOTSTRAP_SERVER: {KAFKA_BOOTSTRAP_SERVER}")
logger.info("Using Aiven Kafka for production deployment")
