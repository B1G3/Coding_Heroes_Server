from fastapi import FastAPI, UploadFile, File
from fastapi import WebSocket
from pydantic import BaseModel

app = FastAPI()

import logging
import asyncio
import base64
import uuid

import llm_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

from stt import STT
from tts import TTS

import tts

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
    status: str

class TTSResponse(BaseModel):
    audio: str  # base64 인코딩된 오디오 데이터
    format: str
    status: str

class ChatbotResponse(BaseModel):
    answer: str
    audio: str  # base64 인코딩된 오디오 데이터
    format: str
    status: str


@app.post("/stt", response_model=STTResponse)
async def speech_to_text(audio_file: UploadFile = File(...)):
    """
    음성을 텍스트로 변환하는 API (WAV 파일 업로드)
    """
    try:
        audio_data = await audio_file.read()
        stt_text = stt.run(audio_data)
        
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


        

@app.post("/qa_chatbot", response_model=ChatbotResponse)
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
        tts_audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return ChatbotResponse(
            answer=answer_text,
            audio=tts_audio_b64,
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
    

# @app.post("/qa_chatbot", response_model=ChatbotResponse)
# async def qa_chatbot(req: TextRequest):
#     """
#     텍스트 질문에 대한 LLM 답변 생성 API
#     """
#     try:
#         # LLM을 통한 답변 생성
#         answer_text = llm_handler.answer(req.text)
        
#         return ChatbotResponse(
#             answer=answer_text,
#             status="success"
#         )
        
#     except Exception as e:
#         logging.error(f"LLM 처리 중 오류 발생: {str(e)}")
#         return ChatbotResponse(
#             answer=f"오류 발생: {str(e)}",
#             status="error"
#         )


# @app.post("/tts", response_model=TTSResponse)
# async def text_to_speech(req: TextRequest):
#     """
#     텍스트를 음성으로 변환하는 API
#     """
#     try:
#         # TTS 처리
#         wav_bytes = text_to_audio(req.text)
        
#         # base64 인코딩
#         tts_audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")
        
#         return TTSResponse(
#             audio=tts_audio_b64,
#             format="wav",
#             status="success"
#         )
        
#     except Exception as e:
#         logging.error(f"TTS 처리 중 오류 발생: {str(e)}")
#         return TTSResponse(
#             audio="",
#             format="mp3",
#             status=f"error: {str(e)}"
#         )





# """
# 질문(음성)에 대한 응답(텍스트)
# """

# # WebSocket API
# @app.websocket("/ws/qa-chatbot")
# async def qa_chatbot(websocket: WebSocket):
#     await websocket.accept()
#     logging.info("WebSocket 연결됨")

#     try:
#         session_id = str(uuid.uuid4())
#         audio_data = await websocket.receive_bytes()
        
#         # 1. STT 처리
#         stt_text = process_audio_to_text(audio_data)

#         # 2. LLM 답변 및 TTS를 비동기로 처리
#         async def llm_and_tts():
#             llm_full_response = None
#             try:
#                 llm_full_response = await asyncio.to_thread(answer, stt_text)
#                 await websocket.send_json({
#                     "type": "llm_response",
#                     "session_id": session_id,
#                     "text": llm_full_response
#                 })
#             except Exception as e:
#                 await websocket.send_json({
#                     "type": "llm_response",
#                     "session_id": session_id,
#                     "error": str(e)
#                 })
#                 return
#             # LLM 끝나면 TTS를 또 비동기로
#             async def tts_task():
#                 try:
#                     llm_full_response = "나는 AI 천재로봇 렉시야"
#                     tts_audio_generator = await text_to_speech(llm_full_response)
                    
#                     # generator를 bytes로 변환
#                     tts_audio_bytes = b''
#                     for chunk in tts_audio_generator:
#                         tts_audio_bytes += chunk
                    
#                     # base64 인코딩
#                     tts_audio_b64 = base64.b64encode(tts_audio_bytes).decode("utf-8")
                    
#                     await websocket.send_json({
#                         "type": "tts_audio",
#                         "session_id": session_id,
#                         "audio": tts_audio_b64,
#                         "format": "mp3"
#                     })
#                     logging.info(f"TTS 음성 전송 완료 (MP3 형식)")

#                 except Exception as e:
#                     await websocket.send_json({
#                         "type": "tts_audio",
#                         "session_id": session_id,
#                         "error": str(e)
#                     })
#             asyncio.create_task(tts_task())

#         # LLM+TTS 태스크를 비동기로 시작
#         asyncio.create_task(llm_and_tts())

#         # STT 결과를 클라이언트에 전송 (이건 await)
#         await websocket.send_json({
#             "type": "stt_result",
#             "session_id": session_id,
#             "text": stt_text
#         })

#     except Exception as e:
#         logging.error(f"처리 중 오류 발생: {str(e)}")
#         await websocket.send_json({
#             "type": "error",
#             "session_id": session_id if 'session_id' in locals() else None,
#             "error": str(e)
#         })
#     finally:
#         logging.info("WebSocket 연결 종료")











# """
# 블록 코딩한거 피드백 API
# """
# class BlockData(BaseModel):
#     execute: list
#     custom_class: list

# @app.post("/block")
# async def block_feedback(data: BlockData):
#     input_dict = {
#         "execute": data.execute,
#         "custom_class": data.custom_class
#     }

#     # 외부 LLM 처리 함수 호출
#     response_text = analyze_code(input_dict)

#     return {
#         "feedback_result": response_text
#     }