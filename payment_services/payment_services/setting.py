from starlette.config import Config
from starlette.datastructures import Secret


try:
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    print("✗ .env file NOT found, using empty config")


PAYMENT_DATABASE_URL = config("PAYMENT_DATABASE_URL", cast=Secret)

KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT = config(
    "KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT", cast=str
)

KAFKA_PAYMENT_TOPIC = config("KAFKA_PAYMENT_TOPIC", cast=str)

KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)

SECRET_KEY = config("SECRET_KEY", cast=str)

ALGORITHM = config("ALGORITHMS", cast=str)
