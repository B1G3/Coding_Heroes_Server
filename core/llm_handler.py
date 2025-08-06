import logging
logger = logging.getLogger(__name__)
logger.info("llm_handler logger")

from dotenv import load_dotenv
load_dotenv()
from config import CHROMA_DB_PATH, PROMPT_PATH

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
            참고 스테이지 문서: {context}

            플레이어의 블록 코딩 json: {json_str}

            플레이어의 질문: {user_question}
        """)
    ])
    print("✅ ChatPromptTemplate 생성 완료")

    # LLM 및 RAG 체인 구성
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    # from langchain_anthropic import ChatAnthropic
    # llm = ChatAnthropic(
    #     model="claude-sonnet-4-20250725",
    #     temperature=0,
    # )

    def format_docs(docs):
        context_str = "\n\n".join(doc.page_content for doc in docs)
        # print("🔎 [RAG] context(문서 내용):\n", context_str)
        return context_str

    def get_stage_query(input_dict):
        """스테이지 정보를 바탕으로 검색 쿼리 생성"""
        stage = input_dict["stage"]
        return f"스테이지 {stage}"

    # def get_user_question(input_dict):
    #     return input_dict["user_question"]
    
    print("🔧 Chain 구성 시작...")
    chain = (
        {
            "user_question": RunnablePassthrough(),
            "json_str": RunnablePassthrough(),
            "context": RunnablePassthrough() | get_stage_query | retriever | format_docs,
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



from core.database import select_playrecord

# -------------------------------------------------------- 질의응답 ----------------------------------------------------------
def chat(user_question: str, stage: str="1", user_id: str = None, conversation_id: str = None) -> str:
    """
    사용자의 질문에 대한 답변을 생성하는 메소드 
    
    Args:
        user_question: 사용자 질문
        stage: 스테이지 단계 (예: "1", "boss")
        user_id: 사용자 ID (선택사항)
        conversation_id: 대화 세션 ID (선택사항)
    """
    # chain이 초기화되지 않았다면 초기화
    if not is_chain_initialized():
        initialize_chain()
    
    json_str = select_playrecord(user_id=user_id, stage=stage)

    # Chain을 사용하여 응답 생성
    response = chain.invoke({
        "stage": stage,
        "json_str": json_str,
        "user_question": user_question,
    })
    
    # 대화 내용 저장 (user_id와 conversation_id가 제공된 경우)
    # if user_id and conversation_id:
    #     save_message(user_id, conversation_id, "human", user_question)
    #     save_message(user_id, conversation_id, "ai", response)
    
    return response


# from core.database import select_messages_by_user_and_conversation_id, add_message

# def get_conversation_history(user_id: str, conversation_id: str) -> str:
#     """
#     user_id, conv_id로 대화 히스토리 조회
#     """
#     messages = select_messages_by_user_and_conversation_id(user_id, conversation_id)

#     conversation_history = []
#     for msg in messages:
#         role = "사용자" if msg.role == "human" else "AI"
#         conversation_history.append(f"{role}: {msg.content}")

#     history = "\n".join(conversation_history)
    
#     return history



# def save_message(user_id: str, conversation_id: str, role: str, content: str):
#     """
#     메시지 저장
#     """
#     return add_message(user_id, conversation_id, role, content)

