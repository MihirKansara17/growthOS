from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.router import router as api_router
from app.seed.seed_data import seed_database

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Enable CORS for React frontend (Vercel / Netlify / local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    seed_database()

@app.get("/")
def root():
    return {
        "message": "GrowthOS V2 Decision Intelligence API is online",
        "docs": "/docs",
        "version": settings.VERSION
    }

app.include_router(api_router, prefix=settings.API_V1_STR)
