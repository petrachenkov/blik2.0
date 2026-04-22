from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

from backend.config.settings import settings
from backend.database import init_db
from backend.routes import auth_router, tickets_router, admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    await init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Application shutting down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Система управления заявками на IT обслуживание",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(tickets_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Mount static files and templates for web interface
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
