"""Database configuration"""

import os

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_url = os.getenv("DATABASE_URL", "sqlite:///sift.db")

engine = create_engine(url=db_url)

Session = sessionmaker(bind=engine)


def get_db():
    """Get database session"""
    session = Session()

    try:
        yield session
    finally:
        session.close()


DatabaseDep = Depends(get_db)
