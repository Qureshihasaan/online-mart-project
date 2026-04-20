from aiokafka import AIOKafkaProducer
from . import setting
import logging
import os


async def kafka_producer():
    # Build Kafka configuration with SSL/SASL support for Aiven
    config = {
        "bootstrap_servers": str(setting.KAFKA_BOOTSTRAP_SERVER)
    }
    
    # Add Aiven SSL/SASL configuration if using Aiven
    aiven_bootstrap = os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER", "")
    if aiven_bootstrap:
        config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_plain_username": os.getenv("AIVEN_KAFKA_USERNAME", ""),
            "sasl_plain_password": os.getenv("AIVEN_KAFKA_PASSWORD", ""),
        })
    
    producer = AIOKafkaProducer(**config)

    try:
        await producer.start()
        yield producer
    except Exception as e:
        logging.error(f"Failed to start Kafka producer: {e}")
        raise
    finally:
        try:
            await producer.stop()
        except Exception as e:
            logging.error(f"Error stopping producer: {e}") 


