import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from supabase import Client

class ExecutionLogsRepo:
    def __init__(self, supabase: Client, schema: str = "public") -> None:
        self.supabase = supabase
        self.schema = schema

    def save(
        self,
        *,
        client_id: uuid.UUID,
        stage: str,
        block_json: Optional[Dict[str, Any]],
        created_at: Optional[str] = None,
    ):
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "block_json": block_json,
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        }
        return (
            self.supabase
            .schema(self.schema)
            .table("execution_logs")
            .insert(data)
            .execute()
        )

    def get_latest_one(self, *, client_id: uuid.UUID, stage: str):
        """client_id + stage 조합의 최신 1건 반환"""
        resp = (
            self.supabase
            .schema(self.schema)
            .table("execution_logs")
            .select("*")
            .eq("client_id", str(client_id))
            .eq("stage", stage)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None
