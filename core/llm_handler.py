
import json
import os

"""
각 모듈(파일)별로 로거 인스턴스를 생성한다.
이 로거는 basicConfig에서 지정한 설정(레벨, 포맷 등)을 따른다.
각 파일마다 __name__이 다르므로, 로그 메시지에 어떤 파일에서 발생한 로그인지 구분할 수 있다.
"""
import logging
logger = logging.getLogger(__name__)
logger.info("llm_handler logger")

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


# temperature: 값이 높을수록 창의적이고 다양한 결과, 낮을수록 일관되고 예측 가능한 결과
# 정답이 존재하는 문제 (수학, 규칙, 코드 피드백 등) → temperature = 0
# 게임 대사, 창의적 문장, 마케팅 문구, 이름 생성 등 → temperature = 0.7 ~ 1.0
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# --- system_prompt 불러오기 ---
"""
스크립트를 어디서 실행하느냐에 따라 파일을 찾는 위치가 달라진다.
llm_handler.py 파일이 있는 위치에서 파일을 읽도록 경로를 지정해야 한다.
이제 어디서 실행해도 문제 없음!
"""
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_PATH = os.path.join(BASE_DIR, "system_prompt.txt")
with open(PROMPT_PATH, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# ChatPromptTemplate 정의
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", """
        이전 대화 내용:
        {conversation_history}

        현재 사용자 질문: {user_question}

        이전 대화 내용을 고려하여 사용자의 질문에 대해 친절하고 도움이 되는 답변을 해주세요.
    """)
])


"""
RunnablePassThrough란?
- 입력값을 가공하지 않고 그대로 다음 단계로 전달하는 역할
- 입력 딕셔너리의 값을 그대로 prompt_template에 넘긴다.
"""
# Chain 구성
chain = (
    # 입력값을 그대로 다음 단계로 전달 (딕셔너리 형태 유지)
    {"conversation_history": RunnablePassthrough(), "user_question": RunnablePassthrough()}
    # 위 딕셔너리를 prompt_template에 적용하여 프롬프트 완성
    | prompt_template
    | llm
    | StrOutputParser()
)




# -------------------------------------------------------- 질의응답 ----------------------------------------------------------
def chat(user_question: str, user_id: str = None, conversation_id: str = None) -> str:
    """
    사용자의 질문에 대한 답변을 생성하는 메소드 (이전 대화 내용 고려)
    
    Args:
        user_question: 사용자 질문
        user_id: 사용자 ID (선택사항)
        conversation_id: 대화 세션 ID (선택사항)
    """
    # 이전 대화 내용 조회
    conversation_history = ""
    if user_id and conversation_id:
        conversation_history = get_conversation_history(user_id, conversation_id)
    
    # Chain을 사용하여 응답 생성
    response = chain.invoke({
        "conversation_history": conversation_history,
        "user_question": user_question
    })
    
    # 대화 내용 저장 (user_id와 conversation_id가 제공된 경우)
    if user_id and conversation_id:
        save_message(user_id, conversation_id, "human", user_question)
        save_message(user_id, conversation_id, "ai", response)
    
    return response





from core.database import select_messages_by_user_and_conversation_id, add_message

# 대화 히스토리 조회
def get_conversation_history(user_id: str, conversation_id: str) -> str:
    messages = select_messages_by_user_and_conversation_id(user_id, conversation_id)

    conversation_history = []
    for msg in messages:
        role = "사용자" if msg.role == "human" else "AI"
        conversation_history.append(f"{role}: {msg.content}")

    history = "\n".join(conversation_history)
    print("result: ", history)
    
    return history

# 메시지 저장
def save_message(user_id: str, conversation_id: str, role: str, content: str):
    return add_message(user_id, conversation_id, role, content)

# -------------------------------------------------------- 블록 피드백 ----------------------------------------------------------
# def analyze_blocks(json_data: dict) -> str: 
#     user_prompt = f"""
#         다음은 사용자의 블록 코딩 결과야:\n
#         ```json\n
#         {json.dumps(json_data, indent=2, ensure_ascii=False)}\n
#         ```\n
#         이 구조를 분석해서 피드백을 줘
#     """
    
#     response = llm.invoke([
#         SystemMessage(content=SYSTEM_PROMPT),
#         HumanMessage(content=user_prompt)
#     ])

#     return response.content
