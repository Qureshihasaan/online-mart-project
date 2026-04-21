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

KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)


KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)
KAFKA_ORDER_CREATED_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)
KAFKA_TOPIC_FOR_ORDER_CANCELLED = config("KAFKA_TOPIC_FOR_ORDER_CANCELLED", cast=str)
KAFKA_TOPIC_FOR_PAYMENT_DONE = config("KAFKA_PAYMENT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION_SERVICE = config(
    "KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION_SERVICE", cast=str
)

SENDER_EMAIL = config("SENDER_EMAIL", cast=str)
SENDER_PASSWORD = config("SENDER_EMAIL_PASSWORD", cast=str)
