from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    print("✗ .env file NOT found, using empty config")


ORDER_DATABASE_URL = config("ORDER_DATABASE_URL", cast=Secret)

KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)

KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_ORDER = config(
    "KAFKA_CONSUMER_GROUP_ID_FOR_ORDER", cast=str
)

# TEST_DATABASE_URL =config("TEST_DATABASE_URL" , cast=Secret)

KAFKA_TOPIC_FROM_USER_TO_ORDER = config("KAFKA_TOPIC_FROM_USER_TO_ORDER", cast=str)

# KAFKA_ORDER_STATUS_TOPIC = config("KAFKA_ORDER_STATUS_TOPIC", cast=str)

SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHMS = config("ALGORITHMS", cast=str)

ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int)


# KAFKA_PAYMENT_TOPIC =config("PAYMENT_REQUEST_TOPIC", cast=str)
