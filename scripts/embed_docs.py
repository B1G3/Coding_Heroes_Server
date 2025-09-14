
# $set PYTHONPATH=%cd% && python scripts/embed_docs.py
# API Reference: https://python.langchain.com/docs/integrations/vectorstores/chroma/#query-vector-store

"""
rag_docs 폴더의 모든 .md 파일을 벡터화하여 Chroma DB에 저장하는 스크립트
"""
from typing import List
import os
import glob
from uuid import uuid4
import shutil

from config import CHROMA_DB_PATH, RAG_DOCS_DIR, EMBEDDING_MODEL_NAME
from dotenv import load_dotenv
load_dotenv()

from langchain_chroma import Chroma
from langchain.schema import Document
from langchain_voyageai import VoyageAIEmbeddings

embeddings = VoyageAIEmbeddings(model=EMBEDDING_MODEL_NAME)

"""
voyage-3.5-lite
voyage-3.5
voyage-3-large
voyage-context-3


voyageai

10000 TPM (Tokens Per Minute)
: 분당 최대 10,000 토큰 처리

- 토큰: 텍스트를 임베딩 모델이 처리하는 최소 단위
    영어 단어 하나가 보통 1~2개 토큰
    한글은 글자 1~2개가 토큰 1개

3 RPM (Requests Per Minute)
: 분당 최대 3개의 요청

"""

def get_files():
    files = glob.glob(os.path.join(RAG_DOCS_DIR, "*.md"))

    if not files:
        print(f"❌ {RAG_DOCS_DIR} 폴더에서 .md 파일을 찾을 수 없습니다.")
        return
    print(f"📁 발견된 .md 파일: {len(files)}개")

    return files


def document(files: list) -> List[Document]:
    documents: List[Document] = []

    for file_path, id in list(zip(files, range(len(files)))):
        filename = os.path.basename(file_path)
        print(f"📄 처리 중: {filename}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 파일 로드 실패: {e}")
            continue
        
        # 문서를 하나의 청크로 처리 (분할X)
        document = Document(
            page_content=content,
            metadata={
                "source": filename
            },
            id=id
        )
        documents.append(document)

    return documents



def vectorize(documents: List[Document]):
    try:
        vector_store = Chroma(
            collection_name="example_collection",
            embedding_function=embeddings,
            persist_directory=CHROMA_DB_PATH
        )

        uuids = [str(uuid4()) for _ in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=uuids)

        return vector_store
            
    except Exception as e:
        print(f"❌ Chroma DB 저장 실패: {e}")


def similarity_search(vector_store):
    print("===유사도 검색 테스트===")
    results = vector_store.similarity_search(
        "스테이지1", 
        k=1
    )

    print()
    for res in results:
        print(f"* {res.page_content[:100]}... \n    [{res.metadata}], [id={res.id}]")


def embed_docs():
    # 0) 기존 ChromaDB 폴더 삭제
    if os.path.exists(CHROMA_DB_PATH):
        print(f"기존 DB 삭제: {CHROMA_DB_PATH}")
        shutil.rmtree(CHROMA_DB_PATH)
    
    # 1) rag_docs 폴더의 모든 .md 파일 찾기
    files = get_files()

    # 2) 각 파일 처리하여 리스트로 반환
    documents = document(files) 

    # 3) 임베딩 후 ChromaDB에 저장
    vector_store = vectorize(documents)

    # 4) 유사도 검색 테스트
    similarity_search(vector_store)
    


if __name__ == "__main__":
    embed_docs() 

