import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.routes import voter, verification, alerts, logs
from app.core.config import settings
from app.db.session import engine
from app.db import base  # noqa: F401 - needed for model registration
from app.db.init_db import init_db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("Starting Secure Smart Voting Verification System backend...")
    await init_db()
    logger.info("Database initialized successfully.")
    yield
    # shutdown
    logger.info("Shutting down backend...")


app = FastAPI(
    title="Secure Smart Voting Verification System",
    description="Multi-layer biometric voter verification API",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# --- Routers ---
app.include_router(voter.router, prefix="/api/v1/voters", tags=["Voters"])
app.include_router(verification.router, prefix="/api/v1/verification", tags=["Verification"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Audit Logs"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "service": "SSVVS Backend"}
