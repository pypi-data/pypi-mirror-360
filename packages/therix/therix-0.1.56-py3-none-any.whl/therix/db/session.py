# db/session.py

from sqlalchemy.orm import sessionmaker
from therix.db.db_manager import DatabaseManager

# Initialize the DatabaseManager singleton
db_manager = DatabaseManager()

# Construct the SQLAlchemy database URL

def get_sql_alchemy_url():
    SQLALCHEMY_DATABASE_URL = db_manager._construct_db_url()
    return SQLALCHEMY_DATABASE_URL
# Get the engine from the DatabaseManager
engine = db_manager._engine

# Optionally dispose the engine if needed
# engine.dispose()

# Create the session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)