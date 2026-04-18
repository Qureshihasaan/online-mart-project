from starlette.config import Config
from starlette.datastructures import Secret
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    config = Config(".env")
    logger.info("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    logger.warning("✗ .env file NOT found, using empty config")

# Aiven Kafka Configuration
AIVEN_KAFKA_BOOTSTRAP_SERVER = os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER", "")
KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", default=AIVEN_KAFKA_BOOTSTRAP_SERVER)

if not KAFKA_BOOTSTRAP_SERVER:
    logger.warning("⚠ KAFKA_BOOTSTRAP_SERVER not set. Kafka features will not work.")
else:
    logger.info(f"✓ Kafka bootstrap server: {KAFKA_BOOTSTRAP_SERVER}")

KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str, default="user-topic")
KAFKA_ORDER_CREATED_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str, default="order-topic")
KAFKA_TOPIC_FOR_ORDER_CANCELLED = config("KAFKA_TOPIC_FOR_ORDER_CANCELLED", cast=str, default="order-cancelled-topic")
KAFKA_TOPIC_FOR_PAYMENT_DONE = config("KAFKA_PAYMENT_TOPIC", cast=str, default="payment-topic")
KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION_SERVICE = config("KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION_SERVICE", cast=str, default="notification-group")

SENDER_EMAIL = config("SENDER_EMAIL", cast=str)
SENDER_PASSWORD = config("SENDER_EMAIL_PASSWORD", cast=str)


def get_kafka_consumer_config(topic: str, group_id: str) -> dict:
    """Get Kafka consumer configuration with Aiven SSL/SASL support"""
    consumer_config = {
        "bootstrap_servers": KAFKA_BOOTSTRAP_SERVER,
        "auto_offset_reset": "earliest"
    }
    
    # Add Aiven SSL/SASL configuration if using Aiven
    if os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER") or os.getenv("AIVEN_KAFKA_USERNAME"):
        consumer_config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_plain_username": os.getenv("AIVEN_KAFKA_USERNAME", ""),
            "sasl_plain_password": os.getenv("AIVEN_KAFKA_PASSWORD", ""),
        })
        
        ssl_cafile = os.getenv("AIVEN_SSL_CA_FILE")
        if ssl_cafile:
            consumer_config["ssl_cafile"] = ssl_cafile
        
        logger.info("✓ Using Aiven Kafka with SASL_SSL for consumer")
    else:
        logger.info("✓ Using Kafka without SASL_SSL")
    
    return consumer_config