"""
Kafka Consumer — AI Design Visualization
==========================================
Consumes product events from Kafka to know which products
are available for design application.
"""

from __future__ import annotations

import asyncio
import json
import logging

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

import config

logging.basicConfig(level=logging.INFO)


async def consume_product_events() -> None:
    """Listen for product lifecycle events from the Product Service.

    Events received:
        - Product_Created
        - Product_Updated
        - Product_Deleted

    Currently logs the events.  Extend this to cache product data
    locally if needed for design generation.
    """

    consumer = AIOKafkaConsumer(
        config.KAFKA_PRODUCT_TOPIC,
        bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVER,
        group_id=config.KAFKA_CONSUMER_GROUP_ID,
        auto_offset_reset="earliest",
    )

    # Retry connection with back-off
    while True:
        try:
            await consumer.start()
            logging.info(
                "AI Design consumer started — listening on '%s'",
                config.KAFKA_PRODUCT_TOPIC,
            )
            break
        except KafkaConnectionError:
            logging.warning("Kafka not ready, retrying in 5 s …")
            await asyncio.sleep(5)

    try:
        async for message in consumer:
            try:
                event = json.loads(message.value.decode("utf-8"))
                event_type = event.get("event_type", "unknown")
                logging.info("Received event: %s", event_type)

                if event_type == "Product_Created":
                    product = event.get("product", {})
                    logging.info(
                        "New product available for design: %s (id=%s)",
                        product.get("Product_name"),
                        product.get("product_id"),
                    )
                elif event_type == "Product_Updated":
                    logging.info(
                        "Product updated: %s",
                        event.get("product", {}).get("product_id"),
                    )
                elif event_type == "Product_Deleted":
                    logging.info(
                        "Product deleted: %s",
                        event.get("product", {}).get("product_id"),
                    )

            except json.JSONDecodeError:
                logging.error("Failed to decode Kafka message: %s", message.value)
    finally:
        await consumer.stop()
