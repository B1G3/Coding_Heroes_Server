from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.api.ai_npc import router as ai_npc_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_npc_router, prefix="/ai_npc")
