from aiokafka import AIOKafkaProducer
from . import setting
import os


async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_server=str(setting.KAFKA_BOOTSTRAP_SERVER))
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
