from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    messages = relationship("Message", back_populates="user")
    # 양방향 관계 설정
    # 한 명의 사용자가 여러 개의 메시지를 가질 수 있음

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    role = Column(String)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="messages")
    # 이 메시지를 쓴 사용자가 누구인지
    # ForeignKey로 연결된 사용자를 역참조
    # back_populates => 양쪽이 서로를 참조할 수 있게 연결하는 키워드
    # 복잡한 쿼리를 짜지 않아도 객체 간 탐색이 자동으로 된다. 


