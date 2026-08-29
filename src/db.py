"""Module to access the database"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///sift.db")

Session = sessionmaker(bind=engine)


def get_db():
    """Get connection to database"""
    session = Session()
    try:
        yield session
    finally:
        session.close()
