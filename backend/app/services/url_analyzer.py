import re
from urllib.parse import urlparse
from typing import List, Tuple, Dict, Any, Optional

# Top authoritative trusted global domains
TRUSTED_DOMAINS = {
    # Search & Major Tech
    "google.com", "google.co.in", "google.co.uk", "google.ca", "google.de", "google.fr",
    "google.it", "google.es", "google.co.jp", "google.com.au", "google.com.br",
    "youtube.com", "youtu.be", "gmail.com",
    "microsoft.com", "office.com", "office365.com", "live.com", "outlook.com", "bing.com", "msn.com",
    "apple.com", "icloud.com",
    "amazon.com", "amazon.in", "amazon.co.uk", "amazon.de", "amazon.co.jp", "amazon.ca", "aws.amazon.com",
    "github.com", "github.io", "gitlab.com", "bitbucket.org",
    "stackoverflow.com", "stackexchange.com",
    "wikipedia.org", "wikimedia.org", "wiktionary.org",
    "yahoo.com", "duckduckgo.com", "baidu.com",

    # Social & Communication
    "linkedin.com", "twitter.com", "x.com", "facebook.com", "fb.com", "instagram.com", "threads.net",
    "reddit.com", "pinterest.com", "tiktok.com", "quora.com", "medium.com", "tumblr.com",
    "netflix.com", "spotify.com", "twitch.tv", "vimeo.com", "soundcloud.com",
    "whatsapp.com", "telegram.org", "discord.com", "slack.com", "zoom.us", "skype.com",

    # Developer, Data Science & Cloud
    "python.org", "pypi.org", "npmjs.com", "npmjs.org", "nodejs.org",
    "cloudflare.com", "digitalocean.com", "heroku.com", "vercel.com", "netlify.com",
    "docker.com", "kubernetes.io", "apache.org", "nginx.org", "linux.org",
    "scikit-learn.org", "pytorch.org", "tensorflow.org", "kaggle.com",
    "fastapi.tiangolo.com", "react.dev", "reactjs.org", "vite.dev", "tailwindcss.com",
    "developer.mozilla.org", "w3schools.com", "geeksforgeeks.org", "gnu.org",

    # Business, Collaboration & Productivity
    "dropbox.com", "box.com", "notion.so", "figma.com", "canva.com", "trello.com",
    "atlassian.com", "jira.com", "salesforce.com",
    "adobe.com", "zendesk.com", "hubspot.com", "shopify.com", "stripe.com",
    "paypal.com", "ebay.com", "intuit.com",

    # News & Reference
    "nytimes.com", "bbc.com", "bbc.co.uk", "cnn.com", "reuters.com", "theguardian.com",
    "washingtonpost.com", "forbes.com", "bloomberg.com", "wsj.com", "techcrunch.com",
    "theverge.com", "wired.com", "arstechnica.com", "nature.com", "sciencedirect.com",
    "nih.gov", "cdc.gov", "who.int", "un.org"
}

TRUSTED_TLD_EXTENSIONS = (
    ".edu", ".gov", ".mil", ".edu.in", ".gov.in", ".ac.uk", ".gov.uk", ".edu.au", ".gov.au"
)

# Brands commonly targeted by spoofers in unverified domains
KNOWN_TARGET_BRANDS = [
    "wellsfargo", "paypal", "chase", "bankofamerica", "citibank", "citi", "barclays",
    "microsoft", "office365", "apple", "icloud", "netflix", "amazon", "google", "facebook",
    "instagram", "binance", "coinbase", "metamask", "kraken", "usps", "fedex", "dhl", "ups",
    "dropbox", "spotify", "ebay", "walmart", "target", "irs"
]

PHISH_INDICATORS = [
    "login", "signin", "verify", "verification", "auth", "security", "secure",
    "account", "suspended", "locked", "confirm", "update", "billing", "password",
    "passcode", "credential", "recovery", "unauthorized", "dispute", "webscr",
    "validate", "unlock", "reactivate", "restore"
]

SPAM_INDICATORS = [
    "lottery", "winner", "won", "cash", "prize", "claim", "free", "reward",
    "bonus", "million", "dollar", "crypto", "investment", "loan", "apr", "promo",
    "jackpot", "giveaway"
]

HIGH_RISK_TLDS = {
    ".xyz", ".top", ".buzz", ".club", ".work", ".click", ".link",
    ".tk", ".ml", ".ga", ".cf", ".gq", ".country", ".kim", ".loan"
}

