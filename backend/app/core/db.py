import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Fetch Database URL
# Ensure this matches your setup: mysql+pymysql://<user>:<password>@<host>/<db_name>
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost/analytics_db")

# 3. Configure the Engine (CRITICAL FIXES APPLIED HERE)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # [Fix 1] pool_pre_ping=True
    # Before every transaction, SQLAlchemy sends "SELECT 1". 
    # If the connection is dead (WinError 10054), it is discarded and a fresh one is created.
    # This prevents the 2013 error completely.
    pool_pre_ping=True,

    # [Fix 2] pool_recycle=3600
    # Automatically discard connections that have been open for 1 hour (3600s).
    # This prevents hitting MySQL's "wait_timeout" limit.
    pool_recycle=3600,

    # [Performance Tuning]
    # pool_size: The number of connections to keep open inside the connection pool.
    pool_size=10,
    
    # max_overflow: How many connections to allow strictly above the pool_size 
    # during traffic spikes.
    max_overflow=20,
    
    # pool_timeout: The number of seconds to wait before giving up on getting a connection.
    pool_timeout=30
)

# 4. Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. Base Class for Models
Base = declarative_base()

# 6. Dependency Injection for FastAPI
def get_db():
    """
    Generator function to create a database session for a request
    and close it immediately after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()