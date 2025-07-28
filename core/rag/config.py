import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROMPT_PATH = os.path.join(BASE_DIR, "system_prompt.txt")
DOCS_PATH = os.path.join(BASE_DIR, 'docs.md')
CHROMA_DB_PATH = os.path.join(BASE_DIR, 'chroma_db')
