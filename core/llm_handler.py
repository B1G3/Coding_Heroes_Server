import logging
logger = logging.getLogger(__name__)
logger.info("llm_handler logger")

from dotenv import load_dotenv
load_dotenv()
from config import CHROMA_DB_PATH, PROMPT_PATH


from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate


from core.vector_utils import get_retriever, get_vectorestore, check_chroma_db_status

chain = None

# -------------------------------------------------------- chain 생성 (서버 실행시 한번만 호출) ----------------------------------------------------------
def setup_chain():
    global chain
    print("=== setup_chain 디버깅 시작 ===")
    
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
    print(f"✅ System prompt 로드 완료 (길이: {len(SYSTEM_PROMPT)} 문자)")

    vectorestore = get_vectorestore()
    print(f"✅ Chroma 벡터스토어 로드 완료 (경로: {CHROMA_DB_PATH})")
    
    check_chroma_db_status(vectorestore)

    retriever = get_retriever(vectorestore)
    print("✅ Retriever 생성 완료")
    
    # ChatPromptTemplate 정의
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """
            참고 문서:
            {context}

            이전 대화 내용:
            {conversation_history}

            현재 사용자 질문: {user_question}

            이전 대화 내용을 고려하여 사용자의 질문에 대해 친절하고 도움이 되는 답변을 해주세요.
        """)
    ])
    print("✅ ChatPromptTemplate 생성 완료")

    # LLM 및 RAG 체인 구성
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    print("✅ LLM 모델 로드 완료")

    def format_docs(docs):
        context_str = "\n\n".join(doc.page_content for doc in docs)
        # print("🔎 [RAG] context(문서 내용):\n", context_str)
        return context_str


    def get_user_question(input_dict):
        return input_dict["user_question"]
    
    print("🔧 Chain 구성 시작...")
    chain = (
        {
            "conversation_history": RunnablePassthrough(),
            "user_question": RunnablePassthrough(),
            "context": RunnablePassthrough() | get_user_question | retriever | format_docs,
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    print("✅ Chain 구성 완료")
    return chain

# chain 초기화 함수 - 외부에서 호출 가능
def initialize_chain():
    """외부에서 chain을 초기화하는 함수"""
    global chain
    if chain is None:
        chain = setup_chain()
    return chain

# chain이 초기화되었는지 확인하는 함수
def is_chain_initialized():
    """chain이 초기화되었는지 확인하는 함수"""
    return chain is not None


# -------------------------------------------------------- 질의응답 ----------------------------------------------------------
def chat(user_question: str, user_id: str = None, conversation_id: str = None) -> str:
    """
    사용자의 질문에 대한 답변을 생성하는 메소드 (이전 대화 내용 고려)
    
    Args:
        user_question: 사용자 질문
        user_id: 사용자 ID (선택사항)
        conversation_id: 대화 세션 ID (선택사항)
    """
    # chain이 초기화되지 않았다면 초기화
    if not is_chain_initialized():
        initialize_chain()
    
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



def get_conversation_history(user_id: str, conversation_id: str) -> str:
    """
    user_id, conv_id로 대화 히스토리 조회
    """
    messages = select_messages_by_user_and_conversation_id(user_id, conversation_id)

    conversation_history = []
    for msg in messages:
        role = "사용자" if msg.role == "human" else "AI"
        conversation_history.append(f"{role}: {msg.content}")

    history = "\n".join(conversation_history)
    
    return history



def save_message(user_id: str, conversation_id: str, role: str, content: str):
    """
    메시지 저장
    """
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




# # claude 모델
# from langchain_anthropic import ChatAnthropic

# anthropic_llm = ChatAnthropic(
#     model="claude-sonnet-4-20250725",
#     temperature=0,

# )

