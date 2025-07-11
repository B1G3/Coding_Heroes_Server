from fastapi import APIRouter
from fastapi import UploadFile, File
from pydantic import BaseModel

import logging


router = APIRouter()

"""
HTTP POST API - STT, LLM, TTS 기능 분리
"""
from fastapi import UploadFile, File

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

@router.post("/stt", response_model=STTResponse)
async def stt(audio_file: UploadFile = File(...)):
    """
    음성을 텍스트로 변환하는 API (WAV 파일 업로드)
    """
    try:
        text = await speech_to_text(audio_file)

        return STTResponse(
            stt_result=text,
            status="success"
        )
        
    except Exception as e:
        return STTResponse(
            stt_result="",
            status=f"error: {str(e)}"
        )


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
        logging.info(f"ai_response: {text_data}")

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





# llm 응답 테스트 api
@router.post("/llm-response-test")
async def qa_chatbot(req: TextRequest):
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
    
