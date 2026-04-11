"""Standalone script - resets password using raw bcrypt and sqlite3 (no app imports)."""
import bcrypt
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ai_video_v3.db")
EMAIL = "ignaciourbina.96@gmail.com"
NEW_PASSWORD = "password123"

new_hash = bcrypt.hashpw(NEW_PASSWORD.encode(), bcrypt.gensalt()).decode()

conn = sqlite3.connect(DB_PATH, timeout=5)
c = conn.cursor()

c.execute("SELECT id, email, is_active, is_admin FROM users")
rows = c.fetchall()
print("=== All users ===")
for row in rows:
    print(row)

c.execute(
    "UPDATE users SET hashed_password=?, is_active=1 WHERE email=?",
    (new_hash, EMAIL),
)
conn.commit()
print(f"\n✓ Updated {c.rowcount} row(s). Password set to: {NEW_PASSWORD}")
conn.close()
