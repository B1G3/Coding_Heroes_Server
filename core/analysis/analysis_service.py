# core/analysis/analysis_service.py
from __future__ import annotations
import uuid
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Tuple

from core.database_client.supabase_client import get_supabase
from core.repositories.questions import QuestionsRepo
from core.repositories.ai_analysis import AiAnalysisRepo
from core.analysis.analysis_llm import (
    classify_question_level,
    generate_overall_findings,
)

STAGES_LEARN = {"learn"}
STAGES_BOSS = {"boss"}

def _rate(part: int, total: int) -> str:
    if total <= 0:
        return "0.00"
    pct = (Decimal(part) * Decimal(100)) / Decimal(total)
    return str(pct.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

def _split_by_stage(rows: List[Dict]) -> Tuple[int, int]:
    learn_cnt = sum(1 for r in rows if str(r.get("stage")) in STAGES_LEARN)
    boss_cnt  = sum(1 for r in rows if str(r.get("stage")) in STAGES_BOSS)
    return learn_cnt, boss_cnt

def update_ai_analysis_for_client(client_id: uuid.UUID) -> Dict:
    """
    - questions 테이블에서 해당 client의 모든 질문을 가져온다
    - LLM으로 각 질문의 난이도(BASIC/INTERMEDIATE/ADVANCED) 분류
    - 통계 집계 후 ai_analysis에 upsert
    - analysis_results에는 LLM 요약 문장 배열을 저장
    """
    sb = get_supabase()
    qrepo = QuestionsRepo(sb)
    arepo = AiAnalysisRepo(sb)

    # 1) 질문 로드
    resp = (
        sb.schema("public")
        .table("questions")
        .select("stage, question, created_at")
        .eq("client_id", str(client_id))
        .order("created_at", desc=False)
        .execute()
    )
    questions = resp.data or []

    total = len(questions)
    learn_cnt, boss_cnt = _split_by_stage(questions)

    # 2) 난이도 분류
    #    필요한 경우 캐싱/증분 업데이트로 최적화 가능(마지막 updated 이후 질문만 재분류)
    levels: List[str] = []
    for q in questions:
        lvl = classify_question_level(q["question"], stage=str(q.get("stage", "")))
        # normalize
        lvl = (lvl or "").strip().lower()
        if lvl not in ("basic", "intermediate", "advanced"):
            lvl = "basic"
        levels.append(lvl)

    basic_cnt = sum(1 for l in levels if l == "basic")
    inter_cnt = sum(1 for l in levels if l == "intermediate")
    adv_cnt   = sum(1 for l in levels if l == "advanced")

    row = {
        "client_id": str(client_id),
        "total_questions": total,
        "learn_stage_questions": learn_cnt,
        "boss_stage_questions": boss_cnt,
        "basic_questions_count": basic_cnt,
        "basic_questions_rate": _rate(basic_cnt, total),
        "intermediate_questions_count": inter_cnt,
        "intermediate_questions_rate": _rate(inter_cnt, total),
        "advanced_questions_count": adv_cnt,
        "advanced_questions_rate": _rate(adv_cnt, total),
        # 3) LLM 종합 분석(문장 리스트)
        "analysis_results": generate_overall_findings(
            total=total,
            learn=learn_cnt,
            boss=boss_cnt,
            counts={"basic": basic_cnt, "intermediate": inter_cnt, "advanced": adv_cnt},
            samples=[q["question"] for q in questions[:10]],  # 일부 샘플만 전달
        ),
    }

    # 4) upsert
    arepo.upsert_by_client(client_id, row)
    return row
