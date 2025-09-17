# Seed script to call /llm-response-test for multiple clients with staged questions.
# It uses environment variable BASE_URL for the endpoint (default shown below).
# Example:
#   BASE_URL="http://localhost:8000/llm-response-test" python /mnt/data/seed_llm_response_test.py

import os
import json
import requests
from typing import List, Tuple

BASE_URL = "https://jolly-accepted-bonefish.ngrok-free.app/ai_npc/llm-response-test"

# ---- Question pools crafted from prompt_0915 and stage docs (learn/boss) ----
LEARN_BASIC = [
    "이동한다 블록에 꼭 연결해야 하는 입력은 뭐야?",  # 입력 필요 개념 확인
    "정수 입력 1을 연결하면 유닛은 어느 데이터로드로 이동해?",  # 맵 인덱스 개념
]

LEARN_INTERMEDIATE = [
    "정수 3으로 이동한 뒤 백신 멍멍이가 다음에 해야 할 블록 연결 순서를 알려줘.",  # 순서/응용
    "이동한다에 연결할 정수값을 바꾸면 데이터로드 선택이 어떻게 변해? 1부터 4까지 기준으로 설명해줘.",  # 규칙 응용
]

LEARN_ADVANCED = [
    "내 라인에서 이동한다에 입력이 없어서 유닛이 멈춰. 어디를 어떻게 고쳐야 해?",  # 디버깅
    "Start→이동한다→백신 멍멍이 구성이 맞는데 실행이 안 돼. 가장 가능성 높은 오류 두 가지를 추정해줘.",  # 추론/디버깅
]

BOSS_BASIC = [
    "보스 스테이지에서 While과 If는 각각 어떤 역할을 해?",  # 제어 블록 기본
    "백신 멍멍이가 처리할 수 있는 바이러스는 무엇이야?",  # 유닛-바이러스 매칭
]

BOSS_INTERMEDIATE = [
    "While 다음에 If로 웜을 검사하고 이동한다→공격한다 순서로 연결하면 흐름이 맞을까?",  # 흐름/응용
    "함수블록에 매개변수로 바이러스를 두면 어떤 장점이 있어? 외부에서 값을 바꿀 때의 이점을 설명해줘.",  # 함수 개념 응용
]

BOSS_ADVANCED = [
    "이동 없이 공격만 연결된 라인이 왜 실패하는지 디버깅 순서를 알려줘.",  # 디버깅
    "함수블록을 도입해 재사용성을 높이려면 라인과 파라미터를 어떻게 설계해야 해?",  # 설계/전략
    "While→If→이동한다→공격한다를 넣었는데 같은 자리에서만 공격해. JSON 구조에서 먼저 확인할 값은 뭐야?",  # 고급 디버깅
]

def pick(items: List[str], n: int) -> List[str]:
    # deterministic pick: take first n (wrap if needed)
    if n <= 0:
        return []
    out = []
    i = 0
    while len(out) < n:
        out.append(items[i % len(items)])
        i += 1
    return out

def plan_for_clients() -> dict:
    """
    Returns mapping: client_id -> List[(stage, question)]
    - Client 1: learn 1, boss 3 (mix basic/intermediate/advanced)
    - Client 2: learn 0, boss 1
    - Client 3: learn 4, boss 5 (balanced mix)
    """
    client1 = "bff109dc-1fb3-437e-a5c1-c5d679681f91"
    client2 = "e5b1244b-eec1-4d33-8433-d9b5e7b2cad8"
    client3 = "ef4a30ef-0210-4bfa-8260-19906f9de309"

    plan = {}

    # ---- Client 1: learn 1 (intermediate), boss 3 (basic, intermediate, advanced) ----
    c1_pairs: List[Tuple[str, str]] = []
    c1_pairs += [("learn", pick(LEARN_INTERMEDIATE, 1)[0])]
    c1_pairs += [("boss", pick(BOSS_BASIC, 1)[0])]
    c1_pairs += [("boss", pick(BOSS_INTERMEDIATE, 1)[0])]
    c1_pairs += [("boss", pick(BOSS_ADVANCED, 1)[0])]
    plan[client1] = c1_pairs

    # ---- Client 2: learn 0, boss 1 (basic) ----
    plan[client2] = [("boss", pick(BOSS_BASIC, 1)[0])]

    # ---- Client 3: learn 4 (B,I,A + extra I), boss 5 (B,I,A + extra I + extra A) ----
    c3_pairs: List[Tuple[str, str]] = []
    c3_pairs += [("learn", pick(LEARN_BASIC, 1)[0])]
    c3_pairs += [("learn", pick(LEARN_INTERMEDIATE, 1)[0])]
    c3_pairs += [("learn", pick(LEARN_ADVANCED, 1)[0])]
    c3_pairs += [("learn", pick(LEARN_INTERMEDIATE, 2)[1])]  # extra intermediate
    c3_pairs += [("boss", pick(BOSS_BASIC, 1)[0])]
    c3_pairs += [("boss", pick(BOSS_INTERMEDIATE, 1)[0])]
    c3_pairs += [("boss", pick(BOSS_ADVANCED, 1)[0])]
    c3_pairs += [("boss", pick(BOSS_INTERMEDIATE, 2)[1])]    # extra intermediate
    c3_pairs += [("boss", pick(BOSS_ADVANCED, 2)[1])]        # extra advanced
    plan[client3] = c3_pairs

    return plan

def post_question(client_id: str, stage: str, question: str):
    headers = {"Content-Type": "application/json", "X-Client-Id": client_id}
    payload = {"text": question, "stage": stage}
    try:
        r = requests.post(BASE_URL, headers=headers, data=json.dumps(payload), timeout=60)
        ok = r.status_code in (200, 201)
        try:
            body = r.json()
        except Exception:
            body = r.text
        print(f"[{client_id[:8]}][{stage}] {question}\n -> HTTP {r.status_code}, ok={ok}\n -> {body}\n")
        return ok
    except Exception as e:
        print(f"[{client_id[:8]}][{stage}] request failed: {e}")
        return False

def main():
    print(f"POST endpoint = {BASE_URL}")
    plan = plan_for_clients()
    total = 0
    success = 0
    for cid, pairs in plan.items():
        for stage, q in pairs:
            total += 1
            if post_question(cid, stage, q):
                success += 1
    print(f"Done. success={success}/{total}")

if __name__ == "__main__":
    main()
