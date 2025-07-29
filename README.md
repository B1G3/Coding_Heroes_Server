# Coding Heroes Server

## 프로젝트 소개

**Coding Heroes Server**는 AI 기반 블록코딩 교육 플랫폼의 백엔드 서버입니다. 
OpenAI LLM, Chroma 벡터DB, LangChain, FastAPI 등 최신 기술을 활용하여 대화형 코딩 교육, 문서 검색, 음성 인식/합성, 대화 이력 관리 기능을 제공합니다.

---

## 폴더/파일 구조 및 역할

```
Coding_Heroes_Server/
│
├── core/                # 서버 런타임 핵심 모듈
│   ├── api/             # API 엔드포인트
│   ├── database.py      # DB 연동 (SQLAlchemy)
│   ├── llm_handler.py   # LLM 체인, 대화 서비스
│   ├── models.py        # 데이터 모델
│   ├── services.py      # 서비스 계층
│   ├── stt.py           # 음성 인식
│   ├── tts.py           # 음성 합성
│   └── vector_utils.py  # 벡터스토어/임베딩/리트리버 유틸
│
├── data/                # 실제 데이터, 벡터DB, 임베딩, 문서 등
|   ├── system_prompt/   # 프롬프트 파일
│   ├── docs.md          # 검색용 문서 원본
│   ├── chroma_db/       # Chroma 벡터DB
│   └── coding-heroes.db # SQLite DB 파일
│
├── scripts/             # 서버 실행 전 1회성 스크립트
│   └── embed_docs.py    # 문서 벡터화 및 DB 저장
│
├── tests/               # 테스트 코드
├── config.py            # 환경설정 및 경로 관리
├── main.py              # 서버 실행 진입점
├── requirements.txt     # Python 패키지 목록
└── README.md            # 프로젝트 설명 (본 파일)
```

---

## 주요 기능

- **AI 대화/코딩 피드백**: OpenAI LLM 기반 대화 및 피드백
- **문서 검색**: Chroma 벡터DB + LangChain으로 문서 유사도 검색
- **대화 이력 관리**: 사용자별 대화 저장/조회
- **음성 인식/합성**: STT, TTS 기능 제공
- **API 서버**: RESTful API 제공

---

## 실행/관리 방법

### 1. 환경설정
- `.env` 파일에 OpenAI API Key, EMBEDDING_MODEL 등 환경변수 설정
- `config.py`에서 경로 자동 관리

### 2. 문서 임베딩 및 벡터DB 구축 (최초 1회)
```bash
python scripts/embed_docs.py
```
- `data/docs.md`를 벡터화하여 `data/chroma_db/`에 저장
- 문서/임베딩 모델 변경 시 재실행 필요

### 3. 서버 실행
```bash
python main.py
```

### 4. DB/데이터 관리
- 모든 데이터/DB/임베딩은 `data/` 폴더에 저장됨
- DB 파일 경로는 `config.py`에서 관리

---

## 개발/운영 팁
- **임베딩 모델**은 환경변수(`EMBEDDING_MODEL`)로 통일 관리
- **코드/데이터/스크립트**를 역할별로 분리하여 유지보수 용이
- **테스트**는 `tests/` 폴더에 작성

---

## 문의/기여
- 코드 개선, 버그 제보, 기능 제안은 이슈/PR로 남겨주세요! 