from fastapi import FastAPI, UploadFile, File
from fastapi import WebSocket
from pydantic import BaseModel

from llm_handler import analyze_code

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()


class CodeExecutionData(BaseModel):
    execute: list
    custom_class: list


@app.post("/debug")
async def debug(data: CodeExecutionData):


    input_dict = {
        "execute": data.execute,
        "custom_class": data.custom_class
    }

    # 외부 LLM 처리 함수 호출
    response_text = analyze_code(input_dict)

    return {
        "feedback_result": response_text
    }



import whisper
import numpy as np
import soundfile as sf
import io
import librosa

# stt 모델 
model = whisper.load_model("turbo")


# 한 번에 오디오 데이터를 받아서 STT 처리
@app.websocket("/ws/qa-chatbot")
async def qa_chatbot(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket 연결됨")

    try:
        # 한 번에 모든 오디오 데이터 받기
        audio_data = await websocket.receive_bytes()
        
        # numpy 배열로 변환 
        audio_array = np.frombuffer(audio_data, dtype=np.float32)

        # 44100Hz에서 16000Hz로 리샘플링
        original_sr = 44100
        target_sr = 16000
        
        audio_resampled = librosa.resample(
            y=audio_array, 
            orig_sr=original_sr, 
            target_sr=target_sr
        )

        # STT 처리 (리샘플링된 데이터 사용)
        result = model.transcribe(audio_resampled, language="ko")
        result_text = result['text']
        logging.info(f"STT 결과: {result_text}")

        # 결과 전송
        await websocket.send_text(result_text)
        logging.debug("STT 결과 전송 완료")

    except Exception as e:
        logging.error(f"STT 처리 중 오류 발생: {str(e)}")
        await websocket.send_text(f"오류 발생: {str(e)}")
    
    finally:
        logging.info("WebSocket 연결 종료")



@app.post("/ai-feedback")
async def get_feedback(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    # Whisper는 numpy array 또는 파일 경로를 입력으로 받음
    with open("temp.wav", "wb") as f:
        f.write(audio_bytes)
    result = model.transcribe("temp.wav")
    return {"text": result["text"]}

