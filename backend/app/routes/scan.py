import io
import csv
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from app.models import (
    ScanRequest,
    ScanResult,
    URLScanRequest,
    URLScanResult,
    BatchScanRequest,
    BatchScanResult
)
from app.services.detector_service import DetectorService

router = APIRouter(prefix="/api/scan", tags=["Scanning"])

@router.post("/text", response_model=ScanResult)
async def scan_single_text(req: ScanRequest):
    try:
        service = DetectorService.get_instance()
        result = service.scan_text(req.text, source=req.source or "auto")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@router.post("/url", response_model=URLScanResult)
async def scan_single_url(req: URLScanRequest):
    try:
        service = DetectorService.get_instance()
        result = service.scan_url(req.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"URL inspection error: {str(e)}")

@router.post("/batch", response_model=BatchScanResult)
async def scan_batch_texts(req: BatchScanRequest):
    try:
        service = DetectorService.get_instance()
        result = service.scan_batch(req.items)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scan error: {str(e)}")

@router.post("/upload", response_model=BatchScanResult)
async def scan_uploaded_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text_content = contents.decode("utf-8", errors="ignore")
        items = []

        if file.filename.endswith(".csv"):
            csv_reader = csv.reader(io.StringIO(text_content))
            header = next(csv_reader, None)
            
            # Find the text column or use column 0
            text_col_idx = 0
            if header:
                for idx, col in enumerate(header):
                    if col.lower() in ["text", "message", "body", "email", "url", "content", "sms"]:
                        text_col_idx = idx
                        break
            
            for row in csv_reader:
                if row and len(row) > text_col_idx:
                    val = row[text_col_idx].strip()
                    if val:
                        items.append(val)
                if len(items) >= 200:  # Safety cap for batch demo
                    break
        else:
            # Plain text file (one line per entry)
            lines = text_content.splitlines()
            for line in lines:
                val = line.strip()
                if val:
                    items.append(val)
                if len(items) >= 200:
                    break

        if not items:
            raise HTTPException(status_code=400, detail="No readable text rows found in uploaded file.")

        service = DetectorService.get_instance()
        return service.scan_batch(items)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing error: {str(e)}")
