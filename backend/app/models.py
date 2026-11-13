from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1, description="SMS message, email text, or content to classify")
    source: Optional[str] = Field("auto", description="Source type: 'sms', 'email', 'url', or 'auto'")

class URLScanRequest(BaseModel):
    url: str = Field(..., min_length=3, description="URL string to scan for phishing & malicious patterns")

class BatchScanRequest(BaseModel):
    items: List[str] = Field(..., min_items=1, max_items=500, description="List of texts to classify in batch")

class ThreatSignal(BaseModel):
    name: str
    value: Any
    description: str
    severity: str  # 'safe', 'warning', 'danger', 'info'

class URLStructureDetails(BaseModel):
    original_url: str
    has_https: bool
    domain: str
    url_length: int
    dot_count: int
    hyphen_count: int
    slash_count: int
    digit_count: int
    special_char_count: int
    suspicious_keywords_found: List[str]
    is_ip_address: bool

class ScanResult(BaseModel):
    id: str
    text_preview: str
    predicted_class: str  # 'Ham', 'Spam', 'Phishing'
    threat_level: str     # 'LOW', 'MEDIUM', 'CRITICAL'
    confidence: float     # 0 - 100
    threat_description: str
    probabilities: Dict[str, float]  # {'Ham': 1.2, 'Spam': 98.1, 'Phishing': 0.7}
    signals: List[ThreatSignal]
    top_indicators: List[str]
    security_advice: List[str]
    processing_time_ms: float
    timestamp: str

class URLScanResult(ScanResult):
    url_details: URLStructureDetails

class BatchScanResult(BaseModel):
    total_scanned: int
    threat_counts: Dict[str, int]
    threat_percentages: Dict[str, float]
    results: List[ScanResult]
    total_processing_time_ms: float
    timestamp: str

class ModelInfo(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_name: str
    model_family: str
    task_type: str
    classes: List[str]
    feature_dimensions: Dict[str, Any]
    threat_level_definitions: Dict[str, Dict[str, str]]
    loaded_status: bool
    version: str
