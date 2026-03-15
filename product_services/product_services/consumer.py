import logging, asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
from . import setting


loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.INFO)

async def consume_messages(topic, bootstrapserver) -> AIOKafkaConsumer:
    # Configure consumer with Azure Event Hubs specific settings
    consumer_config = {
        'bootstrap_servers': setting.KAFKA_BOOTSTRAP_SERVER,
        'group_id': setting.KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT,
        'auto_offset_reset': 'earliest',
    }

    # Add Azure Event Hubs specific authentication if environment variables are set
    if hasattr(setting, 'KAFKA_SASL_MECHANISM') and setting.KAFKA_SASL_MECHANISM:
        consumer_config.update({
            'security_protocol': getattr(setting, 'KAFKA_SECURITY_PROTOCOL', 'SASL_SSL'),
            'sasl_mechanism': setting.KAFKA_SASL_MECHANISM,
            'sasl_plain_username': '$ConnectionString',
        })

        # Extract password from JAAS config for Azure Event Hubs
        if hasattr(setting, 'KAFKA_SASL_JAAS_CONFIG'):
            # Extract the connection string from the JAAS config
            import re
            jaas_config = setting.KAFKA_SASL_JAAS_CONFIG
            # Look for password field in the JAAS config
            password_match = re.search(r"password='([^']+)'", jaas_config)
            if password_match:
                consumer_config['sasl_plain_password'] = password_match.group(1)

    consumer = AIOKafkaConsumer(
        setting.KAFKA_PRODUCT_TOPIC,
        **consumer_config
    )

    # await consumer.start()
    # consumer.subscribe(["my_topic"])
    # return consumer

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
          