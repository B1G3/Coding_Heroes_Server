# core/analysis/analysis_llm.py
from __future__ import annotations
from typing import Dict, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_anthropic import ChatAnthropic

# 기존 llm_handler와 동일한 벤더/옵션을 사용 (필요 시 다른 파라미터)
def _model():
    return ChatAnthropic(
        model="claude-3-5-sonnet-latest",
        temperature=0,
        max_tokens=512,
        timeout=None,
        max_retries=2,
    )

# ===== 1) 질문 난이도 분류 =====
# 출력은 반드시 basic|intermediate|advanced 중 하나의 소문자 토큰만
_CLASSIFY_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "너는 교육 데이터 분석가야. 주어진 질문을 읽고 난이도를 판단해.\n"
     "출력은 반드시 소문자 토큰 하나만: basic | intermediate | advanced"),
    ("human",
     "질문: {question}\n"
     "스테이지: {stage}\n"
     "- basic: 개념 확인, 정의/규칙의 직답을 요구하는 단순 질문\n"
     "- intermediate: 규칙 응용, 두 개 이상의 개념/규칙을 연결해 설명 요구\n"
     "- advanced: 전략/설계/디버깅 등 복합적 판단과 추론이 필요한 질문\n"
     "\n"
     "정답 형식: basic 또는 intermediate 또는 advanced (기타 설명 금지)")
])

_classify_chain = _CLASSIFY_PROMPT | _model() | StrOutputParser()

def classify_question_level(question: str, stage: str) -> str:
    return _classify_chain.invoke({"question": question, "stage": stage}).strip()

# ===== 2) 전체 분석 문장 생성 =====
_FINDINGS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "너는 학습 분석 리포트를 쓰는 전문가야. 통계를 바탕으로 핵심 인사이트를 3~5문장으로 한국어로 제공해."
     "문장은 간결하게, 과장 금지, 액션 제안 1개 포함."),
    ("human",
     "총 질문 수: {total}\n"
     "학습 스테이지 질문 수: {learn}\n"
     "보스 스테이지 질문 수: {boss}\n"
     "난이도 분포(개수): {counts}\n"
     "샘플 질문 10개 이하: {samples}\n"
     "\n"
     "결과는 JSON 배열 형태의 한국어 문장 리스트로 반환해. 예: [\"문장1\", \"문장2\", ...]")
])

_findings_chain = _FINDINGS_PROMPT | _model() | StrOutputParser()

def generate_overall_findings(
    total: int,
    learn: int,
    boss: int,
    counts: Dict[str, int],
    samples: List[str],
):
    import json
    raw = _findings_chain.invoke({
        "total": total, "learn": learn, "boss": boss,
        "counts": counts, "samples": samples
    })
    try:
        arr = json.loads(raw)
        if isinstance(arr, list):
            return arr
    except Exception:
        pass
    # 파싱 실패 시 문장 하나만 넣기
    return [f"총 {total}개의 질문을 기반으로 학습과 보스 단계의 난이도를 분석했습니다."]
