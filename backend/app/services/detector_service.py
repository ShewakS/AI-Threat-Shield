import os
import re
import sys
import time
import uuid
import numpy as np
import pandas as pd
import scipy.sparse as sp
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add backend directory to sys.path to ensure src imports work seamlessly
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from src.artifact_manager import ArtifactManager
from src.feature_engineering import FeatureEngineer, SUSPICIOUS_KEYWORDS
from src.feature_selector import FeatureSelector
from app.services.url_analyzer import (
    evaluate_url_safety,
    analyze_message_content,
    extract_urls_from_text,
    extract_host,
    is_domain_trusted,
    check_brand_spoofing,
    is_ip_host
)
from app.models import (
    ScanResult,
    URLScanResult,
    BatchScanResult,
    ThreatSignal,
    URLStructureDetails,
    ModelInfo
)
from app.database import MongoDatabase

CLASS_NAMES = {0: 'Ham', 1: 'Spam', 2: 'Phishing'}

THREAT_DETAILS = {
    'Ham': {
        'level': 'LOW',
        'desc': 'Minimal security risk detected. Content appears benign and legitimate.',
        'advice': [
            'No immediate mitigation required.',
            'Message aligns with standard benign communication patterns.',
            'Maintain regular cyber hygiene and verify senders when in doubt.'
        ]
    },
    'Spam': {
        'level': 'MEDIUM',
        'desc': 'Unsolicited promotional, commercial, or nuisance content detected. Caution advised.',
        'advice': [
            'Do not engage with promotional links or unverified sales pitches.',
            'Mark or move this item to your Spam/Junk folder.',
            'Avoid replying to unsubscribe messages from unverified sources.'
        ]
    },
    'Phishing': {
        'level': 'CRITICAL',
        'desc': 'Severe security threat! High probability of credential harvesting, spoofing, or malware delivery.',
        'advice': [
            'CRITICAL: Do NOT click any links, open attachments, or disclose credentials.',
            'Verify the sender domain directly via official secondary channels.',
            'If passwords or credentials were submitted, reset them immediately and enable 2FA/MFA.',
            'Report this threat to your organizational IT Security / SOC department.'
        ]
    }
}

