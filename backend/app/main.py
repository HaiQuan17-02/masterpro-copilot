from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router

app = FastAPI(
    title="MasterPro Copilot Backend API",
    description="FastAPI skeleton for MasterPro Copilot application",
    version="0.1.0",
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health_router, prefix="/api/v1")

@app.get("/", summary="Root Endpoint")
async def root():
    return {
        "message": "Welcome to MasterPro Copilot API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
