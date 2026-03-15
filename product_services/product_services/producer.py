from aiokafka import AIOKafkaProducer
from . import setting
import logging


async def kafka_producer():
    # Configure producer with Azure Event Hubs specific settings
    producer_config = {
        'bootstrap_servers': str(setting.KAFKA_BOOTSTRAP_SERVER),
    }

    # Add Azure Event Hubs specific authentication if environment variables are set
    if hasattr(setting, 'KAFKA_SASL_MECHANISM') and setting.KAFKA_SASL_MECHANISM:
        producer_config.update({
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
                producer_config['sasl_plain_password'] = password_match.group(1)

    producer = AIOKafkaProducer(**producer_config)

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


