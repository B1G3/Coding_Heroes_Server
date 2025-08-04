import whisper
import numpy as np
import librosa
import soundfile
import logging
import io

class STT:
    def __init__(self, parameters):
        self.parameters = parameters
        self.model = None
        self.logger = logging.getLogger(self.__class__.__name__)

    # Whisper 모델을 불러오는 함수
    def load_model(self):
        try:
            whisper_model_size = "large-v3-turbo"
            download_root = "models/whisper"
            self.model = whisper.load_model(
                whisper_model_size, 
                device="cuda",
                download_root=download_root
            )
            self.logger.info(f"Whisper 모델 로드")
        except Exception as e:
            self.logger.error(f"Whisper 모델 로드 실패: {e}")
            raise

    # 오디오 bytes 데이터를 받아서 텍스트로 반환하는 함수
    async def run(self, audio_data: bytes) -> str:
        if not self.model:
            self.load_model()
        
        try:
            audio_file = io.BytesIO(audio_data)

            # wav 파일을 numpy 배열로 읽어오기
            audio_array, sample_rate = soundfile.read(audio_file)

            # 샘플링 레이트가 16000이 아니라면 변환
            if sample_rate != 16000:
                audio_array = librosa.resample(
                    y=audio_array,
                    orig_sr=sample_rate,
                    target_sr=16000
                )
                self.logger.info(f"샘플링 레이트 변환: {sample_rate} -> 16000Hz")

            # Whisper 모델로 STT 처리
            result = self.model.transcribe(
                audio_array.astype(np.float32), 
                language='ko',
                temperature=0.0,  # 결정적 출력 (0.0 = 가장 정확)
                compression_ratio_threshold=2.4,  # 압축 비율 임계값
                logprob_threshold=-1.0,  # 로그 확률 임계값
                no_speech_threshold=0.6,  # 무음 임계값
                condition_on_previous_text=False,  # 이전 텍스트 조건 없음
                initial_prompt=None  # 초기 프롬프트 없음
            )
            result_text = result["text"]
            self.logger.info(f"STT 결과: {result_text}")
            
            return result_text
        
        except Exception as e:
            self.logger.error(f"STT 처리 중 오류 발생: {e}")
            return ""
