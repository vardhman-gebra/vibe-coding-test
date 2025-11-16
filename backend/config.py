import logging

# Logging configuration
logging.basicConfig(level=logging.INFO)

# CORS settings
CORS_ORIGINS = ["*"]
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# API metadata
API_TITLE = "Vibe Coding API"
API_DESCRIPTION = "FastAPI backend for Vibe Coding application"
API_VERSION = "1.0.0"
