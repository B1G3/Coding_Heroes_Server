import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class ExecutionLogIn(BaseModel):
    client_id: uuid.UUID
    stage: str
    block_json: Dict[str, Any]

class ExecutionLogOut(BaseModel):
    id: Optional[str] = None
    client_id: uuid.UUID
    stage: str
    block_json: Dict[str, Any]
    created_at: str

class LatestQuery(BaseModel):
    client_id: uuid.UUID
    stage: str
