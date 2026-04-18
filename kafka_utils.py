"""
Shared Kafka utilities for Aiven Kafka production deployment.
This module provides helper functions to create properly configured
Kafka producers and consumers with SSL/SASL support.
"""

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_kafka_config() -> dict:
    """
    Get Kafka configuration dictionary for Aiven Kafka production.

    Returns:
        dict: Configuration dict for AIOKafkaProducer/Consumer
    
    Raises:
        ValueError: If AIVEN_KAFKA_BOOTSTRAP_SERVER is not configured
    """
    aiven_bootstrap = os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER", "")

    if not aiven_bootstrap:
        raise ValueError(
            "AIVEN_KAFKA_BOOTSTRAP_SERVER must be set for production deployment. "
            "Please configure Aiven Kafka credentials in your environment variables."
        )

    config = {
        "bootstrap_servers": aiven_bootstrap,
        "security_protocol": "SASL_SSL",
        "sasl_mechanism": "PLAIN",
        "sasl_plain_username": os.getenv("AIVEN_KAFKA_USERNAME", ""),
        "sasl_plain_password": os.getenv("AIVEN_KAFKA_PASSWORD", ""),
    }

    # Optional SSL certificate verification
    ssl_cafile = os.getenv("AIVEN_SSL_CA_FILE")
    if ssl_cafile:
        config["ssl_cafile"] = ssl_cafile

    logger.info(f"✓ Aiven Kafka configuration loaded (SASL_SSL)")

    return config


async def create_producer() -> AIOKafkaProducer:
    """
    Create and start a Kafka producer with proper configuration.
    
    Returns:
        AIOKafkaProducer: Started producer instance
    """
    config = get_kafka_config()
    producer = AIOKafkaProducer(**config)
    
    try:
        await producer.start()
        logger.info("✓ Kafka producer started successfully")
        return producer
    except Exception as e:
        logger.error(f"✗ Failed to start Kafka producer: {e}")
        raise


async def create_consumer(
    topic: str,
    group_id: str,
    auto_offset_reset: str = "earliest"
) -> AIOKafkaConsumer:
    """
    Create and start a Kafka consumer with proper configuration and retry logic.
    
    Args:
        topic: Kafka topic to consume from
        group_id: Consumer group ID
        auto_offset_reset: Offset reset strategy (default: "earliest")
    
    Returns:
        AIOKafkaConsumer: Started consumer instance
    """
    config = get_kafka_config()
    config.update({
        "group_id": group_id,
        "auto_offset_reset": auto_offset_reset,
    })
    
    consumer = AIOKafkaConsumer(topic, **config)
    
    # Retry logic for connection
    max_retries = 5
    for attempt in range(max_retries):
        try:
            await consumer.start()
            logger.info(f"✓ Kafka consumer started for topic: {topic}")
            return consumer
        except KafkaConnectionError as e:
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)
                logger.warning(f"Consumer connection failed (attempt {attempt + 1}/{max_retries}). "
                             f"Retrying in {wait_time}s... Error: {e}")
                import asyncio
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"✗ Consumer failed to start after {max_retries} attempts: {e}")
                raise
        except Exception as e:
            logger.error(f"✗ Unexpected error starting consumer: {e}")
            raise
    
    return consumer


async def kafka_producer_generator():
    """
    Async generator for FastAPI dependency injection.
    Yields a started producer and ensures cleanup.
    
    Usage:
        @app.post("/endpoint")
        async def endpoint(producer: Annotated[AIOKafkaProducer, Depends(kafka_producer_generator)]):
            pass
    """
    producer = await create_producer()
    try:
        yield producer
    finally:
        try:
            await producer.stop()
            logger.info("✓ Kafka producer stopped")
        except Exception as e:
            logger.error(f"Error stopping producer: {e}")


async def consume_messages_with_retry(topic: str, group_id: str):
    """
    Consume messages from a topic with automatic reconnection.
    
    Args:
        topic: Kafka topic name
        group_id: Consumer group ID
    
    Usage:
        async for message in consume_messages_with_retry("topic", "group"):
            process(message)
    """
    consumer = await create_consumer(topic, group_id)
    
    try:
        async for message in consumer:
            yield message
    except Exception as e:
        logger.error(f"Error consuming messages: {e}")
    finally:
        try:
            await consumer.stop()
            logger.info("✓ Kafka consumer stopped")
        except Exception as e:
            logger.error(f"Error stopping consumer: {e}")
