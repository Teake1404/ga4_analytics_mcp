"""
Configuration management for GA4 Funnel Analysis MCP
Following SEO MCP pattern: environment variables, no hardcoded values
"""

import os
from dotenv import load_dotenv

# Load .env for local development
try:
    load_dotenv()
except ImportError:
    pass  # On Cloud Run, use environment variables directly

# ============================================================================
# API KEYS (CRITICAL: Use environment variables only!)
# ============================================================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or "sk-ant-api03-not-set-local-testing"
GA4_PROPERTY_ID = os.getenv("GA4_PROPERTY_ID")  # Optional default
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
SERANKING_API_TOKEN = os.getenv("SERANKING_API_TOKEN", "YOUR_SERANKING_API_TOKEN")

# GA4 OAuth2 Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8080/auth/callback")

# ============================================================================
# CLAUDE AI CONFIGURATION
# ============================================================================

# ⚠️ CRITICAL: Always use latest Sonnet 4.5 model
CLAUDE_MODEL = "claude-sonnet-4-5-20250929"
CLAUDE_MAX_TOKENS = 4096  # Increased for complete funnel insights (was getting truncated at 2048)

# ============================================================================
# FUNNEL ANALYSIS DEFAULTS (Can be overridden by API request)
# ============================================================================

# Default funnel steps (ecommerce standard)
DEFAULT_FUNNEL_STEPS = [
    "view_item",
    "add_to_cart",
    "purchase"
]

# Default dimensions to analyze (ALL 6 as requested by client)
DEFAULT_DIMENSIONS = [
    "sessionDefaultChannelGroup",  # channel: Organic Search, Social, Email, etc.
    "deviceCategory",              # device: desktop, mobile, tablet
    "browser",                     # browser: Chrome, Safari, Firefox, etc.
    "screenResolution",            # resolution: 1920x1080, 1366x768, etc.
    "itemName",                    # product: individual product names
    "itemCategory"                 # category: product categories
]

# Outlier detection threshold (±20% deviation from baseline)
OUTLIER_THRESHOLD = 0.20

# Default date range
DEFAULT_DATE_RANGE = "last_30_days"

# ============================================================================
# API CONFIGURATION
# ============================================================================

# Request timeout (5 minutes for GA4 API calls)
REQUEST_TIMEOUT = 300

# Rate limiting (if needed for GA4 API)
MIN_REQUEST_INTERVAL = 0.1  # 100ms between requests

# ============================================================================
# MOCK DATA CONFIGURATION (For prototype phase)
# ============================================================================

# Use mock data instead of real GA4 API
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "true").lower() == "true"

# ============================================================================
# LOGGING
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_config():
    """Validate critical configuration"""
    errors = []
    
    if not ANTHROPIC_API_KEY:
        errors.append("ANTHROPIC_API_KEY not set")
    
    if not USE_MOCK_DATA and not GA4_PROPERTY_ID:
        errors.append("GA4_PROPERTY_ID required when USE_MOCK_DATA=false")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")
    
    return True

