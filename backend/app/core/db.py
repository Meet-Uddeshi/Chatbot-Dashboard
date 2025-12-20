from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Connection 
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "mysql+pymysql://root:@127.0.0.1:3306/analytics_db" 
) 

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

def get_db():
    """Dependency injector that provides a connection and ensures it is closed."""
    connection: Connection = engine.connect()
    try:
        yield connection 
    finally:
        connection.close()