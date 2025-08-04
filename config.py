import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

PROMPT_PATH = os.path.join(DATA_DIR, "system_prompt", "prompt_0804.txt")

# RAG 문서 경로들
RAG_DOCS_DIR = os.path.join(DATA_DIR, 'rag_docs')

CHROMA_DB_PATH = os.path.join(DATA_DIR, 'chroma_db')
DB_PATH = os.path.join(DATA_DIR, "coding-heroes.db")
DB_URL = f"sqlite:///{DB_PATH}"
