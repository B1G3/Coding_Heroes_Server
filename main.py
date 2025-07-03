from fastapi import FastAPI, UploadFile, File
from fastapi import WebSocket
from pydantic import BaseModel

from llm_handler import analyze_code, answer, answer_stream

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

app = FastAPI()

"""
블록 코딩한거 피드백 API
"""
class BlockData(BaseModel):
    execute: list
    custom_class: list


@app.post("/block-feedback")
async def block_feedback(data: BlockData):

    input_dict = {
        "execute": data.execute,
        "custom_class": data.custom_class
    }

    # 외부 LLM 처리 함수 호출
    response_text = analyze_code(input_dict)

    return {
        "feedback_result": response_text
    }



"""
질문(텍스트)에 대한 응답(텍스트) ==> 테스트용
"""
class TextQuestionData(BaseModel):
    question: str


@app.post("/test-text-qa")
async def test_text_qa(data: TextQuestionData):
    """
    텍스트 질문을 받아서 LLM으로 처리하고 텍스트로 응답하는 테스트용 API
    """
    try:
        logging.info(f"텍스트 질문 수신: {data.question}")
        
        # LLM을 통한 답변 생성 (비스트리밍)
        response_text = answer(data.question)
        logging.info(f"LLM 답변 생성 완료: {response_text}")
        
        return {
            "question": data.question,
            "answer": response_text,
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"텍스트 QA 처리 중 오류 발생: {str(e)}")
        return {
            "question": data.question,
            "answer": f"오류 발생: {str(e)}",
            "status": "error"
        }


"""
질문(음성)에 대한 응답(텍스트)
"""
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
        stt_text = result['text']
        logging.info(f"STT 결과: {stt_text}")

        # LLM을 통한 스트리밍 답변 생성 및 전송
        logging.info("LLM 스트리밍 답변 시작")
        full_response = ""
        
        for chunk in answer_stream(stt_text):
            full_response += chunk
            # 각 청크를 클라이언트에 전송
            await websocket.send_text(chunk)
            logging.info(f"스트림 청크 전송: {chunk}")
        
        logging.info(f"LLM 스트리밍 답변 완료: {full_response}")

    except Exception as e:
        logging.error(f"STT 처리 중 오류 발생: {str(e)}")
        await websocket.send_text(f"오류 발생: {str(e)}")
    
    finally:
        logging.info("WebSocket 연결 종료")









