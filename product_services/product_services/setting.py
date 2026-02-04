from starlette.config import Config
from starlette.datastructures import Secret


try: 
    config = Config(".env")
    print("✓ .env file found and loaded")
except FileNotFoundError:
    config = Config("")
    print("✗ .env file NOT found, using empty config")
    

PRODUCT_SERVICE_DATABASE_URL = config("PRODUCT_SERVICE_DATABASE_URL", cast=Secret)
BOOTSTRAP_SERVER = config("BOOTSTRAP_SERVER", cast=str)
KAFKA_PRODUCT_TOPIC = config("KAFKA_PRODUCT_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT = config("KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT", cast=str)

# TEST_DATABASE_URL = config("TEST_DATABASE_URL", cast=Secret)

print(f"DATABASE_URL loaded: {str(PRODUCT_SERVICE_DATABASE_URL)[:50]}...")  # Print first 50 chars
print(f"BOOTSTRAP_SERVER: {BOOTSTRAP_SERVER}")