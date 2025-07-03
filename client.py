import asyncio
import websockets
import sounddevice as sd
import numpy as np
import soundfile as sf
import time

import matplotlib.pyplot as plt



async def send_audio_file():
    uri = "ws://localhost:8000/ws/qa-chatbot"

    # WAV 파일에서 오디오 데이터만 추출 (PCM 데이터)
    data, samplerate = sf.read('test.wav', dtype='float32')

    
    # numpy 배열을 바이트로 변환
    audio_bytes = data.tobytes()

    async with websockets.connect(uri) as ws:
        print("WebSocket 연결됨")
        print(f"오디오 데이터 크기: {len(audio_bytes)} 바이트")
        print(f"샘플레이트: {samplerate}")

        # PCM 데이터 전송
        await ws.send(audio_bytes)
        print("PCM 데이터 전송 완료")

        # 스트리밍 응답 수신
        print("🤖 AI 응답:")
        full_response = ""
        
        while True:
            try:
                # 각 청크를 개별적으로 수신
                chunk = await asyncio.wait_for(ws.recv(), timeout=10)
                full_response += chunk
                print(chunk, end="", flush=True)  # 실시간 타이핑 효과
            except asyncio.TimeoutError:
                print("\n✅ 스트리밍 완료")
                break
            except websockets.exceptions.ConnectionClosed:
                print("\n🔌 연결 종료")
                break
        
        print(f"\n📝 전체 응답 길이: {len(full_response)}자")


# 파일이 존재하는지 확인하는 함수 추가
async def send_audio_file_safe():
    try:
        await send_audio_file()
    except FileNotFoundError:
        print("test.wav 파일을 찾을 수 없습니다.")
        print("먼저 record_and_send() 함수로 녹음을 진행하거나 test.wav 파일을 준비해주세요.")
    except Exception as e:
        print(f"오류 발생: {e}")
        

asyncio.run(send_audio_file_safe())


# # print(sd.query_devices()) # 사용 가능한 장치 목록 출력
# mic_info = sd.query_devices(1)
# # print("지원 샘플레이트: ", mic_info["default_samplerate"])

# async def record_and_send():
#     uri = "ws://localhost:8000/ws/qa-chatbot"
    

#     async with websockets.connect(uri) as ws: # 웹소켓 서버에 연결된동안
#         print("Connected to Websocket")

#         samplerate = 44100.0 # 샘플레이트:: 초당 몇개의 샘풀을 추출할지. 높을 수록 원음에 가까운 음질이고 용량 증가 
#         duration = 3 # 1초 단위로 음성 데이터를 자름 

#         i = 0
#         while True: # 음성 전송 게속 반복
#             print("Recording...")
#             recording = sd.rec(
#                 int(samplerate * duration), # 샘플 수 = 샘플레이트 x 시간
#                 samplerate=samplerate, 
#                 channels=1, 
#                 dtype="float32",
#                 device=1
#             )
#             plt.plot(recording)
#             plt.show()
                        
#             sf.write(f"test_{i}.wav", recording, 44100)
#             i += 1
#             sd.wait() # 이건 뭐지? 잠깐 기다려? => 녹음 완료까지 블로킹

#             audio_bytes = recording.tobytes() # numpy 배열 -> byte 배열로 변환 
#             await ws.send(audio_bytes) # 전송 

#             try:
#                 response = await asyncio.wait_for(ws.recv(), timeout=5) # 응답 받는건 비동기로 5초 동안 응답안오면 타임아웃?
#                 print("STT 결과: ", response)
#             except asyncio.TimeoutError:
#                 print("응답 없음")

# # asyncio.run(record_and_send())


