import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import logging

load_dotenv() 

class TTS:
  def __init__(self):
    self.elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY")) 
    self.logger = logging.getLogger(self.__class__.__name__)

  def run(self, text: str, output_format: str):
    try:
      audio = self.elevenlabs.text_to_speech.convert(
          text=text,
          voice_id="GhEYxuQNnQe2oNejkNYs",
          # model_id="eleven_turbo_v2_5",
          model_id="eleven_multilingual_v2",
          output_format=output_format,
          language_code=None,
          seed=10000,
          # voice_settings={
          #   "speed": 0.9,
          #   "stability": 0.8,
          #   "use_speaker_boost": False,
          #   "similarity_boost": 0.7,
          #   "style": 0.1
          # }
          voice_settings={
            "speed": 0.95,
            "stability": 0.9,
            "use_speaker_boost": False,
            "similarity_boost": 1.0,
            "style": 0.3
          }
      )
      return audio

    except Exception as e:
      self.logger.error(f"TTS 변환 중 오류 발생: {str(e)}")
      raise

