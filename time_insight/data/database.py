from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from time_insight.data.models import Base, UserSessionType
from time_insight.config import DATABASE_URL
from time_insight.log import log_to_console

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    #log_to_console(DATABASE_URL)
    Base.metadata.create_all(bind=engine)

    
    session = SessionLocal()
    try:
        default_session_types = [
            {"id": 1, "name": "Active"},
            {"id": 2, "name": "Sleep"}
        ]
        for default_session_type in default_session_types:
            existing = session.query(UserSessionType).filter_by(id=default_session_type["id"]).first()
            if not existing:
                session.add(UserSessionType(**default_session_type))
        session.commit()
    except IntegrityError:
        session.rollback()
        log_to_console("Data is already in UserSessionType table or error appeared.")
    finally:
        session.close()
        log_to_console("Successfully created data in UserSessionType table.")