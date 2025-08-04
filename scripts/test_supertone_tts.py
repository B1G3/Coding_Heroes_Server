import requests
from dotenv import load_dotenv
load_dotenv()
import os

supertone_api_key = os.getenv("SUPERTON_API_KEY")
url = "https://supertoneapi.com/v1/text-to-speech/400c24c9a2718734a5b404"

payload = {
    "text": "게임에 대해 잘 질문하려면, 스테이지 목표와 규칙을 먼저 이해하는 게 중요해!",
    "language": "ko",
    "style": "Neutral",
    "model": "sona_speech_1",
    "output_format": "wav",
    "voice_settings": {
        "speed": 1.2,
        "pitch_shift": 2,
        "pitch_variance": 1.1
    },
}
headers = {
    "x-sup-api-key": supertone_api_key,
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")

if response.status_code == 200:
    # WAV 파일 데이터
    audio_data = response.content
    print(f"Audio data size: {len(audio_data)} bytes")
    
    # X-Audio-Length 헤더 확인
    audio_length = response.headers.get('X-Audio-Length')
    if audio_length:
        print(f"Audio duration: {audio_length} seconds")
    
    # 파일로 저장
    with open("test_output.wav", "wb") as f:
        f.write(audio_data)
    print("✅ WAV 파일이 test_output.wav로 저장되었습니다.")
    
else:
    # 오류 응답
    print(f"Error: {response.text}")