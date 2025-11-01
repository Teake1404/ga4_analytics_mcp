"""
Configuration for Funnel Report Service
"""

import os

# Outlier detection threshold (±20% deviation from baseline)
OUTLIER_THRESHOLD = 0.20

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

