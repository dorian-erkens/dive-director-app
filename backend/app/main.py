from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.routers import chat, wrecks

app = FastAPI(
    title="Dive Director API",
    description="Assistant DP — Caen Ouistreham Plongée",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wrecks.router)
app.include_router(chat.router)


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "dive-director"}
