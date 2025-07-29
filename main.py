import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.ai_npc_api import router as ai_npc_router
from core.database import init_db
from core.llm_handler import initialize_chain

"""
로깅 시스템의 전체적인 설정(글로벌 설정)
로그 레벨, 출력 포맷, 파일 저장 위치 등을 한번에 지정
보통 프로그램의 진입점에서 한번만 호출한다.
이 설정은 전체 애플리케이션에 적용된다.
"""
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

"""
FastAPI 앱 인스턴스 생성
: app은 FastAPI 애플리케이션의 매인 객체
uvicorn이 main:app에서 app 객체를 찾아 서버를 시작한다.  
"""
# FastAPI 앱 생성
app = FastAPI(  
    title="Coding Heroes",
    description="API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

"""
@app.on_event("startup")
FastAPI의 이벤트 핸들러 데코레이터
- FastAPI 앱이 시작될 때 자동으로 실행되는 함수를 정의한다.
- 앱이 완전히 시작되기 전 필요한 초기화 작업을 수행한다.

"startup": 앱 시작 시
"shutdown": 앱 종료 시
"""

# 앱 시작 시 데이터베이스 초기화 및 chain 초기화
@app.on_event("startup")
async def startup_event():
    # 데이터베이스 초기화
    init_db()
    
    # LLM chain 초기화
    try:
        initialize_chain()
        logging.info("LLM chain 초기화 완료")
    except Exception as e:
        logging.error(f"LLM chain 초기화 실패: {e}")
        raise e
    

# 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(ai_npc_router, prefix="/ai_npc")
