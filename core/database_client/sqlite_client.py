from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base
from core.models import Questions, ExecutionLogs


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


def insert_question(stage, question):
    """
    대화 내용을 데이터베이스에 저장하는 함수
    """
    db = SessionLocal()
    try:
        message = Questions(
            stage=stage,
            question=question
        )
        db.add(message)
        db.commit()
    finally:
        db.close()



def insert_execution_log(stage, block_json):
    """
    플레이어의 게임 이용 결과를 저장하는 함수
    """
    db = SessionLocal()
    try:
        coding_result = ExecutionLogs(
            stage=stage,
            block_json=block_json
        )
        db.add(coding_result)
        db.commit()
    finally:
        db.close()


def select_execution_log(stage: str):
    """
    가장 최신 플레이 기록으로 가져오기
    """
    db = SessionLocal()
    try:
        row = (
            db.query(ExecutionLogs.block_json)
            .filter_by(
                stage=stage
            ).order_by(ExecutionLogs.timestamp.desc(), ExecutionLogs.id.desc())
            .limit(1)
            .first() # 가장 최신 항목 하나만 가져옴

        )
        return row[0] if row else ""

    finally:
        db.close()