from sqlalchemy import Column, Integer, String, Text, DateTime , ForeignKey # type: ignore
from sqlalchemy.orm import relationship # type: ignore
from sqlalchemy.ext.declarative import declarative_base # type: ignore
from datetime import datetime, timezone

Base = declarative_base()

class Application(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    desc = Column(Text)
    path = Column(Text)
    enrollment_date = Column(DateTime, default=datetime.now(timezone.utc))

    activities = relationship('ApplicationActivity', back_populates='application')

class ApplicationActivity(Base):
    __tablename__ = 'application_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('application.id'), index=True)
    window_name = Column(Text, nullable=False)
    additional_info = Column(Text)
    session_start = Column(DateTime, default=datetime.now(timezone.utc))
    session_end = Column(DateTime)
    duration = Column(Integer)

    application = relationship('Application', back_populates='activities')

class SystemActivity(Base):
    __tablename__ = 'system_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    system_activity_type_id = Column(Integer, ForeignKey('system_activity_type.id'), index=True)
    start_time = Column(DateTime, default=datetime.now(timezone.utc))
    end_time = Column(DateTime)
    duration = Column(Integer)

    activity_type = relationship('SystemActivityType', back_populates='activities')

class SystemActivityType(Base):
    __tablename__ = 'system_activity_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)

    activities = relationship('SystemActivity', back_populates='activity_type')

class UserSession(Base):
    __tablename__ = 'user_session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_start = Column(DateTime, default=datetime.now(timezone.utc))
    session_end = Column(DateTime)
    duration = Column(Integer)