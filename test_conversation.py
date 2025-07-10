"""
대화 기록을 고려한 chat 함수 테스트 스크립트
"""

from core.database import init_db
from core.llm_handler import chat

def test_conversation():
    """대화 기록을 고려한 응답 테스트"""

    print("\n=== 대화 기록을 고려한 응답 테스트 ===\n")
    
    # 첫 번째 질문 (대화 기록 없음)
    print("1. 첫 번째 질문 (대화 기록 없음):")
    response1 = chat("안녕하세요!", "u001", "s001")
    print(f"질문: 안녕하세요!")
    print(f"답변: {response1}\n")
    
    # 두 번째 질문 (대화 기록 있음)
    print("2. 두 번째 질문 (대화 기록 있음):")
    response2 = chat("네 이름은 뭐야?", "u001", "s001")
    print(f"질문: 네 이름은 뭐야?")
    print(f"답변: {response2}\n")
    
    # 세 번째 질문 (대화 기록 있음)
    print("3. 세 번째 질문 (대화 기록 있음):")
    response3 = chat("이 게임의 규칙에 대해 간략하게 설명해줘", "u001", "s001")
    print(f"질문: 이 게임의 규칙에 대해 간략하게 설명해줘")
    print(f"답변: {response3}\n")
    
    # 새로운 세션에서 질문 (대화 기록 없음)
    print("4. 새로운 세션에서 질문 (대화 기록 없음):")
    response4 = chat("안녕하세요!", "u001", "s002")
    print(f"질문: 안녕하세요!")
    print(f"답변: {response4}\n")

    
from core.database import SessionLocal
from core.models import Base, User, Message

def add_sample_user():
    db = SessionLocal()

    # 사용자 추가
    db.merge(User(user_id="u001", username="메아미"))

    # 메시지 추가
    msg1 = Message(conversation_id="s001", user_id="u001", role="human", content="안녕")
    msg2 = Message(conversation_id="s001", user_id="u001", role="ai", content="반가워요!")
    db.add_all([msg1, msg2])
    db.commit()
    db.close()

# # 메시지 조회
# results = db.query(Message).filter_by(conversation_id="s001").all()
# for m in results:
#     print(f"[{m.role}] {m.content} ({m.timestamp})")


if __name__ == "__main__":
    # 데이터베이스 초기화 및 샘플 데이터 추가
    print("데이터베이스 초기화 중...")
    init_db()
    # add_sample_user()
    test_conversation() 



if __name__ == "__main__":
    init_db()
    # add_sample_user_and_messages()
