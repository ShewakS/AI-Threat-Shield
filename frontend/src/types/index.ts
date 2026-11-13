export type ThreatClass = 'Ham' | 'Spam' | 'Phishing';
export type ThreatLevel = 'LOW' | 'MEDIUM' | 'CRITICAL';
export type SignalSeverity = 'safe' | 'warning' | 'danger' | 'info';

export interface ThreatSignal {
  name: string;
  value: string | number;
  description: string;
  severity: SignalSeverity;
}

export interface URLStructureDetails {
  original_url: string;
  has_https: boolean;
  domain: string;
  url_length: number;
  dot_count: number;
  hyphen_count: number;
  slash_count: number;
  digit_count: number;
  special_char_count: number;
  suspicious_keywords_found: string[];
  is_ip_address: boolean;
}

export interface ScanResult {
  id: string;
  text_preview: string;
  predicted_class: ThreatClass;
  threat_level: ThreatLevel;
  confidence: number;
  threat_description: string;
  probabilities: {
    Ham: number;
    Spam: number;
    Phishing: number;
    [key: string]: number;
  };
  signals: ThreatSignal[];
  top_indicators: string[];
  security_advice: string[];
  processing_time_ms: number;
  timestamp: string;
}

export interface URLScanResult extends ScanResult {
  url_details: URLStructureDetails;
}

export interface BatchScanResult {
  total_scanned: number;
  threat_counts: {
    Ham: number;
    Spam: number;
    Phishing: number;
    [key: string]: number;
  };
  threat_percentages: {
    Ham: number;
    Spam: number;
    Phishing: number;
    [key: string]: number;
  };
  results: ScanResult[];
  total_processing_time_ms: number;
  timestamp: string;
}

export interface ModelInfo {
  model_name: string;
  model_family: string;
  task_type: string;
  classes: string[];
  feature_dimensions: {
    total_extracted_features: number;
    selected_features_k: number;
    feature_types: string[];
  };
  threat_level_definitions: {
    [key in ThreatClass]: {
      risk: string;
      badge: string;
      color: string;
    };
  };
  loaded_status: boolean;
  version: string;
}

export interface PresetSample {
  id: string;
  category: string;
  label: string;
  tag: string;
  type: 'email' | 'sms' | 'url';
  content: string;
}

export interface HealthStatus {
  status: 'healthy' | 'degraded';
  service: string;
  artifacts_loaded: boolean;
  model_name: string;
  uptime_seconds: number;
  version: string;
}
