from fastapi import FastAPI, UploadFile, File
from fastapi import WebSocket
from pydantic import BaseModel

from llm_handler import analyze_code, answer, answer_stream

import logging
import asyncio
import whisper
import numpy as np
import soundfile as sf
import io
import librosa
import base64
import uuid

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


@app.post("/block")
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


# (가상) TTS 함수 - 실제 구현 대신 예시용
async def fake_tts(text: str) -> bytes:
    await asyncio.sleep(0.5)  # TTS 처리 시간 시뮬레이션
    return b"FAKE_TTS_AUDIO_DATA"  # 실제로는 생성된 음성 데이터 반환


# 새로운 멀티모달 WebSocket API
@app.websocket("/ws/qa-multimodal")
async def qa_multimodal(websocket: WebSocket):
    await websocket.accept()
    logging.info("WebSocket 연결됨")

    try:
        session_id = str(uuid.uuid4())
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
        # 1. STT 처리 및 텍스트 응답
        result = model.transcribe(audio_resampled, language="ko")
        stt_text = result['text']
        logging.info(f"STT 결과: {stt_text}")

        # 2. LLM 답변 및 TTS를 비동기로 처리
        async def llm_and_tts():
            llm_full_response = None
            try:
                llm_full_response = await asyncio.to_thread(answer, stt_text)
                await websocket.send_json({
                    "type": "llm_response",
                    "session_id": session_id,
                    "text": llm_full_response
                })
            except Exception as e:
                await websocket.send_json({
                    "type": "llm_response",
                    "session_id": session_id,
                    "error": str(e)
                })
                return
            # LLM 끝나면 TTS를 또 비동기로
            async def tts_task():
                try:
                    tts_audio = await fake_tts(llm_full_response)
                    tts_audio_b64 = base64.b64encode(tts_audio).decode("utf-8")
                    await websocket.send_json({
                        "type": "tts_audio",
                        "session_id": session_id,
                        "audio": tts_audio_b64
                    })
                    logging.info(f"TTS 음성 전송 완료")
                except Exception as e:
                    await websocket.send_json({
                        "type": "tts_audio",
                        "session_id": session_id,
                        "error": str(e)
                    })
            asyncio.create_task(tts_task())

        # LLM+TTS 태스크를 비동기로 시작
        asyncio.create_task(llm_and_tts())

        # STT 결과를 클라이언트에 전송 (이건 await)
        await websocket.send_json({
            "type": "stt_result",
            "session_id": session_id,
            "text": stt_text
        })

    except Exception as e:
        logging.error(f"처리 중 오류 발생: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "session_id": session_id if 'session_id' in locals() else None,
            "error": str(e)
        })
    finally:
        logging.info("WebSocket 연결 종료")