SOCIAL_ENGINEERING_PHRASES = [
    "account suspended", "account locked", "temporarily suspended", "unauthorized login",
    "verify your identity", "verify your account", "verify your password", "restore full access",
    "action required within", "within 24 hours", "confirm your password", "provide your ssn",
    "security alert", "unauthorized transaction", "billing failure", "payment declined",
    "immediate action required"
]

def clean_url_str(url: str) -> str:
    u = str(url).strip()
    if not re.match(r'^[a-zA-Z]+://', u):
        u = 'http://' + u
    return u

def is_ip_host(host: str) -> bool:
    if not host:
        return False
    # Check IPv4
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', host.split(':')[0]))

def extract_host(url: str) -> Tuple[str, str, str]:
    """
    Returns (host, path, scheme) safely.
    """
    clean_u = clean_url_str(url)
    try:
        parsed = urlparse(clean_u)
        host = (parsed.hostname or parsed.netloc.split(':')[0]).lower()
        path = parsed.path.lower()
        scheme = parsed.scheme.lower()
        return host, path, scheme
    except Exception:
        parts = clean_u.replace('http://', '').replace('https://', '').split('/')
        return parts[0].lower(), '/' + '/'.join(parts[1:]).lower(), 'http'

def is_domain_trusted(host: str) -> Tuple[bool, Optional[str]]:
    """
    Checks if host belongs authentically to a trusted authority.
    """
    if not host or is_ip_host(host):
        return False, None

    # Check official academic/government TLDs
    for tld in TRUSTED_TLD_EXTENSIONS:
        if host.endswith(tld):
            return True, tld

    # Check trusted domain registry
    for td in TRUSTED_DOMAINS:
        if host == td or host.endswith('.' + td):
            return True, td

    return False, None

def check_brand_spoofing(host: str) -> Tuple[bool, Optional[str]]:
    """
    Detects if an unverified domain is impersonating a well-known brand.
    e.g. wellsfargo-verify.com, login-microsoft.xyz, paypal-update.net
    """
    is_trusted, _ = is_domain_trusted(host)
    if is_trusted:
        return False, None

    for brand in KNOWN_TARGET_BRANDS:
        if brand in host:
            return True, brand

    return False, None

def evaluate_url_safety(url: str) -> Dict[str, Any]:
    """
    Evaluates whether a URL is Trusted/Benign, Spam, or Phishing.
    """
    clean_u = clean_url_str(url)
    host, path, scheme = extract_host(clean_u)
    full_str = clean_u.lower()

    # 1. Direct IP Address Host
    if is_ip_host(host):
        return {
            "verdict": "Phishing",
            "threat_level": "CRITICAL",
            "confidence": 98.9,
            "probabilities": {"Ham": 0.5, "Spam": 0.6, "Phishing": 98.9},
            "reason": "Direct IP address host detected. Legitimate web services use domain names; raw IP hosts are a hallmark of phishing and malware delivery.",
            "is_trusted": False
        }

    # 2. Trusted Domain Authority Check
    is_trusted, matched_authority = is_domain_trusted(host)
    if is_trusted:
        # Verified authentic domain
        return {
            "verdict": "Ham",
            "threat_level": "LOW",
            "confidence": 99.2,
            "probabilities": {"Ham": 99.2, "Spam": 0.5, "Phishing": 0.3},
            "reason": f"Domain verified as an authentic, trusted global web authority ({matched_authority}). Content is safe and legitimate.",
            "is_trusted": True
        }

    # 3. Brand Impersonation / Typosquatting in Unverified Host
    is_spoofed, spoofed_brand = check_brand_spoofing(host)
    if is_spoofed:
        return {
            "verdict": "Phishing",
            "threat_level": "CRITICAL",
            "confidence": 99.1,
            "probabilities": {"Ham": 0.4, "Spam": 0.5, "Phishing": 99.1},
            "reason": f"Severe phishing threat: Deceptive domain spoofing brand '{spoofed_brand}' detected on unauthorized host '{host}'. High risk of credential theft.",
            "is_trusted": False
        }

    # 4. Phishing & Credential Theft Keywords in Host / Path
    found_phish_kw = [kw for kw in PHISH_INDICATORS if kw in host or kw in path]
    has_high_risk_tld = any(host.endswith(tld) for tld in HIGH_RISK_TLDS)

    if len(found_phish_kw) >= 2 or (len(found_phish_kw) >= 1 and has_high_risk_tld):
        matched_str = ", ".join(found_phish_kw[:3])
        return {
            "verdict": "Phishing",
            "threat_level": "CRITICAL",
            "confidence": 97.8,
            "probabilities": {"Ham": 1.2, "Spam": 1.0, "Phishing": 97.8},
            "reason": f"Suspicious credential harvesting cues detected in unverified domain/path ({matched_str}). Caution: do not enter passwords.",
            "is_trusted": False
        }

    # 5. Spam / Prize / Commercial Lure Keywords
    found_spam_kw = [kw for kw in SPAM_INDICATORS if kw in host or kw in path]
    if len(found_spam_kw) >= 2 or (len(found_spam_kw) >= 1 and has_high_risk_tld):
        matched_str = ", ".join(found_spam_kw[:3])
        return {
            "verdict": "Spam",
            "threat_level": "MEDIUM",
            "confidence": 97.0,
            "probabilities": {"Ham": 2.0, "Spam": 97.0, "Phishing": 1.0},
            "reason": f"Promotional prize or lottery lure patterns detected in unverified URL ({matched_str}).",
            "is_trusted": False
        }

    # 6. Standard Benign Domain (Ordinary website without threats)
    return {
        "verdict": "Ham",
        "threat_level": "LOW",
        "confidence": 95.0,
        "probabilities": {"Ham": 95.0, "Spam": 3.0, "Phishing": 2.0},
        "reason": "Standard web destination. No brand spoofing, anomalous credential harvesting cues, or deceptive patterns detected.",
        "is_trusted": False
    }

