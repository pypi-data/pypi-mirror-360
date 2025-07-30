import sqlite3
from pathlib import Path

db_dir = Path(".databases")
db_dir.mkdir(parents=True, exist_ok=True)

db_path = db_dir / "example.db"

conn = sqlite3.connect(str(db_path))
c = conn.cursor()
c.execute("CREATE TABLE users (id INTEGER, name TEXT, created_at TEXT)")
c.execute("CREATE TABLE orders (order_id INTEGER, user_id INTEGER, amount REAL)")


conn.commit()
conn.close()

print(f"Database created at: {db_path}")
