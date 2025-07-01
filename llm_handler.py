
import json
import os

import logging
logger = logging.getLogger(__name__)


# python-dotenv 패키지를 사용해서 .env 파일에 저장된 환경변수들을 파이썬 프로그램에 자동으로 불러오는 역할을 한다. 
# load_dotenv()를 호출하면 .env 파일의 내용이 현재 파이썬 프로세스의 환경변수(os.environ)로 등록된다.
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# --- system_prompt.txt 파일에서 불러오기 ---
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def analyze_code(json_data: dict) -> str: 


    user_prompt = f"""
다음은 사용자의 블록 코딩 결과야:\n
```json\n
{json.dumps(json_data, indent=2, ensure_ascii=False)}\n
```\n
이 구조를 분석해서 피드백을 줘
"""
    
    response = llm.invoke([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_prompt)
    ])

    return response.content