import os
import requests
import logging
from dotenv import load_dotenv
from enum import Enum
from config import OUTPUT_DIR
from datetime import datetime
import asyncio


load_dotenv()

class VoiceStyle(str, Enum):
    ANGRY = "Angry"
    EMBARRASSED = "Embarrassed"
    FRIENDLY = "Friendly"
    HAPPY = "Happy"
    SAD = "Sad"
    NEUTRAL = "Neutral"

class TTS:
    def __init__(self):
      self.api_key = os.getenv("SUPERTON_API_KEY")
      self.base_url = "https://supertoneapi.com/v1/text-to-speech"
      self.voice_id = "400c24c9a2718734a5b404"
      self.logger = logging.getLogger(self.__class__.__name__)

    async def run(self, text: str, style: VoiceStyle = VoiceStyle.NEUTRAL, output_format: str = "wav"):
        url = f"{self.base_url}/{self.voice_id}?output_format={output_format}"
        headers = {
            "x-sup-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "language": "ko",
            "style": style.value,
            "model": "sona_speech_1",
            "voice_settings": {
                "speed": 1.2,
                "pitch_shift": 2,
                "pitch_variance": 1.1
            },
        }
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                await asyncio.create_task(self.save_output_file(response.content))
                return response.content  # wav 바이너리
            else:
                self.logger.error(f"Superton API 오류: {response.status_code} - {response.text}")
                raise Exception(f"Superton API 오류: {response.status_code} - {response.text}")
        except Exception as e:
            self.logger.error(f"TTS 변환 중 오류 발생: {str(e)}")
            raise

    async def save_output_file(self, audio_data):
        timestamp = datetime.now().strftime("%m%d_%H%M")
        filename = os.path.join(OUTPUT_DIR, f"audio_{timestamp}.wav")

        with open(filename, "wb") as f:
            f.write(audio_data)
        print("✅ WAV 파일이 test_output.wav로 저장되었습니다.")
        

        

