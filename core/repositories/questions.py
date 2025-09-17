import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from supabase import Client

class QuestionsRepo:
    def __init__(self, supabase: Client, schema: str = "public") -> None:
        self.supabase = supabase
        self.schema = schema

    def save(
        self,
        *,
        client_id: uuid.UUID,
        stage: str,
        question: str,
        created_at: Optional[str] = None,
    ):
        data = {
            "client_id": str(client_id),
            "stage": stage,
            "question": question,
            "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        }
        return (
            self.supabase
            .schema(self.schema)
            .table("questions")
            .insert(data)
            .execute()
        )
     
