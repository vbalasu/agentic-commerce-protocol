"""
Main FastAPI application for ACP Demo
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.checkout import router as checkout_router
from .config import settings

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="Agentic Commerce Protocol (ACP) Demo with Stablecoin Payments",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(checkout_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Commerce Protocol (ACP) Demo API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)

