import os
from dotenv import load_dotenv

load_dotenv()

AMAP_API_KEY = os.getenv("AMAP_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

if not AMAP_API_KEY:
    raise ValueError("AMAP_API_KEY is required. Please set it in .env file")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY is required. Please set it in .env file")
