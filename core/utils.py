import os
import logging
logger = logging.getLogger(__name__)
from datetime import datetime
from fastapi import UploadFile

async def save_uploaded_audio(audio_file: UploadFile, prefix: str = "uploaded") -> str:
    """
    업로드된 음성파일을 임시 저장하는 함수
    
    Args:
        audio_file: 업로드된 음성파일
        prefix: 파일명 접두사
    
    Returns:
        str: 저장된 파일 경로
    """
    try:
        # 임시 디렉토리 생성
        temp_dir = "./temp_audio"
        os.makedirs(temp_dir, exist_ok=True)
        
        # 파일명 생성 (타임스탬프 포함)
        timestamp = datetime.now().strftime("%m%d_%H%M%S")
        filename = f"{prefix}_audio_{timestamp}.wav"
        file_path = os.path.join(temp_dir, filename)

        # 파일 내용 읽기
        await audio_file.seek(0)  # 파일 포인터를 처음으로 되돌림
        audio_content = await audio_file.read()

        # 파일 저장
        with open(file_path, "wb") as f:
            f.write(audio_content)
        
        logger.info(f"음성파일 저장 완료: {file_path}")
        
    except Exception as e:
        logger.error(f"음성파일 저장 중 오류: {str(e)}")
        raise