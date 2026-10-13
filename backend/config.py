"""Application configuration, loaded from environment variables / .env."""
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "finance_db")

# DATABASE_URL may be set directly (e.g. for tests); otherwise it is built from DB_* values.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    if DB_PASSWORD or os.getenv("USE_MYSQL"):
        DATABASE_URL = (
            f"mysql+pymysql://{quote_plus(DB_USER)}:{quote_plus(DB_PASSWORD)}"
            f"@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )
    else:
        sqlite_file = BASE_DIR / "database" / "finance_db.sqlite"
        sqlite_file.parent.mkdir(parents=True, exist_ok=True)
        DATABASE_URL = f"sqlite:///{sqlite_file.as_posix()}"

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))

FRONTEND_DIR = BASE_DIR / "frontend"
DEFAULT_USER_ID = 1  # single-user demo; authentication can be added later
