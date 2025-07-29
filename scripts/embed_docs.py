
# https://python.langchain.com/api_reference/chroma/vectorstores/langchain_chroma.vectorstores.Chroma.html#langchain_chroma.vectorstores.Chroma

"""
docs.md 파일을 벡터화하여 Chroma DB에 저장하는 스크립트
"""

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.schema import Document

from config import CHROMA_DB_PATH, DOCS_PATH

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large")


def embed_docs():
    """docs.md 파일을 벡터화하여 Chroma DB에 저장"""
    
    print("=== 문서 벡터화 시작 ===")
    
    # 1. docs.md 파일 읽기
    try:
        with open(DOCS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"✅ docs.md 파일 로드 완료 (길이: {len(content)} 문자)")
    except Exception as e:
        print(f"❌ docs.md 파일 로드 실패: {e}")
        return
    
    # 2. 텍스트 분할
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "H1")]
    )
    
    documents = splitter.split_text(content)
    print(f"✅ 텍스트 분할 완료: {len(documents)}개 청크")
    
    # 3. 메타데이터 추가
    for doc in documents:
        doc.metadata["source"] = "docs.md"
    print(f"✅ Document 객체 생성 완료: {len(documents)}개")
    
    # 4. Embeddings 모델 로드
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    
    # 5. Chroma DB에 저장
    try:
        vectorestore = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
        
        # 저장 확인
        collection = vectorestore._collection
        count = collection.count()
        print(f"📊 저장된 문서 개수: {count}")
        
        # 샘플 검색 테스트
        test_results = vectorestore.similarity_search("블록코딩", k=2)
        print(f"🔍 검색 테스트 결과: {len(test_results)}개 문서 검색됨")
        if test_results:
            print(f"   첫 번째 결과: {test_results[0].page_content[:100]}...")
            
    except Exception as e:
        print(f"❌ Chroma DB 저장 실패: {e}")
    
    print("=== 문서 벡터화 완료 ===")

if __name__ == "__main__":
    embed_docs() 