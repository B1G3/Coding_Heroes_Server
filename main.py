from fastapi import FastAPI, UploadFile, File
from fastapi import WebSocket
from pydantic import BaseModel

from llm_handler import analyze_code

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()


class CodeExecutionData(BaseModel):
    execute: list
    custom_class: list


@app.post("/analyze-code/debug")
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

# stt 모델 
model = whisper.load_model("turbo")


# 실시간 음성 스트림 처리 및 텍스트 반환(x 음성 반환)
@app.websocket("/ws/qa-chatbot")
async def qa_chatbot(websocket: WebSocket):
    await websocket.accept()
    audio_chunks = []
    while True:
        data = await websocket.receive_bytes()
        audio_chunks.append(data)
        # 일정 크기 이상 모이면 처리
        if len(audio_chunks) >= 10:
            audio_data = np.frombuffer(b''.join(audio_chunks), dtype=np.float32) # 이건 뭐?
            result = model.transcribe(audio_data) # 이건 뭐?
            result_text = result['text']
            logging.debug("result_text ==> ", result_text)

            await websocket.send_text(result['text'])
            audio_chunks = []


# import soundfile as sf
# import tempfile

# if len(audio_chunks) >= 10:
#     raw_audio = b''.join(audio_chunks)
#     with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#         sf.write(tmp.name, np.frombuffer(raw_audio, dtype=np.float32), 16000)
#         result = model.transcribe(tmp.name)


# @app.post("/ai-feedback")
# async def get_feedback(file: UploadFile = File(...)):
#     audio_bytes = await file.read()
#     # Whisper는 numpy array 또는 파일 경로를 입력으로 받음
#     with open("temp.wav", "wb") as f:
#         f.write(audio_bytes)
#     result = model.transcribe("temp.wav")
#     return {"text": result["text"]}




# @app.post("/execute")
# async def execute(request: Request):
#     return


# @app.post("/question")
# async def question(request: Request):
#     return

# @app.post("/hint")
# async def hint(request: Request):
#     return 



# #  등록
# @app.post("/user")
# async def create_user(request: Request):
#     return

# # 전화번호로 가입. 
# # 선생님은 웹사이트에서 따로 가입후 학생 전화번호로 인증요청하면 관리 페이지 볼수 있음.