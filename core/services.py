import logging 
import base64
import os
from datetime import datetime

from fastapi import UploadFile

from core.llm_handler import chat

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


async def text_to_speech(text: str):
    try:
        audio_content = await tts.run(text)
        b64_data = base64.b64encode(audio_content).decode("utf-8")

        return b64_data
    
    except Exception as e:
        logging.error(f"qa_chatbot_tts 처리 중 오류 발생: {str(e)}")
        raise


    
# llm 응답
def get_ai_response(question: str, user_id: str, conversation_id: str):
    return chat(user_question=question, 
                user_id=user_id, 
                conversation_id=conversation_id)
