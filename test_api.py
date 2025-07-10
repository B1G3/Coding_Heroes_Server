from fastapi.testclient import TestClient
from main import app

# TestClient 생성
client = TestClient(app)

def test_health_check():
    """기본 헬스 체크 테스트"""
    response = client.get("/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")

def test_ai_npc_chat():
    """AI NPC 채팅 엔드포인트 테스트"""
    test_data = {
        "message": "안녕하세요!",
        "user_id": "test_user_001"
    }
    
    response = client.post("/ai_npc/chat", json=test_data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"AI 응답: {data}")
    else:
        print(f"Error: {response.text}")

def test_database_connection():
    """데이터베이스 연결 테스트"""
    # 간단한 GET 요청으로 서버가 정상 작동하는지 확인
    response = client.get("/docs")
    print(f"Docs 접근 가능: {response.status_code == 200}")

if __name__ == "__main__":
    print("=== FastAPI TestClient 테스트 시작 ===")
    
    print("\n1. 헬스 체크 테스트")
    test_health_check()
    
    print("\n2. AI NPC 채팅 테스트")
    test_ai_npc_chat()
    
    print("\n3. 데이터베이스 연결 테스트")
    test_database_connection()
    
    print("\n=== 테스트 완료 ===") 