import sqlite3
import os

db_path = 'ai_video_platform.db'
print(f"--- Checking: {db_path} ---")
try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cur.fetchall()]
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        count = cur.fetchone()[0]
        print(f"Table {t}: {count} rows")
        if count > 0 and t in ['projects', 'jobs', 'users']:
            cur.execute(f"SELECT * FROM {t} LIMIT 1")
            print(f"  Sample {t}: {cur.fetchone()}")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
