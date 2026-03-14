from starlette.config import Config
from starlette.datastructures import Secret

try: 
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    print("✗ .env file NOT found, using empty config")


INVENTORY_DATABASE_URL = config("INVENTORY_DATABASE_URL", cast=Secret)

# TEST_DATABASE_URL = config("TEST_DATABASEURL", cast=Secret)

KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)

# KAFKA_INVENTORY_TOPIC = config("KAFKA_INVENTORY_TOPIC", cast=str)

KAFKA_ORDER_TOPIC = config("KAFKA_ORDER_TOPIC", cast=str)


# KAFKA_ORDER_STATUS_TOPIC = config("KAFKA_ORDER_STATUS_TOPIC", cast=str)


# KAFKA_INVENTORY_TOPIC = config("KAFKA_INVENTORY_TOPIC", cast=str)

KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)

# KAFKA_TOPIC_FOR_PRODUCT_EVENT = config("KAFKA_TOPIC_FOR_PRODUCT_EVENT", cast=str)

KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY = config("KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY", cast=str)

# Security
SECRET_KEY = config("SECRET_KEY", cast=str)
ALGORITHMS = config("ALGORITHMS", cast=str)
