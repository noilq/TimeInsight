from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time_insight.data.models import Base
from time_insight.config import DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    print(DATABASE_URL)
    Base.metadata.create_all(bind=engine)