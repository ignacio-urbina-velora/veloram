import sqlite3
import os

db_path = "backend/ai_video_v3.db"

def migrate():
    # Fix path if running from backend folder
    actual_path = db_path if os.path.exists(db_path) else "ai_video_v3.db"
    if not os.path.exists(actual_path):
        print(f"Database {actual_path} not found.")
        return

    conn = sqlite3.connect(actual_path)
    cursor = conn.cursor()
    
    columns = [
        ("director_bible", "JSON"),
        ("bible_version", "INTEGER DEFAULT 1"),
        ("thread_id", "TEXT")
    ]
    
    for col_name, col_type in columns:
        try:
            print(f"Adding column {col_name} to projects...")
            cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type};")
            print(f"✅ Column {col_name} added.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"⚠️ Column {col_name} already exists.")
            else:
                print(f"❌ Error adding {col_name}: {e}")
                
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate()
