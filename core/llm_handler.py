"""
각 모듈(파일)별로 로거 인스턴스를 생성한다.
이 로거는 basicConfig에서 지정한 설정(레벨, 포맷 등)을 따른다.
각 파일마다 __name__이 다르므로, 로그 메시지에 어떤 파일에서 발생한 로그인지 구분할 수 있다.
"""
import logging
logger = logging.getLogger(__name__)
logger.info("llm_handler logger")

import os
from dotenv import load_dotenv


from langchain.schema import SystemMessage, HumanMessage

from langchain_openai import ChatOpenAI

from langchain_community.vectorstores import Chroma

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import OpenAIEmbeddings

from rag.config import CHROMA_DB_PATH

load_dotenv()

def load_vectordb():

    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorestore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )

    # 문서 검색용 retriever 생성
    # search_kwargs는 LangChain에서 **retriever가 문서를 검색할 때 사용하는 “검색 조건”**을 설정하는 딕셔너리
    '''
    k => 반환할 유사 문서의 개수 
    filter => 메타데이터 기반 필터링
    score_threshold => 유사도 점수가 일정 기준 이상인 문서만 반환 
    lambda_mult => 일부 벡터스토어에서 ranking 보정 가중치
    '''
    retriever = vectorestore.as_retriever(
        search_kwargs={'k': 10}
    )

    '''
    #TODO 문서가 업데이트 되었을때 기존 Chroma 벡터 스토어 갱신하기
    '''
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

    # LLM 및 RAG 체인 구성
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {
            "conversation_history": RunnablePassthrough(),
            "question": RunnablePassthrough(),
            "context": retriever | format_docs,
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return chain

chain = setup_rag()

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
        "question": user_question
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




# # claude 모델
# from langchain_anthropic import ChatAnthropic

# anthropic_llm = ChatAnthropic(
#     model="claude-sonnet-4-20250725",
#     temperature=0,

# )