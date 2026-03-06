from sqlmodel import SQLModel , Field , create_engine
from typing import  Optional
# from .setting import INVENTORY_DATABASE_URL
from . import setting
    
    
### Database connectivity 

connection_string = str(setting.INVENTORY_DATABASE_URL).replace(
    "postgresql" , "postgresql+psycopg2"
)

engine = create_engine(connection_string , connect_args={} , pool_recycle=300)

def create_db_and_tables()-> None:
   SQLModel.metadata.create_all(engine) 