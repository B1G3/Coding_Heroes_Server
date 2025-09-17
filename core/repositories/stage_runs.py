import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from supabase import Client

class StageRunsRepo:
    def __init__(self, supabase: Client, schema: str = "public") -> None:
        self.supabase = supabase
        self.schema = schema

    def save(
        self,
        *,
        client_id: uuid.UUID,
        stage: str,
        cleared: bool,
        created_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        core.stage_runs 테이블에 스테이지 클리어 기록을 저장합니다.
        """
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "cleared": cleared,
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
            "metadata": metadata
        }
        return (
            self.supabase
            .schema(self.schema)
            .table("stage_runs")
            .insert(data)
            .execute()
        ) 
        