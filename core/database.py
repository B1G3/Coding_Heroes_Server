from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, User, Message


import logging
logger = logging.getLogger(__name__)
logger.info("database logger")


DB_URL = "sqlite:///coding-heroes.db"
engine = create_engine(DB_URL, echo=False)
"""
sessionmaker는 SQLAlchemy에서 session 객체를 생성하는 factory
"""
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
# 테이블이 존재하지 않으면 새로 생성


def select_messages_by_user_and_conversation_id(user_id: str, conversation_id: str) -> str:
    """
    사용자의 이전 대화 내용을 조회하는 함수
    """
    db = SessionLocal()
    try:
        messages = db.query(Message).filter_by(
            user_id=user_id,
            conversation_id=conversation_id
        ).order_by(Message.timestamp).all()

        logger.info(f"type(messages) => {type(messages)}")

        if not messages:
            return ""

        return messages
      
    finally:
        db.close()


def add_message(user_id: str, conversation_id: str, role: str, content: str):
    """
    대화 내용을 데이터베이스에 저장하는 함수
    """
    db = SessionLocal()
    try:
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content
        )
        db.add(message)
        db.commit()
    finally:
        db.close()





