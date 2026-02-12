"""
Configuration module for API endpoints, constants, and environment variables.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment Configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "testnet").lower()
if ENVIRONMENT not in ["testnet", "production"]:
    raise ValueError(
        f"Invalid ENVIRONMENT: {ENVIRONMENT}. Must be 'testnet' or 'production'")

# Binance API Configuration
if ENVIRONMENT == "production":
    print("=" * 80)
    print("⚠️  WARNING: BOT CONFIGURED FOR PRODUCTION")
    print("Real trades will be executed. Be careful!")
    print("=" * 80)
    BINANCE_ENDPOINT = "https://fapi.binance.com"
    USE_TESTNET = False
else:
    BINANCE_ENDPOINT = "https://testnet.binancefuture.com"
    USE_TESTNET = True

# API Credentials (from environment variables)
API_KEY = os.getenv("BINANCE_API_KEY", "")
API_SECRET = os.getenv("BINANCE_API_SECRET", "")

# Validate API credentials are set
if not API_KEY or not API_SECRET:
    raise ValueError(
        "Missing API credentials! Set BINANCE_API_KEY and BINANCE_API_SECRET in .env"
    )

# Order Configuration
ALLOWED_ORDER_SIDES = ["BUY", "SELL"]
ALLOWED_ORDER_TYPES = ["MARKET", "LIMIT"]
LIMIT_ORDER_TIME_IN_FORCE = "GTC"  # Good-till-canceled

# Logging Configuration
LOG_DIR = "logs"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)
