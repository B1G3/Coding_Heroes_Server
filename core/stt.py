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
            self.logger.info("Whisper 모델 로드 완료")
        except Exception as e:
            self.logger.error(f"모델 로딩 실패: {e}")
            raise

    # 오디오 bytes 데이터를 받아서 텍스트로 반환하는 함수 (비동기)
    async def run(self, audio_data: bytes) -> str:
        if not self.model:
            self.logger.error("Whisper 모델이 로드되지 않았습니다.")
            return ""
        
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
            result = self.model.transcribe(audio_array.astype(np.float32), language='ko')
            
            return result["text"]
        
        except Exception as e:
            self.logger.error(f"STT 처리 중 오류 발생: {e}")
            return ""
        

        
# def process_audio_to_text(audio_data: bytes) -> str:
#     """
#     오디오 데이터를 텍스트로 변환하는 함수
    
#     Args:
#         audio_data (bytes): WAV 파일 데이터
    
#     Returns:
#         str: STT 처리 결과 텍스트
#     """
#     try:
#         # WAV 파일을 numpy 배열로 로드
#         import soundfile as sf
#         import io
        
#         # bytes를 파일 객체로 변환
#         audio_file = io.BytesIO(audio_data)
        
#         # soundfile로 WAV 파일 읽기
#         audio_array, sample_rate = sf.read(audio_file)
        
#         # 16000Hz로 리샘플링 (필요한 경우)
#         if sample_rate != 16000:
#             audio_resampled = librosa.resample(
#                 y=audio_array, 
#                 orig_sr=sample_rate, 
#                 target_sr=16000
#             )
#         else:
#             audio_resampled = audio_array

#         # STT 처리
#         result = model.transcribe(audio_resampled, language="ko")
#         stt_text = result['text']
        
#         logging.info(f"STT 결과: {stt_text}")
#         return stt_text
        
#     except Exception as e:
#         logging.error(f"STT 처리 중 오류 발생: {str(e)}")
#         raise e



