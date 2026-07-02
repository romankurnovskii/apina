from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.v1.providers import router as providers_router

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(providers_router, prefix="/api/v1/providers", tags=["Providers"])


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.app_version}


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.app_name} API"}
