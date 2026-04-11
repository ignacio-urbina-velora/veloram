
import sqlite3
import os

db_path = "c:/Users/user/.gemini/antigravity/scratch/ai-video-platform/backend/ai_video_v3.db"

def check_users():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, user_id, name, status, reference_pack_url FROM avatars")
        avatars = cursor.fetchall()
        print("\nAvatars in DB:")
        for avatar in avatars:
            print(f"ID: {avatar[0]}, UserID: {avatar[1]}, Name: {avatar[2]}, Status: {avatar[3]}, Pack: {avatar[4]}")
    except Exception as e:
        print(f"Error checking avatars: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users()
