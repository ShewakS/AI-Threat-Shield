from typing import List, Dict, Any
from fastapi import APIRouter
from app.models import ModelInfo
from app.services.detector_service import DetectorService

router = APIRouter(prefix="/api/analytics", tags=["Analytics & Metadata"])

PRESET_TEST_CASES = [
    {
        "id": "phishing-bank",
        "category": "Phishing",
        "label": "Urgent Bank Security Alert",
        "tag": "Credential Theft",
        "type": "email",
        "content": "URGENT SECURITY ALERT: Your Wells Fargo online account has been temporarily suspended due to unauthorized login attempts. Click https://wellsfargo-verify-security-login.com/auth immediately to verify your identity, password, and SSN to restore full access within 24 hours."
    },
    {
        "id": "phishing-paypal",
        "category": "Phishing",
        "label": "PayPal Unauthorized Transaction",
        "tag": "Spoofed Portal",
        "type": "email",
        "content": "Dear Customer, You sent a payment of $849.00 USD to CryptoWorld Ltd. If you did not make this transaction, please cancel it immediately by visiting our secure resolution center at http://paypal-dispute-cancellation.net/signin."
    },
    {
        "id": "spam-lottery",
        "category": "Spam",
        "label": "Mega Lottery Winner SMS",
        "tag": "Prize Scam",
        "type": "sms",
        "content": "CONGRATULATIONS! Your mobile number has been selected as the WINNER of $1,000,000 in the 2026 International Cash Draw! Text CLAIM to 88442 now or visit http://freeprizes.xyz to receive your check!"
    },
    {
        "id": "spam-promo",
        "category": "Spam",
        "label": "Exclusive Loan Offer",
        "tag": "Commercial Unsolicited",
        "type": "sms",
        "content": "Pre-approved! Get an instant personal loan up to $50,000 with 0% introductory APR. Limited time flash offer. Reply YES to accept or STOP to unsubscribe."
    },
    {
        "id": "ham-meeting",
        "category": "Ham",
        "label": "Team Sprint Planning Memo",
        "tag": "Legitimate Email",
        "type": "email",
        "content": "Hi Team, Let's meet tomorrow at 10:00 AM in Conference Room B for our sprint retrospective and quarterly planning. Please update your Jira tickets and review the roadmap document beforehand. Thanks, Sarah."
    },
    {
        "id": "ham-order",
        "category": "Ham",
        "label": "E-Commerce Shipping Confirmation",
        "tag": "Legitimate Notification",
        "type": "email",
        "content": "Hello Alex, your order #893214 has shipped via UPS Ground (Tracking: 1Z9999999999999999). Estimated delivery is Thursday by 7:00 PM. Thank you for shopping with us!"
    },
    {
        "id": "url-phishing",
        "category": "Phishing URL",
        "label": "Fake Microsoft Login Portal",
        "tag": "Malicious URL",
        "type": "url",
        "content": "http://192.168.1.105/microsoft-office365-login-verify-account/auth.php"
    },
    {
        "id": "url-safe",
        "category": "Safe URL",
        "label": "GitHub Repository Documentation",
        "tag": "Safe URL",
        "type": "url",
        "content": "https://github.com/scikit-learn/scikit-learn/blob/main/README.md"
    }
]

@router.get("/model", response_model=ModelInfo)
async def get_model_information():
    service = DetectorService.get_instance()
    return service.get_model_info()

@router.get("/presets")
async def get_preset_samples():
    return PRESET_TEST_CASES

@router.get("/history")
async def get_scan_history(limit: int = 100):
    service = DetectorService.get_instance()
    history = service.get_recent_scans(limit=limit)
    counts = service.get_scan_counts()
    
    return {
        "total_scans": counts.get("total", len(history)),
        "breakdown": {
            "Ham": counts.get("Ham", 0),
            "Spam": counts.get("Spam", 0),
            "Phishing": counts.get("Phishing", 0)
        },
        "history": history
    }

@router.delete("/history")
async def clear_scan_history():
    service = DetectorService.get_instance()
    success = service.clear_history()
    return {"status": "cleared" if success else "error"}
