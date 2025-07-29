import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")

PROMPT_PATH = os.path.join(DATA_DIR, "system_prompt", "prompt_0729_v1.txt")

DOCS_PATH = os.path.join(DATA_DIR, 'rag_docs', 'docs_0729_v1.md')

CHROMA_DB_PATH = os.path.join(DATA_DIR, 'chroma_db')
DB_PATH = os.path.join(DATA_DIR, "coding-heroes.db")
DB_URL = f"sqlite:///{DB_PATH}"