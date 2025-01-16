from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import os

DATABASE_CARELINK_CONNECTION_URL = os.getenv("DATABASE_CARELINK_CONNECTION_URL")
if not DATABASE_CARELINK_CONNECTION_URL:
    raise ValueError("DATABASE_CARELINK_CONNECTION_URL environment variable is not set")

carelink_engine = create_engine(
    DATABASE_CARELINK_CONNECTION_URL, pool_pre_ping=True, echo=False
)
carelink_session = sessionmaker(autocommit=False, autoflush=False, bind=carelink_engine)


def get_carelink_db() -> Generator[Session, None, None]:
    try:
        db_carelink = carelink_session()
        yield db_carelink
    except Exception as e:
        print(f"Error managing database session: {e}")
        raise
    finally:
        db_carelink.close()
