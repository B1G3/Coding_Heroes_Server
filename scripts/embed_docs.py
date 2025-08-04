
# https://python.langchain.com/api_reference/chroma/vectorstores/langchain_chroma.vectorstores.Chroma.html#langchain_chroma.vectorstores.Chroma

"""
rag_docs 폴더의 모든 .md 파일을 벡터화하여 Chroma DB에 저장하는 스크립트
"""

import os
import glob
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
# from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.schema import Document

from config import CHROMA_DB_PATH, RAG_DOCS_DIR

EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL", "text-embedding-3-large")


def embed_docs():
    """rag_docs 폴더의 모든 .md 파일을 벡터화하여 Chroma DB에 저장"""
    
    print("=== 문서 벡터화 시작 ===")
    
    # 1. rag_docs 폴더의 모든 .md 파일 찾기
    md_files = glob.glob(os.path.join(RAG_DOCS_DIR, "*.md"))
    
    if not md_files:
        print(f"❌ {RAG_DOCS_DIR} 폴더에서 .md 파일을 찾을 수 없습니다.")
        return
    
    print(f"📁 발견된 .md 파일: {len(md_files)}개")
    for file_path in md_files:
        print(f"   - {os.path.basename(file_path)}")
    
    all_documents = []
    
    # 2. 각 파일 처리
    for file_path in md_files:
        filename = os.path.basename(file_path)
        print(f"\n📄 처리 중: {filename}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            print(f"   ✅ 파일 로드 완료 (길이: {len(content)} 문자)")
        except Exception as e:
            print(f"   ❌ 파일 로드 실패: {e}")
            continue
        
        # 3. 문서를 하나의 청크로 처리 (분할하지 않음)
        document = Document(
            page_content=content,
            metadata={
                "source": filename
            }
        )
        
        all_documents.append(document)
        print(f"   ✅ Document 객체 생성 완료: 1개 청크")
    
    print(f"\n📊 총 처리된 문서: {len(all_documents)}개")
    
    # 4. Embeddings 모델 로드
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    
    # 5. Chroma DB에 저장
    try:
        vectorestore = Chroma.from_documents(
            documents=all_documents,
            embedding=embeddings,
            persist_directory=CHROMA_DB_PATH
        )
        
        # 저장 확인
        collection = vectorestore._collection
        count = collection.count()
        print(f"📊 저장된 문서 개수: {count}")
        
        # 샘플 검색 테스트
        test_results = vectorestore.similarity_search("스테이지1", k=1)
        print(f"🔍 검색 테스트 결과: {len(test_results)}개 문서 검색됨")
        if test_results:
            print(f"   첫 번째 결과: {test_results[0].page_content[:100]}...")
            print(f"   소스 파일: {test_results[0].metadata.get('source', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Chroma DB 저장 실패: {e}")
    
    print("=== 문서 벡터화 완료 ===")

if __name__ == "__main__":
    embed_docs() 