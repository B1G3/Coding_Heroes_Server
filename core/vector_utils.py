import os
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from config import CHROMA_DB_PATH


EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large")



def get_vectorestore():
    """
    Chroma vectorestore를 초기화하여 반환하는 함수
    """
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    vectorestore = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings
    )
    return vectorestore


def get_retriever(vectorestore):
    # 문서 검색용 retriever 생성
    # search_kwargs는 LangChain에서 **retriever가 문서를 검색할 때 사용하는 "검색 조건"**을 설정하는 딕셔너리
    '''
    k => 반환할 유사 문서의 개수 
    filter => 메타데이터 기반 필터링
    score_threshold => 유사도 점수가 일정 기준 이상인 문서만 반환 
    lambda_mult => 일부 벡터스토어에서 ranking 보정 가중치
    '''
    retriever = vectorestore.as_retriever(
        search_kwargs={'k': 10}
    )
    return retriever




# Chroma DB 상태 확인
def check_chroma_db_status(vectorestore):
    try:
        collection = vectorestore._collection
        count = collection.count()
        print(f"📊 Chroma DB 문서 개수: {count}")
        
        if count == 0:
            print("⚠️  경고: Chroma DB에 문서가 없습니다!")
            print("💡 해결방법: docs.md 파일을 벡터화하여 Chroma DB에 저장해야 합니다.")

    except Exception as e:
        print(f"❌ Chroma DB 상태 확인 실패: {e}")
