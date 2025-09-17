import os
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv()



_SUPABASE: Optional[Client] = None

def init_supabase() -> Client:
    global _SUPABASE
    if _SUPABASE is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SECRET_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 누락")
        _SUPABASE = create_client(url, key)
    return _SUPABASE

def get_supabase() -> Client:
    if _SUPABASE is None:
        return init_supabase()
    return _SUPABASE





class SupabaseClient:
    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_SECRET_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 환경변수가 없습니다.")
        self.supabase: Client = create_client(url, key)

    # 내부 편의 함수
    def _table(self, name: str):
        return self.supabase.schema("core").table(name)

    def save_stage_run(
            self, 
            stage: str, 
            cleared: bool,
            metadata: Optional[Dict[str, Any]] = None, 
            client_id: uuid.UUID=DEFAULT_CLIENT_ID
        ):
        """
        core.stage_runs 테이블에 스테이지 클리어 기록을 저장합니다.
        """
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "cleared": cleared,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata
        }
        
        try:
            response = self._table('stage_runs').insert(data).execute()
            print(f"✅ Stage run for {stage} saved successfully.")
            return response
        except Exception as e:
            print(f"❌ Error saving stage run: {e}")
            return None

    def save_question(
            self, 
            stage: str, 
            question: str, 
            client_id: uuid.UUID=DEFAULT_CLIENT_ID
        ):
        """
        core.questions 테이블에 플레이어의 질문을 저장합니다.
        """
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "question": question,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            response = self._table('questions').insert(data).execute()
            print(f"✅ Question for {stage} saved successfully.")
            return response
        except Exception as e:
            print(f"❌ Error saving question: {e}")
            return None

    def save_execution_log(
            self, 
            stage: str, 
            block_json: dict, 
            client_id: uuid.UUID=DEFAULT_CLIENT_ID
            ):
        """
        core.execution_logs 테이블에 실행 기록을 저장합니다.
        """
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "block_json": block_json,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        try:
            response = self._table('execution_logs').insert(data).execute()
            print(f"✅ Execution log for {stage} saved successfully.")
            return response
        except Exception as e:
            print(f"❌ Error saving execution log: {e}")
            return None
        
