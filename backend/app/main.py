import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add backend directory to sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.routes.scan import router as scan_router
from app.routes.analytics import router as analytics_router
from app.routes.health import router as health_router
from app.services.detector_service import DetectorService

app = FastAPI(
    title="AI Threat Shield - Spam & Phishing Detection Engine API",
    description="Multi-class Machine Learning API for real-time classification of SMS, Emails, and URLs into Benign (Ham), Spam, and Malicious Phishing.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for frontend applications (Vite default is 5173 / 3000 / 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-load ML artifacts on startup
@app.on_event("startup")
async def startup_event():
    print("Initializing AI Detector Service...")
    service = DetectorService.get_instance()
    if service.artifacts_loaded:
        print("Detector Service initialized successfully with all model artifacts.")
    else:
        print("WARNING: Detector Service could not load model artifacts.")

# Mount routers
app.include_router(scan_router)
app.include_router(analytics_router)
app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "AI Threat Shield Spam & Phishing Detection API is operational",
        "docs": "/docs",
        "endpoints": [
            "/api/scan/text",
            "/api/scan/url",
            "/api/scan/batch",
            "/api/scan/upload",
            "/api/analytics/model",
            "/api/analytics/presets",
            "/api/analytics/history",
            "/api/health"
        ]
    }
