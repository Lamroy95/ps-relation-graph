from pathlib import Path

SQLITE_DB_PATH = Path("karma.db")
HTML_DIR = Path("html")
HTML_DIR.mkdir(parents=True, exist_ok=True)

if not SQLITE_DB_PATH.exists():
    raise FileNotFoundError("Sqlite database file not found")
