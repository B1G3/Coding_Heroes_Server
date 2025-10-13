import logging 
import base64
import os
from datetime import datetime

from fastapi import UploadFile

from core.stt import STT
from core.tts import TTS

stt = STT(parameters={})
stt.load_model()
tts = TTS()

async def speech_to_text(audio_file: UploadFile):
    try:
        await audio_file.seek(0)  
        audio_data = await audio_file.read()
        
        result_text = await stt.run(audio_data)
        return result_text

    except Exception as e:
        logging.error(f"STT 처리 중 오류 발생: {str(e)}")
        raise



from pathlib import Path

# 폴백 WAV 경로 (윈도우 경로는 raw string으로)
FALLBACK_WAV = Path(r"C:\workspace\Coding_Heroes_Server\data\lexy_response_audio.wav")


async def text_to_speech(text: str):
    try:
        audio_content = await tts.run(text)
    
    except Exception as e:
        logging.error(f"qa_chatbot_tts 처리 중 오류 발생: {str(e)} \n -> 임시 오디오 파일로 대체합니다.")
        with open(FALLBACK_WAV, 'rb') as f:
            audio_content = f.read()
        
    b64_data = base64.b64encode(audio_content).decode("utf-8")
    return b64_data







