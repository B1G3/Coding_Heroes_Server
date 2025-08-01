import logging
logger = logging.getLogger(__name__)

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

@router.post("/")
def block_coding():
    return ""