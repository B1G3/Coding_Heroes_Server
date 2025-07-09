from fastapi import APIRouter
from fastapi import UploadFile, File

from pydantic import BaseModel
import core.llm_handler as llm_handler

from core.stt import STT
from core.tts import TTS

import os
import logging
import base64

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

router = APIRouter()
stt = STT(parameters={})
stt.load_model()
tts = TTS()

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


@router.post("/stt", response_model=STTResponse)
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    음성을 텍스트로 변환하는 API (WAV 파일 업로드)
    """
    try:
        audio_data = await audio_file.read()
        stt_text = await stt.run(audio_data)
        
        return STTResponse(
            stt_result=stt_text,
            status="success"
        )
        
    except Exception as e:
        logging.error(f"STT 처리 중 오류 발생: {str(e)}")
        return STTResponse(
            stt_result="",
            status=f"error: {str(e)}"
        )


@router.post("/qa_chatbot", response_model=ChatbotResponse)
async def qa_chatbot(req: TextRequest):
    """
    텍스트 질문에 대한 LLM 답변 생성 후, 답변을 TTS로 변환하여 오디오와 함께 반환하는 API
    """
    try:
        # 1. LLM을 통한 답변 생성
        answer_text = llm_handler.answer(req.text)

        # 2. TTS 처리 (LLM 답변을 음성으로 변환)
        audio = tts.run(answer_text, "pcm_16000")
        audio_bytes = b''.join(audio)
        b64_data = base64.b64encode(audio_bytes).decode("utf-8")

        from datetime import datetime
        output_dir = "./outputs"
        os.makedirs(output_dir, exist_ok=True)  # 디렉토리 없으면 생성

        timestamp = datetime.now().strftime("%m%d_%H%M")
        filename = os.path.join(output_dir, f"audio_{timestamp}.wav")

        save_pcm_as_wav(audio_bytes, filename)

        return ChatbotResponse(
            answer=answer_text,
            audio=b64_data,
            format="wav",
            status="success"
        )
    
    except Exception as e:
        logging.error(f"qa_chatbot_tts 처리 중 오류 발생: {str(e)}")
        return ChatbotResponse(
            answer="",
            audio="",
            format="wav",
            status=f"오류 발생: {str(e)}"
        )

import wave
def save_pcm_as_wav(pcm_data: bytes, filename: str, sample_rate=16000):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)         # mono
        wav_file.setsampwidth(2)         # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)   # write raw PCM data

    print(f"저장 완료: {filename}")




# llm 응답 테스트 api
@router.post("/llm-response-test")
async def qa_chatbot(req: TextRequest):
    return llm_handler.answer(req.text)
    
