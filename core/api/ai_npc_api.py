import logging
import uuid
import os
import json
from dotenv import load_dotenv

from fastapi import APIRouter, UploadFile, File, WebSocket, Header
from pydantic import BaseModel
from typing import Literal, Any, Optional

from core.services import speech_to_text, text_to_speech
from core.llm_handler import get_ai_response
from core.utils import save_uploaded_audio

# === DB repos ===
from core.database_client.supabase_client import get_supabase
from core.repositories.questions import QuestionsRepo
from core.repositories.execution_logs import ExecutionLogsRepo

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter()


# ----------------- Helpers -----------------
def _resolve_client_id(x_client_id: Optional[str]) -> uuid.UUID:
    """X-Client-Id 헤더 또는 환경변수 DEFAULT_CLIENT_ID에서 client_id를 결정"""
    cid = x_client_id or os.environ.get("DEFAULT_CLIENT_ID")
    if not cid:
        raise ValueError("client_id가 없습니다. X-Client-Id 헤더나 DEFAULT_CLIENT_ID 환경변수를 설정하세요.")
    try:
        return uuid.UUID(cid)
    except Exception:
        raise ValueError("client_id 형식이 올바르지 않습니다(UUID 필요).")

def _questions_repo() -> QuestionsRepo:
    return QuestionsRepo(get_supabase())

def _exec_logs_repo() -> ExecutionLogsRepo:
    return ExecutionLogsRepo(get_supabase())


# ----------------- Schemas -----------------
class TextRequest(BaseModel):
    text: str
    stage: Literal["learn", "boss"]

class STTResponse(BaseModel):
    stt_result: str
    status: str

class ChatbotResponse(BaseModel):
    answer: str
    audio: str  # base64 인코딩된 오디오 데이터
    format: str
    status: str


# ----------------- STT -----------------
@router.post("/stt", response_model=STTResponse)
async def stt(audio_file: UploadFile = File(...)):
    """
    음성을 텍스트로 변환하는 API (WAV 파일 업로드)
    
    요구사항:
    - 파일 형식: WAV
    - 샘플링 레이트: 16000Hz (권장)
    - 비트 깊이: 16-bit
    - 채널: Mono (1채널)
    """
    try:
        logger.info(f"audio_file: {audio_file}")

        # 파일 형식 검증
        if audio_file.content_type != 'audio/wav':
            return STTResponse(
                stt_result = "",
                status="error: WAV 파일만 지원됩니다."
        )

        # 1. 음성파일 임시 저장 (디버깅용)
        saved_file_path = await save_uploaded_audio(audio_file, prefix="stt")
        
        # 2. STT 처리
        text = await speech_to_text(audio_file)
        logger.info(f"tts result: {text}")

        return STTResponse(
            stt_result=text,
            status="success"
        )
        
    except Exception as e:
        return STTResponse(
            stt_result="",
            status=f"error: {str(e)}"
        )



# ----------------- QA + TTS -----------------
@router.post("/qa_chatbot", response_model=ChatbotResponse)
async def qa_chatbot(req: TextRequest, 
                     x_client_id: Optional[str] = Header(default=None, convert_underscores=False)):
    """
    텍스트 질문에 대한 LLM 답변 생성 후, 답변을 TTS로 변환하여 오디오와 함께 반환하는 API
    """
    try:
        client_uuid = _resolve_client_id(x_client_id)
        _questions_repo().save(client_id=client_uuid, stage=req.stage, question=req.text)
    except Exception as e:
        logger.exception("❌ Error saving question")

    try:
        # 1) LLM 답변 생성
        resp_str = get_ai_response(question=req.text, stage=req.stage, client_id=client_uuid)
        logger.info(f"AI RESPONSE: {resp_str}")

        # 2) TTS
        b64_data = await text_to_speech(resp_str)

        return ChatbotResponse(
            answer=resp_str,
            audio=b64_data,
            format="wav",
            status="success"
        )
    
    except Exception as e:
        return ChatbotResponse(
            answer="",
            audio="",
            format="wav",
            status=f"오류 발생: {str(e)}"
        )



# ----------------- LLM 응답 테스트 -----------------
@router.post("/llm-response-test")
async def llm_response_test(req: TextRequest, 
                            x_client_id: Optional[str] = Header(default=None, convert_underscores=False)):
    try:
        client_uuid = _resolve_client_id(x_client_id)
        _questions_repo().save(client_id=client_uuid, stage=req.stage, question=req.text)
    except Exception as e:
        logger.exception("❌ Error saving question (test)")

    try:
        resp_str = get_ai_response(question=req.text, stage=req.stage, client_id=client_uuid)
        logger.info(f"AI RESPONSE: {resp_str}")
        return resp_str
    
    except Exception as e:
        logger.exception("❌ Error running get_ai_response")
        return {"status": f"LLM 오류 발생: {str(e)}"}
    

# ----------------- TTS 테스트 -----------------
@router.post("/tts-test")
async def tts(req: TextRequest):
    """
    (테스트용) text to speech
    """
    return await text_to_speech(req.text)
    

# ----------------- 실행 로그 -----------------
class CodingResult(BaseModel):
    stage: str
    # 문자열 JSON 또는 dict 모두 허용될 수 있으므로 Any로 받아 파싱
    block_json: Any

@router.post("/execution_log")
async def execution_log(request: CodingResult, 
                        x_client_id: Optional[str] = Header(default=None, convert_underscores=False)):
    try:
        client_uuid = _resolve_client_id(x_client_id)

        # block_json이 문자열이면 JSON 파싱 시도
        block_payload = request.block_json
        if isinstance(block_payload, str):
            try:
                block_payload = json.loads(block_payload)
            except Exception:
                # 파싱 실패해도 원문 문자열로 저장
                pass

        _exec_logs_repo().save(
            client_id=client_uuid,
            stage=request.stage,
            block_json=block_payload if isinstance(block_payload, dict) else {"raw": block_payload},
        )
        return {"status": "success"}
    except Exception as e:
        logger.exception("❌ Error saving execution log")
        print(f"❌ Error saving execution log: {e}")
        return {"status": f"오류 발생: {str(e)}"}