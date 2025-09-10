
from config import CHROMA_DB_PATH, EMBEDDING_MODEL_NAME
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain_voyageai import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(model=EMBEDDING_MODEL_NAME)

def get_retriever():
    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,  
        persist_directory=CHROMA_DB_PATH
    )
    try:
        collection = vector_store._collection
        count = collection.count()
        print(f"📊 Chroma DB 문서 개수: {count}")
        
        if count == 0:
            print("⚠️  경고: Chroma DB에 문서가 없습니다!")

    except Exception as e:
        print(f"❌ Chroma DB 상태 확인 실패: {e}")



    """
        search_kwargs는 LangChain에서 **retriever가 문서를 검색할 때 사용하는 "검색 조건"**을 설정하는 딕셔너리
         
            k => 반환할 유사 문서의 개수 
            filter => 메타데이터 기반 필터링
            score_threshold => 유사도 점수가 일정 기준 이상인 문서만 반환 
            lambda_mult => 일부 벡터스토어에서 ranking 보정 가중치
        
    """
    retriever = vector_store.as_retriever(
        search_kwargs={'k': 1}
    )
    return retriever


"""

chromadb.errors.InvalidArgumentError: Collection expecting embedding with dimension of 1024, got 512

ChromaDB에 저장된 벡터의 차원과 현재 검색을 위해 입력된 쿼리 벡터의 차원이 다르다.

Collection에 저장된 모든 벡터의 차원은 1024인데 쿼리 벡터의 차원은 512이다.


"""