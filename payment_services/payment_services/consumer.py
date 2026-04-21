import asyncio
import logging
import os
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from . import setting

loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.INFO)


async def consume_messages(topic, bootstarpserver) -> AIOKafkaConsumer:

    consumer = AIOKafkaConsumer(
        setting.KAFKA_PAYMENT_TOPIC,
        bootstrap_server=setting.KAFKA_BOOTSTRAP_SERVER,
        group_id=setting.KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT,
        auto_offset_reset="earliest",
    )

    while True:
        try:
            await consumer.start()
            logging.info("consumer started...")
            break
        except KafkaConnectionError as e:
            logging.info("Consumer starting failed, Retry in 5 sec...")
            await asyncio.sleep(5)

    try:
        async for messages in consumer:
            consume = messages.value
            print("Consumer_messages", consume)
    except:
        await consumer.stop()
