from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Application(Base):
    __tablename__ = 'application'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    desc = Column(Text)
    path = Column(Text)
    enrollment_date = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    activities = relationship('ApplicationActivity', back_populates='application')

class ApplicationActivity(Base):
    __tablename__ = 'application_activity'

    id = Column(Integer, primary_key=True, autoincrement=True)
    application_id = Column(Integer, ForeignKey('application.id'), index=True)
    window_name = Column(Text, nullable=False)
    additional_info = Column(Text)
    session_start = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    session_end = Column(DateTime(timezone=True))
    duration = Column(Integer)

    application = relationship('Application', back_populates='activities')

class UserSession(Base):
    __tablename__ = 'user_session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_session_type_id = Column(Integer, ForeignKey('user_session_type.id'))
    session_start = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    session_end = Column(DateTime(timezone=True))
    duration = Column(Integer)

    user_session_type = relationship('UserSessionType', back_populates='user_sessions')

class UserSessionType(Base):
    __tablename__ = 'user_session_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)

    user_sessions = relationship('UserSession', back_populates='user_session_type')
