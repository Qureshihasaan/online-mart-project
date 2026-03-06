from sqlmodel import SQLModel , Field, Session , create_engine
from . import setting

connection_strings = str(setting.PAYMENT_DATABASE_URL).replace(
    "postgresql" , "postgresql+psycopg2"
)

engine = create_engine(connection_strings , connect_args={} , pool_recycle=300) 


def create_db_and_tables()->None:
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session