def extract_urls_from_text(text: str) -> List[str]:
    """
    Extracts all URLs and domain-like links from a text message.
    """
    # 1. Standard http(s) URLs
    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
    # 2. Root domain-like patterns: e.g. github.com/repo, google.com
    bare_domains = re.findall(r'\b[a-zA-Z0-9-]+\.(?:com|org|net|io|edu|gov|co|xyz|top|me)(?:/[^\s<>"]*)?\b', text)
    
    combined = list(dict.fromkeys(urls + bare_domains))
    return combined

def analyze_message_content(text: str, ml_predicted_class: str, ml_probabilities: Dict[str, float]) -> Dict[str, Any]:
    """
    Calibrates message predictions by analyzing embedded URLs and social engineering patterns.
    Prevents false positives on trusted URLs (like github.com or google.com in normal conversation).
    """
    text_lower = text.lower()
    urls = extract_urls_from_text(text)

    # 1. Check if message contains high-risk social engineering attack phrases
    has_social_eng = any(phrase in text_lower for phrase in SOCIAL_ENGINEERING_PHRASES)
    has_lottery_scam = any(phrase in text_lower for phrase in ["you won", "$1,000,000", "lottery prize", "cash draw", "claim prize"])

    # 2. Check embedded URLs
    url_evaluations = [evaluate_url_safety(u) for u in urls]
    any_phish_url = any(e['verdict'] == 'Phishing' for e in url_evaluations)
    any_spam_url = any(e['verdict'] == 'Spam' for e in url_evaluations)
    all_trusted_urls = len(urls) > 0 and all(e['is_trusted'] for e in url_evaluations)

    # Case A: An embedded URL is genuinely malicious / spoofed
    if any_phish_url:
        return {
            "override": True,
            "verdict": "Phishing",
            "threat_level": "CRITICAL",
            "confidence": 98.8,
            "probabilities": {"Ham": 0.5, "Spam": 0.7, "Phishing": 98.8},
            "reason": "Phishing attack detected: Message contains an unverified, deceptive link designed to harvest credentials or impersonate a brand."
        }

    # Case B: Embedded URLs are all verified trusted authorities (e.g. github, google, zoom)
    # AND message has NO social engineering threats
    if all_trusted_urls and not has_social_eng and not has_lottery_scam:
        # Correct false positive
        return {
            "override": True,
            "verdict": "Ham",
            "threat_level": "LOW",
            "confidence": 98.5,
            "probabilities": {"Ham": 98.5, "Spam": 1.0, "Phishing": 0.5},
            "reason": "Verified legitimate communication. Embedded links point to recognized trusted web authorities with no social engineering attack patterns detected."
        }

    # Case C: Genuine social engineering threat in text
    if has_social_eng:
        return {
            "override": True,
            "verdict": "Phishing",
            "threat_level": "CRITICAL",
            "confidence": 98.5,
            "probabilities": {"Ham": 0.8, "Spam": 0.7, "Phishing": 98.5},
            "reason": "Social engineering attack detected: Message uses urgent account suspension or credential verification threats."
        }

    if has_lottery_scam:
        return {
            "override": True,
            "verdict": "Spam",
            "threat_level": "MEDIUM",
            "confidence": 99.2,
            "probabilities": {"Ham": 0.5, "Spam": 99.2, "Phishing": 0.3},
            "reason": "Unsolicited lottery or cash prize scam detected."
        }

    # Otherwise keep ML output
    return {"override": False}

