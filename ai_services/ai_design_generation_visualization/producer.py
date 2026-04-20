"""
Kafka Producer — AI Design Visualization
=========================================
Provides an async generator dependency for FastAPI endpoints
that need to publish messages to Kafka topics.
"""
from __future__ import annotations

import os
from aiokafka import AIOKafkaProducer

import config


async def kafka_producer():
    """FastAPI dependency that yields a started Kafka producer."""
    # Build Kafka configuration with SSL/SASL support for Aiven
    kafka_config = {
        "bootstrap_servers": str(config.KAFKA_BOOTSTRAP_SERVER)
    }
    
    # Add Aiven SSL/SASL configuration
    if os.getenv("AIVEN_KAFKA_BOOTSTRAP_SERVER") or os.getenv("AIVEN_KAFKA_USERNAME"):
        kafka_config.update({
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            "sasl_plain_username": os.getenv("AIVEN_KAFKA_USERNAME", ""),
            "sasl_plain_password": os.getenv("AIVEN_KAFKA_PASSWORD", ""),
        })
        
        ssl_cafile = os.getenv("AIVEN_SSL_CA_FILE")
        if ssl_cafile:
            kafka_config["ssl_cafile"] = ssl_cafile
    
    producer = AIOKafkaProducer(**kafka_config)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()
