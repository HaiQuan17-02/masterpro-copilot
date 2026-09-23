from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router

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
app.include_router(chat_router, prefix="/api")
