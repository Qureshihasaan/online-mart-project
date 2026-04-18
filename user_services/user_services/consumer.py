from aiokafka import AIOKafkaConsumer
import logging
from aiokafka.errors import KafkaConnectionError
import asyncio
import os
from . import setting

loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.INFO)


async def consume()->AIOKafkaConsumer:
    # Build Kafka configuration with SSL/SASL support for Aiven
    config = {
        "bootstrap_servers": setting.KAFKA_BOOTSTRAP_SERVER,
        "group_id": setting.KAFKA_CONSUMER_GROUP_ID_FOR_USER,
        "auto_offset_reset": "earliest",
        "enable_auto_commit": False,
        "consumer_timeout_ms": 1000
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
        
        logging.info("✓ Using Aiven Kafka with SASL_SSL")

    consumer = AIOKafkaConsumer(
        setting.KAFKA_USER_TOPIC,
        **config
    )
    while True:
        try :
            await consumer.start()
            logging.info("Consumer Started...")
            break
        except KafkaConnectionError as e: 
            logging.info("Consumer staring failed, Retry in 5 sec")
            await asyncio.sleep(5)
                   
                   
    try: 
        async for messages in consumer:
            consume = messages.value
            print("consumer_messages " , consume )
    finally:
        await consumer.stop()
          
