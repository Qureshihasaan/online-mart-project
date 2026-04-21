from aiokafka import AIOKafkaProducer
from . import setting
import logging
import os


async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_server=str(setting.KAFKA_BOOTSTRAP_SERVER))

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
