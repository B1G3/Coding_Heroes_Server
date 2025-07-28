# rag/embed_docs.py

from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from config import DOCS_PATH, CHROMA_DB_PATH

def embed_and_store():
    # 문서 로드 및 분할
    loader = TextLoader(DOCS_PATH, encoding="utf-8")
    documents = loader.load()
    content = documents[0].page_content

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "H1")]
    )
    split_docs = splitter.split_text(content)

    # 임베딩 및 벡터 저장
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    vectordb = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vectordb.persist()
    print(f"✅ 벡터스토어 저장 완료: {CHROMA_DB_PATH}")

if __name__ == "__main__":
    embed_and_store()
