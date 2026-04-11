import sqlite3

def check_projects():
    conn = sqlite3.connect('ai_video_platform.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, user_id, status, final_video_url FROM projects")
    rows = cursor.fetchall()
    print("--- Projects ---")
    for row in rows:
        print(row)
    conn.close()

if __name__ == "__main__":
    check_projects()
