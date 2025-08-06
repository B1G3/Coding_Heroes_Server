from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, User, Message, PlayRecord


import logging
logger = logging.getLogger(__name__)
logger.info("database logger")

from config import DB_URL
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
# sessionmaker는 SQLAlchemy에서 session 객체를 생성하는 factory




# ----------------- main.py에서 서버 실행시 한 번 호출 ---------------
def init_db():
    Base.metadata.create_all(bind=engine)


def save_user(user_id: str, username: str):
    db = SessionLocal()
    try:
        user = User(
            user_id=user_id,
            username=username
        )
        db.add(user)
        db.commit()

    finally:
        db.close()



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





def save_message(user_id: str, conversation_id: str, role: str, content: str):
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





def delete_messages_by_ids(ids: list):
    """
    메시지 id 리스트를 받아 해당 메시지들을 삭제하는 함수
    """
    db = SessionLocal()
    try:
        db.query(Message).filter(Message.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()



def delete_playrecord(ids: list):
    db = SessionLocal()
    try:
        db.query(PlayRecord).filter(PlayRecord.id.in_(ids)).delete(synchronize_session=False)
        db.commit()
    finally:
        db.close()



def save_playrecord(user_id: str, stage: str, json_str: str):
    """
    플레이어의 게임 이용 결과를 저장하는 함수
    """
    db = SessionLocal()
    try:
        coding_result = PlayRecord(
            user_id=user_id,
            json_str=json_str,
            stage=stage
        )
        db.add(coding_result)
        db.commit()
    finally:
        db.close()


def select_playrecord(user_id: str, stage: str):
    """
    가장 최신 플레이 기록으로 가져오기
    """
    db = SessionLocal()
    try:
        json_str = (
            db.query(PlayRecord.json_str)
            .filter_by(
                user_id=user_id,
                stage=stage
            ).order_by(PlayRecord.timestamp.desc())
            .scalar() # 가장 최신 항목 하나만 가져옴

        )
        logger.info(f"json_str => {json_str}")

        return json_str or ""

    finally:
        db.close()