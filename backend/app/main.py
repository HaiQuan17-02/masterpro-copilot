from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes.documents import router as documents_router
from app.api.routes.search import router as search_router
from app.api.routes.ingestion import router as ingestion_router
from app.api.routes.chat_stream import router as chat_stream_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.auth import router as auth_router
from app.api.routes.lifecycle import router as lifecycle_router
from app.api.routes.provider import router as provider_router
from app.api.routes.benchmark import router as benchmark_router

app = FastAPI(
    title="MasterPro Copilot API",
    version="0.1.0"
)

# CORS Middleware to support frontend React / Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "MasterPro Copilot API is running"
    }

# Include routers
app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(chat_stream_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(search_router, prefix="/api")
app.include_router(ingestion_router, prefix="/api")
app.include_router(feedback_router, prefix="/api")
app.include_router(lifecycle_router, prefix="/api")
app.include_router(provider_router, prefix="/api")
app.include_router(benchmark_router, prefix="/api")