class DetectorService:
    _instance = None

    def __init__(self, artifact_dir: Optional[str] = None):
        if artifact_dir is None:
            artifact_dir = os.path.join(backend_dir, 'artifacts')
        self.artifact_dir = artifact_dir
        self.artifacts_loaded = False
        self.best_model = None
        self.feature_engineer = None
        self.feature_selector = None
        self.metadata = {}
        self.history: List[Dict[str, Any]] = []
        self.db = MongoDatabase.get_instance()
        self._load_artifacts()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DetectorService()
        return cls._instance

    def _load_artifacts(self):
        try:
            print(f"[DetectorService] Loading ML artifacts from: {self.artifact_dir}")
            mgr = ArtifactManager(artifact_dir=self.artifact_dir)
            loaded = mgr.load_artifacts()
            self.best_model = loaded['best_model']
            self.feature_engineer = loaded['feature_engineer']
            self.feature_selector = loaded['feature_selector']
            self.metadata = loaded['metadata']
            self.artifacts_loaded = True
            print(f"[DetectorService] Successfully loaded model: {self.metadata.get('model_name', 'XGBoost')}")
        except Exception as e:
            print(f"[DetectorService] Error loading artifacts: {e}")
            self.artifacts_loaded = False

    def _extract_threat_signals(self, text: str) -> List[ThreatSignal]:
        signals = []
        text_lower = text.lower()

        # 1. Suspicious keywords detection
        found_kw = [kw for kw in SUSPICIOUS_KEYWORDS if kw in text_lower]
        if found_kw:
            signals.append(ThreatSignal(
                name="Suspicious Keywords",
                value=", ".join(found_kw[:6]) + (f" (+{len(found_kw)-6} more)" if len(found_kw) > 6 else ""),
                description=f"Detected {len(found_kw)} high-risk social engineering keywords often used in phishing lures.",
                severity="danger" if len(found_kw) >= 2 else "warning"
            ))
        else:
            signals.append(ThreatSignal(
                name="Suspicious Keywords",
                value="None Detected",
                description="No common high-risk phishing trigger words detected in text body.",
                severity="safe"
            ))

        # 2. URL and Link Analysis
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[^\s]*', text)
        if urls:
            url_evals = [evaluate_url_safety(u) for u in urls]
            has_phish = any(e['verdict'] == 'Phishing' for e in url_evals)
            all_safe = all(e['verdict'] == 'Ham' for e in url_evals)
            has_http_only = any(u.startswith('http://') for u in urls)

            if has_phish:
                signals.append(ThreatSignal(
                    name="Embedded URLs",
                    value=f"{len(urls)} Deceptive Link(s)",
                    description="Contains suspicious or brand-spoofing links indicative of credential harvesting.",
                    severity="danger"
                ))
            elif all_safe:
                signals.append(ThreatSignal(
                    name="Embedded URLs",
                    value=f"{len(urls)} Verified Safe Link(s)",
                    description="Embedded hyperlinks point to authenticated, reputable web domains.",
                    severity="safe"
                ))
            else:
                signals.append(ThreatSignal(
                    name="Embedded URLs",
                    value=f"{len(urls)} Link(s) Found",
                    description=f"Contains embedded web hyperlinks ({'Unencrypted HTTP present' if has_http_only else 'HTTPS used'}).",
                    severity="danger" if has_http_only else "warning"
                ))
        else:
            signals.append(ThreatSignal(
                name="Embedded URLs",
                value="None",
                description="No active hyperlinks detected inside the message content.",
                severity="safe"
            ))

        # 3. Uppercase & Urgency Density
        char_count = len(text)
        upper_count = sum(1 for c in text if c.isupper())
        upper_ratio = (upper_count / (char_count + 1e-5)) * 100.0
        if upper_ratio > 18.0:
            signals.append(ThreatSignal(
                name="Capitalization & Urgency",
                value=f"{upper_ratio:.1f}% Uppercase",
                description="High ratio of capital letters frequently used to fabricate false urgency or bypass spam heuristics.",
                severity="warning"
            ))
        else:
            signals.append(ThreatSignal(
                name="Capitalization",
                value=f"{upper_ratio:.1f}% Uppercase",
                description="Normal casing pattern consistent with regular communication.",
                severity="safe"
            ))

        # 4. Sentiment & Tone Polarity
        if hasattr(self.feature_engineer, 'vader'):
            try:
                sent = self.feature_engineer.vader.polarity_scores(text)
                compound = sent['compound']
                if compound <= -0.5:
                    signals.append(ThreatSignal(
                        name="Sentiment Tone",
                        value=f"Negative (Score: {compound:.2f})",
                        description="Aggressive or coercive emotional tone indicative of coercive extortion or account suspension alerts.",
                        severity="warning"
                    ))
                elif compound >= 0.7:
                    signals.append(ThreatSignal(
                        name="Sentiment Tone",
                        value=f"Overly Positive (Score: {compound:.2f})",
                        description="Exaggerated positive excitement indicative of prize/lottery lure spam.",
                        severity="warning"
                    ))
                else:
                    signals.append(ThreatSignal(
                        name="Sentiment Tone",
                        value=f"Neutral (Score: {compound:.2f})",
                        description="Balanced linguistic tone.",
                        severity="safe"
                    ))
            except Exception:
                pass

        return signals

    def _dissect_url(self, url: str) -> URLStructureDetails:
        url_str = str(url).strip()
        has_https = url_str.lower().startswith("https://")
        
        # Domain extraction
        domain_match = re.search(r'https?://([^/:\s]+)', url_str)
        domain = domain_match.group(1) if domain_match else url_str.split('/')[0]

        # IP in URL check
        is_ip = bool(re.match(r'^(?:http://|https://)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_str))

        # Suspicious keywords in URL
        found_kw = [kw for kw in SUSPICIOUS_KEYWORDS if kw in url_str.lower()]

        return URLStructureDetails(
            original_url=url_str,
            has_https=has_https,
            domain=domain,
            url_length=len(url_str),
            dot_count=url_str.count('.'),
            hyphen_count=url_str.count('-'),
            slash_count=url_str.count('/'),
            digit_count=sum(c.isdigit() for c in url_str),
            special_char_count=sum(1 for c in url_str if c in "@?=%&_~"),
            suspicious_keywords_found=found_kw,
            is_ip_address=is_ip
        )

    def scan_text(self, text: str, source: str = "auto") -> ScanResult:
        if not self.artifacts_loaded:
            raise RuntimeError("Model artifacts are not loaded.")

        start_time = time.time()
        input_text = text.strip()

        # Check if the text is purely a standalone URL
        is_pure_url = (source == "url") or (
            len(input_text.split()) == 1 and (
                bool(re.match(r'^(?:https?://|www\.)', input_text, re.IGNORECASE)) or
                any(input_text.lower().endswith(ext) or (ext + '/') in input_text.lower()
                    for ext in ['.com', '.org', '.net', '.edu', '.gov', '.io', '.dev', '.app', '.co', '.in', '.uk'])
            )
        )

        if is_pure_url:
            url_eval = evaluate_url_safety(input_text)
            pred_class = url_eval["verdict"]
            threat_level = url_eval["threat_level"]
            confidence = url_eval["confidence"]
            probabilities = url_eval["probabilities"]
            threat_desc = url_eval["reason"]
            threat_info = THREAT_DETAILS.get(pred_class, THREAT_DETAILS['Ham'])
            signals = self._extract_threat_signals(input_text)
            
            if url_eval["is_trusted"]:
                top_indicators = ["Domain Authority: Verified Global Entity", "Reputation: Safe / Trusted", "Content: Benign URL"]
            elif pred_class == "Phishing":
                top_indicators = ["Security Warning: Phishing Pattern", "Deceptive Host or Keyword Match", "Risk: High-Threat URL"]
            else:
                top_indicators = ["Category: Promotional / Suspicious", "Confidence: High", "Status: Unverified Destination"]
        else:
            df_sample = pd.DataFrame([{'text': input_text}])

            # Feature Transformation
            feats = self.feature_engineer.transform(df_sample)
            feats_sel = self.feature_selector.transform(feats)

            # Model Prediction
            pred_idx = int(self.best_model.predict(feats_sel)[0])
            pred_class = CLASS_NAMES.get(pred_idx, 'Unknown')

            # Probabilities
            probabilities = {'Ham': 0.0, 'Spam': 0.0, 'Phishing': 0.0}
            confidence = 100.0

            if hasattr(self.best_model, 'predict_proba'):
                try:
                    proba_arr = self.best_model.predict_proba(feats_sel)[0]
                    confidence = float(np.max(proba_arr)) * 100.0
                    for idx, prob in enumerate(proba_arr):
                        c_name = CLASS_NAMES.get(idx, f"Class_{idx}")
                        probabilities[c_name] = round(float(prob) * 100.0, 2)
                except Exception:
                    probabilities[pred_class] = 100.0
            else:
                probabilities[pred_class] = 100.0

            # Calibrate with message content analyzer to prevent false positives on trusted links
            cal = analyze_message_content(input_text, pred_class, probabilities)
            if cal.get("override"):
                pred_class = cal["verdict"]
                threat_info = THREAT_DETAILS.get(pred_class, THREAT_DETAILS['Ham'])
                threat_level = cal["threat_level"]
                confidence = cal["confidence"]
                probabilities = cal["probabilities"]
                threat_desc = cal["reason"]
            else:
                threat_info = THREAT_DETAILS.get(pred_class, THREAT_DETAILS['Ham'])
                threat_level = threat_info['level']
                threat_desc = threat_info['desc']

            signals = self._extract_threat_signals(input_text)

            # Feature indicators / influential tokens
            top_indicators = []
            try:
                if hasattr(self.best_model, 'feature_importances_'):
                    selected_names = [self.feature_engineer.feature_names[i] for i in self.feature_selector.selected_indices]
                    if sp.issparse(feats_sel):
                        dense_sample = feats_sel.toarray()[0]
                    else:
                        dense_sample = feats_sel[0]
                    active_indices = np.where(dense_sample > 0)[0]
                    if len(active_indices) > 0:
                        importances = self.best_model.feature_importances_[active_indices]
                        top_local = active_indices[np.argsort(importances)[::-1][:4]]
                        for idx in top_local:
                            fname = selected_names[idx].replace('tfidf_', 'token:')
                            top_indicators.append(f"{fname}")
            except Exception:
                pass

            if not top_indicators:
                if signals:
                    top_indicators = [f"{s.name}: {s.value}" for s in signals if s.severity in ['warning', 'danger']][:3]

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        scan_id = str(uuid.uuid4())[:8]

        result = ScanResult(
            id=scan_id,
            text_preview=input_text[:120] + ("..." if len(input_text) > 120 else ""),
            predicted_class=pred_class,
            threat_level=threat_level,
            confidence=round(confidence, 2),
            threat_description=threat_desc,
            probabilities=probabilities,
            signals=signals,
            top_indicators=top_indicators,
            security_advice=threat_info['advice'],
            processing_time_ms=elapsed_ms,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

        # Save to database (MongoDB)
        scan_dict = result.dict()
        if self.db and self.db.is_connected():
            self.db.save_scan(scan_dict)

        # Store in recent history (in-memory, keep last 100)
        self.history.insert(0, scan_dict)
        if len(self.history) > 100:
            self.history.pop()

        return result

    def scan_url(self, url: str) -> URLScanResult:
        start_time = time.time()
        clean_u = url.strip()
        url_details = self._dissect_url(clean_u)
        url_eval = evaluate_url_safety(clean_u)

        verdict = url_eval["verdict"]
        threat_level = url_eval["threat_level"]
        confidence = url_eval["confidence"]
        probabilities = url_eval["probabilities"]
        threat_desc = url_eval["reason"]
        threat_info = THREAT_DETAILS.get(verdict, THREAT_DETAILS['Ham'])

        host, path, scheme = extract_host(clean_u)
        is_trusted, matched_authority = is_domain_trusted(host)
        is_spoofed, spoofed_brand = check_brand_spoofing(host)
        is_ip = is_ip_host(host)

        # Specialized Threat Signals for URL
        url_signals: List[ThreatSignal] = []

        # 1. Domain Authority & Identity
        if is_trusted:
            url_signals.append(ThreatSignal(
                name="Domain Authority",
                value=f"Verified Authority ({matched_authority})",
                description="Legitimate, officially authenticated web domain belonging to a recognized global entity.",
                severity="safe"
            ))
        elif is_spoofed:
            url_signals.append(ThreatSignal(
                name="Domain Impersonation",
                value=f"Brand Spoofing ({spoofed_brand})",
                description=f"Deceptive domain unauthorizedly impersonating '{spoofed_brand}'. Severe risk of credential theft.",
                severity="danger"
            ))
        elif is_ip:
            url_signals.append(ThreatSignal(
                name="Host Identity",
                value=f"Raw IP ({host})",
                description="Direct numeric IP address host detected. Phishing campaigns frequently use raw IPs to evade reputation filters.",
                severity="danger"
            ))
        else:
            url_signals.append(ThreatSignal(
                name="Domain Registration",
                value=host or "Unregistered Host",
                description="Standard domain registration without known authority affiliation or immediate spoofing indicators.",
                severity="safe" if verdict == "Ham" else "warning"
            ))

        # 2. SSL/TLS Transport Security
        if url_details.has_https:
            url_signals.append(ThreatSignal(
                name="Transport Security",
                value="HTTPS Encrypted",
                description="Secure SSL/TLS encrypted transmission channel between client and server.",
                severity="safe"
            ))
        else:
            url_signals.append(ThreatSignal(
                name="Transport Security",
                value="Plain HTTP (Unencrypted)",
                description="Insecure plaintext connection vulnerable to interception and traffic spoofing.",
                severity="danger" if verdict == "Phishing" else "warning"
            ))

        # 3. Structural Complexity
        if url_details.dot_count > 3 or url_details.hyphen_count > 2 or url_details.special_char_count > 2:
            url_signals.append(ThreatSignal(
                name="Structural Complexity",
                value=f"{url_details.dot_count} dots, {url_details.hyphen_count} hyphens",
                description="Elevated structural complexity and obfuscation typical of deceptive phishing redirects.",
                severity="danger" if verdict == "Phishing" else "warning"
            ))
        else:
            url_signals.append(ThreatSignal(
                name="URL Structure",
                value="Standard Structure",
                description="URL length and component hierarchy conform to standard web standards.",
                severity="safe"
            ))

        # 4. Keyword / Heuristic Signals
        if url_details.suspicious_keywords_found:
            url_signals.append(ThreatSignal(
                name="Deceptive Indicators",
                value=", ".join(url_details.suspicious_keywords_found[:4]),
                description="Detected credential, banking, or urgent authentication keywords in the URL path.",
                severity="danger" if verdict == "Phishing" else "warning"
            ))
        else:
            url_signals.append(ThreatSignal(
                name="Deceptive Indicators",
                value="None Detected",
                description="No credential-harvesting or deceptive lure keywords identified.",
                severity="safe"
            ))

        # Top indicators
        if is_trusted:
            top_indicators = [
                f"Authority: {matched_authority}",
                "Transport: HTTPS Encrypted" if url_details.has_https else "Transport: HTTP",
                "Integrity: Verified Clean Domain"
            ]
        elif is_spoofed:
            top_indicators = [
                f"Brand Spoofing: {spoofed_brand}",
                f"Unauthorized Host: {host}",
                "Risk: Credential Harvesting Lure"
            ]
        elif is_ip:
            top_indicators = [
                f"Raw IP Hostname: {host}",
                "Risk: Evasion of Domain Reputation",
                "Protocol: " + ("HTTPS" if url_details.has_https else "Plain HTTP")
            ]
        else:
            top_indicators = [
                f"Domain: {host}",
                "Structure: " + ("Complex / Suspicious" if url_details.dot_count > 3 else "Normal"),
                f"Verdict: {verdict}"
            ]

        elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
        scan_id = str(uuid.uuid4())[:8]

        url_result = URLScanResult(
            id=scan_id,
            text_preview=clean_u[:120] + ("..." if len(clean_u) > 120 else ""),
            predicted_class=verdict,
            threat_level=threat_level,
            confidence=round(confidence, 2),
            threat_description=threat_desc,
            probabilities=probabilities,
            signals=url_signals,
            top_indicators=top_indicators,
            security_advice=threat_info['advice'],
            processing_time_ms=elapsed_ms,
            timestamp=datetime.utcnow().isoformat() + "Z",
            url_details=url_details
        )

        # Save to MongoDB
        url_scan_dict = url_result.dict()
        if self.db and self.db.is_connected():
            self.db.save_scan(url_scan_dict)

        # Store in recent history
        self.history.insert(0, url_scan_dict)
        if len(self.history) > 100:
            self.history.pop()

        return url_result

    def scan_batch(self, items: List[str]) -> BatchScanResult:
        start_time = time.time()
        results: List[ScanResult] = []
        threat_counts = {'Ham': 0, 'Spam': 0, 'Phishing': 0}

        for item in items:
            cleaned = str(item).strip()
            if not cleaned:
                continue
            res = self.scan_text(cleaned)
            results.append(res)
            c_name = res.predicted_class
            threat_counts[c_name] = threat_counts.get(c_name, 0) + 1

        total = len(results)
        percentages = {
            k: round((v / (total + 1e-5)) * 100.0, 1) for k, v in threat_counts.items()
        }
        total_time_ms = round((time.time() - start_time) * 1000.0, 2)

        return BatchScanResult(
            total_scanned=total,
            threat_counts=threat_counts,
            threat_percentages=percentages,
            results=results,
            total_processing_time_ms=total_time_ms,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )

    def get_model_info(self) -> ModelInfo:
        return ModelInfo(
            model_name=self.metadata.get('model_name', 'XGBoost Multi-Class Classifier'),
            model_family="Extreme Gradient Boosting Ensemble with TF-IDF & Linguistic Features",
            task_type="Multi-class Spam & Phishing Detection (Ham vs Spam vs Phishing)",
            classes=['Ham', 'Spam', 'Phishing'],
            feature_dimensions={
                'total_extracted_features': len(self.feature_engineer.feature_names) if self.feature_engineer else 5020,
                'selected_features_k': len(self.feature_selector.selected_indices) if self.feature_selector else 3000,
                'feature_types': [
                    'TF-IDF Word & Character N-Grams (1-2 gram)',
                    'URL Structural Heuristics (HTTPS, Dots, Hyphens, Special Symbols)',
                    'Text Statistical Attributes (Length, Uppercase Density, Punctuation Density)',
                    'VADER Sentiment Polarity & Compound Scoring',
                    'Stopword & Lexical Length Metrics'
                ]
            },
            threat_level_definitions={
                'Ham': {'risk': 'LOW', 'badge': 'Safe', 'color': '#10B981'},
                'Spam': {'risk': 'MEDIUM', 'badge': 'Spam / Commercial', 'color': '#F59E0B'},
                'Phishing': {'risk': 'CRITICAL', 'badge': 'Malicious Phishing', 'color': '#EF4444'}
            },
            loaded_status=self.artifacts_loaded,
            version="2.0.0"
        )

    def get_recent_scans(self, limit: int = 100) -> List[Dict[str, Any]]:
        # Fetch from MongoDB if available
        if self.db and self.db.is_connected():
            db_scans = self.db.get_recent_scans(limit=limit)
            if db_scans:
                return db_scans
        return self.history[:limit]

    def get_scan_counts(self) -> Dict[str, int]:
        if self.db and self.db.is_connected():
            return self.db.get_counts()
        
        counts = {"Ham": 0, "Spam": 0, "Phishing": 0, "total": len(self.history)}
        for item in self.history:
            c = item.get("predicted_class")
            if c in counts:
                counts[c] += 1
        return counts

    def clear_history(self) -> bool:
        self.history.clear()
        if self.db and self.db.is_connected():
            return self.db.clear_all()
        return True
