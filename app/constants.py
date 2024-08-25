import os

# API Configuration
API_KEY = os.getenv("API_KEY", "51Nj8UxKGLqm7Xt9Aw3RzBvF8qY6cJpL2tMn7DkZxC9Hs5EoVfGjTy2Lm1Rk3Pb8N")
API_KEY_NAME = "X-API-Key"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@postgres/scraper_db")

# Redis Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM_NUMBER = os.getenv("TWILIO_FROM_NUMBER")
TWILIO_TO_NUMBER = os.getenv("TWILIO_TO_NUMBER")

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Scraper Configuration
TARGET_URL = os.getenv("TARGET_URL", "https://dentalstall.com/shop/")

# Storage Configuration
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
IMAGE_SAVE_DIR = os.path.join(STORAGE_PATH, "images")

# Application Configuration
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Retry Configuration
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# HTML Classes
PRODUCT_CLASS = "product"
PRODUCT_TITLE_CLASS = "woo-loop-product__title"
PRODUCT_PRICE_CLASS = "woocommerce-Price-amount"
PRODUCT_IMAGE_CLASS = "attachment-woocommerce_thumbnail"
NEXT_PAGE_CLASS = "next.page-numbers"

# Cache Keys
PRODUCT_PRICE_CACHE_KEY = "product_price:{}"
