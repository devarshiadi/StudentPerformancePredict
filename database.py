import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "users.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# on import, ensure tables exist
with get_conn() as c:
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      email TEXT UNIQUE,
      name TEXT,
      hashed_password TEXT
    )""")
    c.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
      id INTEGER PRIMARY KEY,
      user_id INTEGER,
      predicted REAL,
      accuracy REAL,
      algorithm TEXT,
      input_json TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(user_id) REFERENCES users(id)
    )""")
