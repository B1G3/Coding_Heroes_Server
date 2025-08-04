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



# stt
async def speech_to_text(audio_file: UploadFile):
    try:
        await audio_file.seek(0)  
        audio_data = await audio_file.read()
        
        result = await stt.run(audio_data)
        return result

    except Exception as e:
        logging.error(f"STT 처리 중 오류 발생: {str(e)}")
        raise



# llm 응답
def get_ai_response(question: str, user_id: str, conversation_id: str):
    return chat(user_question=question, 
                user_id=user_id, 
                conversation_id=conversation_id)


# tts
async def text_to_speech(text: str):
    try:
        # 2. TTS 처리 (LLM 답변을 음성으로 변환)
        audio = tts.run(text, "pcm_16000")
        audio_bytes = b''.join(audio)
        b64_data = base64.b64encode(audio_bytes).decode("utf-8")

        # output 디렉토리에 저장 (나중에 주석처리하기)
        output_dir = "./outputs"
        os.makedirs(output_dir, exist_ok=True)  # 디렉토리 없으면 생성

        timestamp = datetime.now().strftime("%m%d_%H%M")
        filename = os.path.join(output_dir, f"audio_{timestamp}.wav")

        save_pcm_as_wav(audio_bytes, filename)


        return b64_data
    
    except Exception as e:
        logging.error(f"qa_chatbot_tts 처리 중 오류 발생: {str(e)}")
        raise


import wave
def save_pcm_as_wav(pcm_data: bytes, filename: str, sample_rate=16000):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)         # mono
        wav_file.setsampwidth(2)         # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)   # write raw PCM data

    print(f"저장 완료: {filename}")
