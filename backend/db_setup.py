from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from database import Base
import os

class DatabaseConnection:
    def __init__(self, db_url: str = None):
        if db_url is None:
            # Default to SQLite database in the current directory
            db_url = 'sqlite:///finance_data.db'
        
        self.engine = create_engine(db_url, echo=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self) -> Session:
        """Get a new database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close the database connection"""
        self.engine.dispose()

# Usage example
def init_db():
    """Initialize the database and create tables"""
    db = DatabaseConnection()
    db.create_tables()
    return db

# Create tables if running this file directly
if __name__ == "__main__":
    db = init_db()
    print("Database initialized and tables created successfully!") 