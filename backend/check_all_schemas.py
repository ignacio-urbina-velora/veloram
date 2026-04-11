import sqlite3
import os

db_path = "ai_video_platform.db"

def check_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ["users", "projects", "shots", "affiliates", "referrals"]
    for table in tables:
        print(f"\nSchema for '{table}':")
        cursor.execute(f"PRAGMA table_info({table})")
        for row in cursor.fetchall():
            print(f"  {row[1]} ({row[2]})")
            
    conn.close()

if __name__ == "__main__":
    check_all()
