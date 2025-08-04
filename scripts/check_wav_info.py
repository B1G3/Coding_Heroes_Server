#!/usr/bin/env python3
"""
WAV 파일 정보 확인 스크립트
"""

import wave
import os
from pathlib import Path


if __name__ == "__main__":
    """WAV 파일의 정보를 출력"""
    try:
        with wave.open("outputs/audio_0804_2059.wav", 'rb') as wav_file:
            # 기본 정보
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            frame_rate = wav_file.getframerate()
            frames = wav_file.getnframes()
            
            # 재생 시간 계산
            duration = frames / frame_rate
            
            print(f"🎵 채널 수: {channels}")
            print(f"🔢 샘플링 레이트: {frame_rate} Hz")
            print(f"📏 샘플 크기: {sample_width * 8} bit")
            print(f"⏱️  재생 시간: {duration:.2f}초")
            print(f"📊 프레임 수: {frames}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ 오류: {e}")