
import json
import os

import logging
logger = logging.getLogger(__name__)


# python-dotenv 패키지를 사용해서 .env 파일에 저장된 환경변수들을 파이썬 프로그램에 자동으로 불러오는 역할을 한다. 
# load_dotenv()를 호출하면 .env 파일의 내용이 현재 파이썬 프로세스의 환경변수(os.environ)로 등록된다.
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


# temperature: 값이 높을수록 창의적이고 다양한 결과, 낮을수록 일관되고 예측 가능한 결과
# 정답이 존재하는 문제 (수학, 규칙, 코드 피드백 등) → temperature = 0
# 게임 대사, 창의적 문장, 마케팅 문구, 이름 생성 등 → temperature = 0.7 ~ 1.0
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# --- system_prompt.txt 파일에서 불러오기 ---
with open("system_prompt_0703_v2.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def analyze_code(json_data: dict) -> str: 


    user_prompt = f"""
다음은 사용자의 블록 코딩 결과야:\n
```json\n
{json.dumps(json_data, indent=2, ensure_ascii=False)}\n
```\n
이 구조를 분석해서 피드백을 줘
"""
    
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    return response.content


def answer(user_question: str) -> str:
    """
    사용자의 질문에 대한 답변을 생성하는 메소드 (비스트리밍)
    """
    user_prompt = f"""
사용자가 다음과 같이 질문했습니다:
"{user_question}"

이 질문에 대해 친절하고 도움이 되는 답변을 해주세요.
"""
    
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    return response.content


# def answer_stream(user_question: str):
#     """
#     사용자의 질문에 대한 답변을 스트리밍으로 생성하는 메소드
#     """
#     user_prompt = f"""
# 사용자가 다음과 같이 질문했습니다:
# "{user_question}"

# 이 질문에 대해 친절하고 도움이 되는 답변을 해주세요.

# """
    
#     # 스트리밍 응답 생성
#     for chunk in llm.stream([
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=user_prompt)
#     ]):
#         if chunk.content:
#             yield chunk.content