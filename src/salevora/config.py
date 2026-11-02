"""Project paths and database settings, read from .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"

# .env holds the database password and is never committed (see .env.example).
load_dotenv(ROOT / ".env")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "salevora")
DB_USER = os.getenv("DB_USER", "salevora")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
