import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "fire_security")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
HASH_SECRET = os.getenv("HASH_SECRET")
LOG_FILE = os.getenv("LOG_FILE", "app.log")

if not HASH_SECRET or HASH_SECRET.lower() in {"change_me", "replace_me"}:
    raise RuntimeError(
        "HASH_SECRET должен быть задан в .env и отличаться от change_me/replace_me"
    )
