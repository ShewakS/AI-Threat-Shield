from fastapi import APIRouter
from app.services.detector_service import DetectorService
import time

router = APIRouter(prefix="/api/health", tags=["Health & Status"])

START_TIME = time.time()

@router.get("")
async def health_check():
    service = DetectorService.get_instance()
    uptime_seconds = round(time.time() - START_TIME, 1)
    
    db_connected = service.db.is_connected() if service.db else False
    
    return {
        "status": "healthy" if service.artifacts_loaded else "degraded",
        "service": "AI Spam & Phishing Detection Engine",
        "artifacts_loaded": service.artifacts_loaded,
        "database_connected": db_connected,
        "database_type": "MongoDB (Localhost)",
        "model_name": service.metadata.get("model_name", "XGBoost"),
        "uptime_seconds": uptime_seconds,
        "version": "2.0.0"
    }
