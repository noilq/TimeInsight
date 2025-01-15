import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from time_insight.data.models import Base, UserSessionType
from time_insight.config import DATABASE_URL, BASE_DIR

from time_insight.logging.logger import logger

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    #log_to_console(DATABASE_URL)

    #create db if not exists
    db_path = os.path.join(BASE_DIR, 'data', 'time_insight.db')
    if not os.path.exists(db_path):
        logger.info("Database file not found. Creating a new database.")

    Base.metadata.create_all(bind=engine)

    logger.info("Database initialization started.")

    session = SessionLocal()
    try:
        default_session_types = [
            {"id": 1, "name": "Active"},
            {"id": 2, "name": "Sleep"}
        ]
        for default_session_type in default_session_types:
            existing = session.query(UserSessionType).filter_by(id=default_session_type["id"]).first()
            if not existing:
                session.add(UserSessionType(**default_session_type))    #типо дикшионари распаковывает звездочками
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error during database initialization: {e}")
    finally:
        session.close()
        logger.info("Database initialization completed successfully.")