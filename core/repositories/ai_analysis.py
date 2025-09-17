# core/repositories/ai_analysis.py
import uuid
from typing import Optional, Dict, Any
from supabase import Client

class AiAnalysisRepo:
    def __init__(self, supabase: Client, schema: str = "public") -> None:
        self.supabase = supabase
        self.schema = schema

    def get_by_client(self, client_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        resp = (
            self.supabase
            .schema(self.schema)
            .table("ai_analysis")
            .select("*")
            .eq("client_id", str(client_id))
            .limit(1)
            .execute()
        )
        rows = resp.data or []
        return rows[0] if rows else None

    def insert(self, row: Dict[str, Any]):
        return (
            self.supabase
            .schema(self.schema)
            .table("ai_analysis")
            .insert(row)
            .execute()
        )

    def update_by_client(self, client_id: uuid.UUID, patch: Dict[str, Any]):
        return (
            self.supabase
            .schema(self.schema)
            .table("ai_analysis")
            .update(patch)
            .eq("client_id", str(client_id))
            .execute()
        )

    def upsert_by_client(self, client_id: uuid.UUID, row: Dict[str, Any]):
        existed = self.get_by_client(client_id)
        if existed:
            return self.update_by_client(client_id, row)
        else:
            return self.insert(row)
