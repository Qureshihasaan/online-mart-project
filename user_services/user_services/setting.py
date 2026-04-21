from starlette.config import Config
from starlette.datastructures import Secret

# try:
#     config = Config(".env")
#     print("✓ .env file found and loaded")
# except FileNotFoundError:
#     config = Config("")
#     print("✗ .env file NOT found, using empty config")
config = Config(".env")

USER_SERVICE_DATABASE_URL = config("USER_SERVICE_DATABASE_URL", cast=Secret)
KAFKA_BOOTSTRAP_SERVER = config("KAFKA_BOOTSTRAP_SERVER", cast=str)
KAFKA_USER_TOPIC = config("KAFKA_USER_TOPIC", cast=str)
KAFKA_CONSUMER_GROUP_ID_FOR_USER = config("KAFKA_CONSUMER_GROUP_ID_FOR_USER", cast=str)

KAFKA_TOPIC_FROM_USER_TO_ORDER = config("KAFKA_TOPIC_FROM_USER_TO_ORDER", cast=str)

### JWT Variables
SECRET_KEY = config("SECRET_KEY", cast=Secret)
ALGORITHM = config("ALGORITHMS", cast=str)
ACCESS_TOKEN_EXPIRE_MINUTES = config(
    "ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=10
)

### Google OAuth
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", cast=str)


# KAFKA_SASL_USERNAME = config("KAFKA_SASL_USERNAME", cast=str)
# KAFKA_SASL_PASSWORD = config("KAFKA_SASL_PASSWORD", cast=str)
