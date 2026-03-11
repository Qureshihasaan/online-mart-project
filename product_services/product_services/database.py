from sqlmodel import SQLModel , Field , create_engine , Session
from typing import Optional
from . import setting

class Product(SQLModel , table = True):
    product_id : Optional[int] = Field(default= None , primary_key=True)
    Product_name : str = Field(default=None)
    Product_details : str = Field(default=None)
    product_quantity : int = Field(default=0)
    price : float = Field(gt=0)
    product_image : Optional[str] = Field(default=None, description="Base64-encoded product image")


connection_strings = str(setting.PRODUCT_SERVICE_DATABASE_URL).replace(
    "postgresql" , "postgresql+psycopg2"
)


engine = create_engine(connection_strings , connect_args={} ,  pool_recycle=300)

def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)



def get_session():
    with Session(engine) as session:
        yield session 






















        
              
# def get_session():  
#     session = Session(engine)
#     try:
#         yield session
#     finally:
#         session.close()
    
   
#### For Converting datetime into string before it is serialized into json   
 
# class DatetimeEncoder(json.JSONEncoder):
#     def default(self , obj):
#         if isinstance(obj , datetime):
#             return obj.isoformat()
#         return super().default(obj)