from aiokafka import AIOKafkaProducer
from . import setting


async def kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers = str(setting.KAFKA_BOOTSTRAP_SERVER))
    await producer.start()
    try: 
        yield producer
    finally:
        await producer.stop()
