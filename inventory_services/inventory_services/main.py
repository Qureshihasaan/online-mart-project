import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Annotated, AsyncGenerator, List
from aiokafka import AIOKafkaProducer
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select
from . import setting
from .conusmer import consume_product_events, consume_order_events
from .database import create_db_and_tables, engine
from .model import Inventory_update, Stock_update
from .producer import kafka_producer1
from .authenticate import validate_role


loop = asyncio.get_event_loop()
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Waiting for Kafka to be ready...")
    await asyncio.sleep(10)

    print("Creating database Tables...")
    create_db_and_tables()

    print("Tables Created")
    consumer_task = asyncio.create_task(consume_product_events())
    order_consumer_task = asyncio.create_task(consume_order_events())
    yield
    consumer_task.cancel()
    order_consumer_task.cancel()


app: FastAPI = FastAPI(lifespan=lifespan, version="1.0.0")


def get_db():
    with Session(engine) as session:
        yield session


@app.get("/get_single_stock_update")
def get_single_stock_update(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))],
):
    stock = db.exec(
        select(Stock_update).where(Stock_update.product_id == product_id)
    ).first()
    if not stock:
        raise HTTPException(
            status_code=404, detail=f"Stock for Product ID {product_id} not found"
        )
    return stock


@app.get("/get_stock_update")
def get_stock_update(
    db: Annotated[Session, Depends(get_db)],
    token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))],
):
    stock = db.exec(select(Stock_update)).all()
    return stock


@app.delete("/delete_stock/{product_id}")
def delete_stock(
    product_id: int,
    db: Annotated[Session, Depends(get_db)],
    token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))],
):
    stock = db.exec(
        select(Stock_update).where(Stock_update.product_id == product_id)
    ).first()
    if not stock:
        raise HTTPException(
            status_code=404, detail=f"Stock for Product ID {product_id} not found"
        )
    db.delete(stock)
    db.commit()
    return {"detail": f"Stock for Product ID {product_id} deleted successfully"}


@app.get("/check_inventory/{product_id}/{quantity}")
async def check_inventory(product_id: int, quantity: int):
    with Session(engine) as session:
        product = session.exec(
            select(Stock_update).where(Stock_update.product_id == product_id)
        ).first()
        if product and product.product_quantity >= quantity:
            return {"available": True}
        else:
            return {"available": False}
