from fastapi import FastAPI , Depends , HTTPException , UploadFile , File , Form
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer
from contextlib import asynccontextmanager
import asyncio, json, base64
from typing import AsyncGenerator , Annotated , Optional
from sqlmodel import select
from . import setting
from .database import Product , Session , create_db_and_tables , get_session
from .consumer import consume_messages
from .producer import kafka_producer
from .authenticate import validate_role
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


     
@asynccontextmanager
async def lifespan(app : FastAPI) -> AsyncGenerator[None , None]:
    logger.info("Starting up product service...")
    logger.info(f"Connecting to database: {str(setting.PRODUCT_SERVICE_DATABASE_URL)[:50]}...")
    logger.info(f"Kafka bootstrap server: {setting.KAFKA_BOOTSTRAP_SERVER}")
    logger.info(f"Kafka product topic: {setting.KAFKA_PRODUCT_TOPIC}")

    try:
        logger.info("Creating database tables...")
        create_db_and_tables()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

    try:
        logger.info("Starting Kafka consumer task...")
        task = asyncio.create_task(consume_messages(setting.KAFKA_PRODUCT_TOPIC, setting.KAFKA_BOOTSTRAP_SERVER))
        logger.info("Kafka consumer task started.")
    except Exception as e:
        logger.error(f"Failed to start Kafka consumer: {e}")
        raise

    yield

    logger.info("Shutting down product service...")
    # Note: The consumer task runs indefinitely, so cleanup might not be reached
    # unless there's a specific shutdown mechanism 


app : FastAPI = FastAPI(lifespan=lifespan , version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/product" , response_model = Product)
async def product_service(
    Product_id: Annotated[int, Form()],
    Product_name: Annotated[str, Form()],
    Product_details: Annotated[str, Form()],
    product_quantity: Annotated[int, Form()],
    price: Annotated[float, Form()],
    producer: Annotated[AIOKafkaProducer, Depends(kafka_producer)],
    session: Annotated[Session, Depends(get_session)],
    token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))],
    file: Optional[UploadFile] = File(None),
) -> Product:
    """Create a new product with an optional image upload (multipart form)."""

    # Convert uploaded file to base64 if provided
    product_image_b64 = None
    if file:
        file_bytes = await file.read()
        product_image_b64 = base64.b64encode(file_bytes).decode("utf-8")

    product = Product(
        Product_id=Product_id,
        Product_name=Product_name,
        Product_details=Product_details,
        product_quantity=product_quantity,
        price=price,
        product_image=product_image_b64,
    )

    session.add(product)
    session.commit()
    session.refresh(product) 
    try:
        event = {"event_type" : "Product_Created" , "product" : product.dict()}
        await producer.send_and_wait(setting.KAFKA_PRODUCT_TOPIC ,  json.dumps(event).encode("utf-8"))
        print("Product Send to Kafka topic")
    except Exception as e:
        print("Error Sending to Kafka", e)
    
    return product



@app.get("/product/" , response_model=list[Product])
async def get_product(session : Annotated[Session , Depends(get_session)],
                      token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))]
                      ):
     products = session.exec(select(Product)).all()
     return  products


@app.put("/product/{product_id}" , response_model= Product)
async def update_product(product_id : int , product : Product , 
                         producer : Annotated[AIOKafkaProducer, Depends(kafka_producer)],
                         session : Annotated[Session , Depends(get_session)],
                         token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))]
                         ):
    db_product = session.get(Product , product_id)
    if not db_product:
        raise HTTPException(status_code=404 , detail = "Product Not Found")
    
    for fields , value in product.dict(exclude_unset=True).items():
        setattr(db_product , fields, value)
        
    session.commit()
    session.refresh(db_product)
    try:
        event = {"event_type" : "Product_Updated" , "product" : product.dict()}
        await producer.send_and_wait(setting.KAFKA_PRODUCT_TOPIC , json.dumps(event).encode("utf-8"))
        print("Updated_Product Send to Kafka topic")
    except Exception as e:
        print("Error Sending to Kafka", e)  

    return db_product

 
@app.delete("/product/{product_id}", response_model= Product)	
async def delete_product(product_id : int , session : Annotated[Session, Depends(get_session)],
                    producer : Annotated[AIOKafkaProducer, Depends(kafka_producer)],
                    token_data: Annotated[dict, Depends(validate_role(["seller", "admin"]))]
                   ):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail = "Product Not Found")
    product_dict = {field : getattr(db_product, field) for field in db_product.dict()}
    product_json = json.dumps(product_dict).encode("utf-8")
    print("product_json" , product_json)
    session.delete(db_product)
    session.commit()
    try:
        event = {"event_type" : "Product_Deleted" , "product" : product_dict}
        await producer.send_and_wait(setting.KAFKA_PRODUCT_TOPIC , json.dumps(event).encode("utf-8"))
        print("Deleted_Product Send to Kafka topic")
    except Exception as e:
        print("Error sending to Kafka:", e)

    return db_product


@app.get("/product/{product_id}/image")
async def get_product_image(
    product_id: int,
    session: Session = Depends(get_session),
    token_data: dict = Depends(validate_role(["seller", "admin"]))
):
    """Get the base64-encoded image for a product."""
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product Not Found")
    if not db_product.product_image:
        raise HTTPException(status_code=404, detail="No image uploaded for this product")

    return {
        "product_id": product_id,
        "product_image": db_product.product_image,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "service": "product-service",
        "message": "Product service is running and ready to accept requests"
    }