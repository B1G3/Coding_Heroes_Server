import logging
logger = logging.getLogger(__name__)
import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, WebSocket
from pydantic import BaseModel


router = APIRouter()

class TextRequest(BaseModel):
    text: str

class STTResponse(BaseModel):
    stt_result: str
    status: str

class ChatbotResponse(BaseModel):
    answer: str
    audio: str  # base64 인코딩된 오디오 데이터
    format: str
    status: str


from core.services import speech_to_text
from core.utils import save_uploaded_audio

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

# # WebSocket을 통한 STT 스트리밍
# @router.websocket("/stt_stream")
# async def stt_stream(websocket: WebSocket):
#     """
#     WebSocket을 통한 실시간 STT 스트리밍 API
#     """
#     from core.stt_stream import STTStream
    
#     stt_stream = STTStream()
#     await stt_stream.process_audio_stream(websocket, None)


TEMP_USER_ID = "u001"
TEMP_CONV_ID = "s001"

from core.services import get_ai_response, text_to_speech

@router.post("/qa_chatbot", response_model=ChatbotResponse)
async def qa_chatbot(req: TextRequest):
    """
    텍스트 질문에 대한 LLM 답변 생성 후, 답변을 TTS로 변환하여 오디오와 함께 반환하는 API
    """
    try:
        # 1. LLM을 통한 답변 생성
        text_data = get_ai_response(req.text, TEMP_USER_ID, TEMP_CONV_ID)
        logger.info(f"ai_response: {text_data}")

        # # 2. TTS 처리 (LLM 답변을 음성으로 변환)
        b64_data = await text_to_speech(text_data)

        return ChatbotResponse(
            answer=text_data,
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

# ----------------------------- test용 api ---------------------------- #

# llm 응답 테스트 api
@router.post("/llm-response-test")
async def llm_response_test(req: TextRequest):
    """
    (테스트용) 텍스트 질문에 대한 LLM 답변 생성하여 텍스트만 반환하는 API
    """
    return get_ai_response(req.text, TEMP_USER_ID, TEMP_CONV_ID)
    

# tts 테스트 api
@router.post("/tts-test")
async def tts(req: TextRequest):
    """
    (테스트용) text to speech
    """
    return await text_to_speech(req.text)
    



# ------------------------ 플레이 기록 -------------------------------
from core.database import save_playrecord

class CodingResult(BaseModel):
    stage: str
    json_str: str

@router.post("/playrecord")
async def block_coding(request: CodingResult):
    # DB 저장
    try:
        save_playrecord(TEMP_USER_ID, request.stage, request.json_str)
        return {"status": "success"}

    except Exception as e:
        return {"status": f"오류 발생: {str(e)}"}
