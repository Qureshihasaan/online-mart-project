import logging, asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from . import setting
import os


loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.INFO)

async def consume_messages(topic, bootstrapserver) -> AIOKafkaConsumer:
    # Build Kafka configuration with SSL/SASL support for Aiven
    config = {
        "bootstrap_servers": setting.KAFKA_BOOTSTRAP_SERVER,
        "group_id": setting.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
        "auto_offset_reset": "earliest"
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
    
    consumer = AIOKafkaConsumer(
        setting.KAFKA_PRODUCT_TOPIC,
        **config
    )

    while True:
        try:
            await consumer.start()
            logging.info("Consumer Started...")
            break
        except KafkaConnectionError as e:
            logging.error(f"Consumer starting failed: {e}. Retry in 5 sec")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Unexpected error starting consumer: {e}. Retry in 5 sec")
            await asyncio.sleep(5)

    try:
        async for messages in consumer:
            consume = messages.value
            print("consumer_messages ", consume)
    except Exception as e:
        logging.error(f"Error consuming messages: {e}")
    finally:
        try:
            await consumer.stop()
        except Exception as e:
            logging.error(f"Error stopping consumer: {e}")
          