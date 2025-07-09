from tts import TTS
import wave 
import datetime


def save_pcm_as_wav(pcm_data: bytes, filename: str, sample_rate=16000):
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)         # mono
        wav_file.setsampwidth(2)         # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(pcm_data)   # write raw PCM data


def main():
    print("== TTS 프로그램 시작 ==")
    text = input("변환할 문장을 입력하세요: ")

    tts = TTS()
    audio = tts.run(text, "pcm_16000")
    audio_bytes = b''.join(audio)

    from datetime import datetime
    timestamp = datetime.now().strftime("%m%d_%H%M")
    filename = f"sample_audio_{timestamp}.wav"

    save_pcm_as_wav(audio_bytes, filename)
    print(f"파일 저장 완료: {filename}")

    input("엔터를 눌러 종료합니다.")

if __name__ == "__main__":
    main()