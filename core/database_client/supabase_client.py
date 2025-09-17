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