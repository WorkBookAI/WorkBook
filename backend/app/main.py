from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import init_db
from app.api import documents, chats, models as models_api, tools, rules

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title="WorkBook Backend", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(chats.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(models_api.router, prefix="/api/models", tags=["models"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(rules.router, prefix="/api/rules", tags=["rules"])

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
