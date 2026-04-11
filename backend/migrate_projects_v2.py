import sqlite3
import os

db_path = "ai_video_platform.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns
    cursor.execute("PRAGMA table_info(projects)")
    columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns in 'projects': {columns}")
    
    to_add = [
        ("global_prompt", "TEXT"),
        ("negative_prompt_global", "TEXT"),
        ("style_preset", "VARCHAR(100)")
    ]
    
    for col_name, col_type in to_add:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            try:
                cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added {col_name}")
            except Exception as e:
                print(f"❌ Error adding {col_name}: {e}")
        else:
            print(f"Column {col_name} already exists.")
            
    conn.commit()
    conn.close()
    print("Migration finished.")

if __name__ == "__main__":
    migrate()
