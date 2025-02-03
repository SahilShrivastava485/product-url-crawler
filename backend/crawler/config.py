import os

# Concurrency control
CONCURRENT_REQUESTS = 5
MAX_PRODUCT_LINKS = 100

# Redis and Celery settings
CELERY_BROKER = "redis://localhost:6379/0"
CELERY_BACKEND = "redis://localhost:6379/0"

# User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)"
]

# Product page patterns
PRODUCT_PATTERNS = [r"/product/", r"/item/", r"/p/"]
