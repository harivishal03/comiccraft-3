"""Central configuration: paths and environment variables."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"
FONT_PATH = STATIC_DIR / "fonts" / "DejaVuSans.ttf"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
HF_API_KEY = os.getenv("HF_API_KEY", "")

GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "models/gemini-2.5-flash")
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "models/gemini-2.5-pro")
SD_MODEL_ID = os.getenv("SD_MODEL_ID", "stable-diffusion-v1-5/stable-diffusion-v1-5")

for _folder in (PANELS_DIR, EXPORTS_DIR):
    _folder.mkdir(parents=True, exist_ok=True)
