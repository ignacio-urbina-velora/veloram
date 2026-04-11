import sqlite3

def check_db():
    conn = sqlite3.connect("ai_video_platform.db")
    cursor = conn.cursor()
    
    print("--- Users ---")
    cursor.execute("SELECT id, email, credits, is_admin FROM users")
    for row in cursor.fetchall():
        print(row)
    
    print("\n--- Avatars ---")
    try:
        cursor.execute("SELECT id, name FROM avatars")
        for row in cursor.fetchall():
            print(row)
    except Exception as e:
        print(f"Avatars table check failed: {e}")
        
    conn.close()

if __name__ == "__main__":
    check_db()
