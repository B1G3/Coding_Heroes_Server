from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.models import Base, User, Message

DB_URL = "sqlite:///coding-heroes.db"
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
# 테이블이 존재하지 않으면 새로 생성



# 테스트


# def add_sample_user_and_messages():
#     db = SessionLocal()

#     # 사용자 추가
#     db.merge(User(user_id="u001", username="메아미"))

#     # 메시지 추가
#     msg1 = Message(session_id="s001", user_id="u001", role="human", content="안녕")
#     msg2 = Message(session_id="s001", user_id="u001", role="ai", content="반가워요!")
#     db.add_all([msg1, msg2])
#     db.commit()

#     # 메시지 조회
#     results = db.query(Message).filter_by(session_id="s001").all()
#     for m in results:
#         print(f"[{m.role}] {m.content} ({m.timestamp})")

# if __name__ == "__main__":
#     add_sample_user_and_messages()
