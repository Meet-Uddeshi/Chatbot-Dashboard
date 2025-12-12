# backend/app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Connection # Import Connection type for type hinting
import os

# Adapt to MySQL/XAMPP connection string
# Format: mysql+pymysql://user:password@host:port/database_name
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "mysql+pymysql://root:@127.0.0.1:3306/analytics_db" # XAMPP default
) 

# Create the Engine with connection pooling settings suitable for web apps
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