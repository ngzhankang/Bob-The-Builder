# config files to load all secrets from .env
import os
from dotenv import load_dotenv

if os.path.exists(".env"):
    load_dotenv()

TELE_API_KEY = os.getenv("TG_BOT_API_TOKEN")
PERPLEXITY_API_KEY=os.getenv("PERPLEXITY_API_KEY")

if not TELE_API_KEY or not PERPLEXITY_API_KEY:
    raise ValueError("API tokens not found. Please check your .env file or environment variables.")