from datetime import datetime

from sqlalchemy.orm import declarative_base, relationship

from sqlalchemy import Column, String, Text, DateTime, Integer

Base = declarative_base()

class Questions(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(String, nullable=False)

    question = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

class ExecutionLogs(Base):
    __tablename__ = "execution_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    stage = Column(String, nullable=False)

    block_json = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)