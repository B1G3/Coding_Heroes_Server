import logging
logger = logging.getLogger(__name__)
logger.info("llm_handler logger")

from config import CHROMA_DB_PATH, PROMPT_PATH
from dotenv import load_dotenv
load_dotenv()

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from core.retriever import get_retriever

chain = None

def llm_model():
    return ChatAnthropic(
        model="claude-3-5-sonnet-latest",
        temperature=0,
        max_tokens=1024,
        timeout=None,
        max_retries=2,
        # other params...
    )

def prompttemplate():
    # 1) Get SYSTEM PROMPT
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
    print(f"✅ System prompt 로드")

    # 2) Generate PROMPT TEMPLATE
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", """
# 플레이어의 질문:{question}

# 플레이어의 블록 코딩
```json
{block_json}
```

# 참고 스테이지 문서
{context}

플레이어의 블록 코딩 json은 플레이어 질문이 블록 코딩에 대한 피드백을 요구할 때만 참고해.
단순히 인사를 하거나 게임 시스템에 대한 질문을 할 때는 블록 코딩 json을 참고할 필요 없어.
        """)
    ])
    return prompt_template

def setup_chain():
    global chain

    def format_docs(docs):
        context_str = "\n\n".join(doc.page_content for doc in docs)
        # print("🔎 [RAG] context(문서 내용):\n", context_str)
        return context_str

    def get_stage_query(input):
        """스테이지를 바탕으로 검색 쿼리 생성"""
        stage = input['stage']
        return f"스테이지 {stage}"
    
    def question(input):
        return input['question']

    def block_json(input):
        return input['block_json']
        
    
    print("🔧 Chain 구성 시작...")
    chain = (
        {
            "question": question,
            "block_json": block_json,
            "context": get_stage_query | get_retriever() | format_docs,
        }
        | prompttemplate()
        | llm_model()
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


from core.database_client.sqlite_client import select_execution_log

# -------------------------------------------------------- 질의응답 ----------------------------------------------------------
def chat(question: str, stage: str) -> str:
    
    # chain이 초기화되지 않았다면 초기화
    if not is_chain_initialized():
        initialize_chain()
    
    block_json = select_execution_log(stage=stage)
        
    # Chain을 사용하여 응답 생성
    response = chain.invoke({
        "stage": stage,
        "block_json": block_json,
        "question": question,
    })

    return response