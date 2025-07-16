from fastapi import Depends
from sqlalchemy.orm import Session
from db.db_config import SessionLocal

from typing import Generator

# Dependency to provide a DB session per request.
# Uses SQLAlchemy session factory configured in db_config.
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
