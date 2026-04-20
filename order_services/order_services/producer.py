from aiokafka import AIOKafkaProducer
from . import setting
import os


async def kafka_producer():
    # Build Kafka configuration with SSL/SASL support for Aiven
    config = {
        "bootstrap_servers": str(setting.KAFKA_BOOTSTRAP_SERVER)
    }
    
    # Add Aiven SSL/SASL configuration
    if os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER") or os.getenv("AIVEN_KAFKA_USERNAME"):
        config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_plain_username": os.getenv("AIVEN_KAFKA_USERNAME", ""),
            "sasl_plain_password": os.getenv("AIVEN_KAFKA_PASSWORD", ""),
        })
        
        ssl_cafile = os.getenv("AIVEN_SSL_CA_FILE")
        if ssl_cafile:
            config["ssl_cafile"] = ssl_cafile
    
    producer = AIOKafkaProducer(**config)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
