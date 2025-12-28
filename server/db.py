import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("CLINICGUARD_DB_PATH", "sqlite:///clinicguard.db")
engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    calls = relationship("Call", back_populates="patient")
    summaries = relationship("Summary", back_populates="patient")

class Call(Base):
    __tablename__ = "calls"
    id = Column(Integer, primary_key=True, index=True)
    call_sid = Column(String, unique=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    outcome = Column(String, nullable=True)
    conversation_logs = relationship("ConversationLog", back_populates="call")
    patient = relationship("Patient", back_populates="calls")

class ConversationLog(Base):
    __tablename__ = "conversation_logs"
    id = Column(Integer, primary_key=True, index=True)
    call_id = Column(Integer, ForeignKey("calls.id"))
    role = Column(String)  # 'User' or 'Assistant'
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    call = relationship("Call", back_populates="conversation_logs")

class Summary(Base):
    __tablename__ = "summaries"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    summary_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="summaries")

def init_db():
    """
    Initialize the database by creating all tables.
    This should be called once at application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Database initialized successfully at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise 