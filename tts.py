import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import logging


class TTS:
  def __init__(self):
    load_dotenv()
    self.elevenlabs = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY")) 
    self.logger = logging.getLogger(self.__class__.__name__)

  def run(self, output_format):
    try:
      audio = self.elevenlabs.text_to_speech.convert(
          text=text,
          voice_id="BZWuZ6lPLVdYkSXTgt0Y",
          model_id="eleven_turbo_v2_5",
          output_format=output_format,
          language_code="ko",
          seed=10000,
          voice_settings={
            "speed": 0.9,
            "stability": 0.8,
            "use_speaker_boost": False,
            "similarity_boost": 0.7,
            "style": 0.1
          }
      )
      return audio

    except Exception as e:
      self.logger.error(f"TTS 변환 중 오류 발생: {str(e)}")
      raise

