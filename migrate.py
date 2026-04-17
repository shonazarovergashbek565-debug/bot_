import json
import os
import sqlite3
from database import init_db, add_movie

MOVIES_FILE = 'movies.json'
DB_NAME = 'bot_database.db'

def migrate_data():
    if not os.path.exists(MOVIES_FILE):
        print(f"Xatolik: {MOVIES_FILE} topilmadi!")
        return

    # DB ni tozalash (agar avval yaratilgan bo'lsa)
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    
    init_db()
    
    with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    count = 0
    for code, items in data.items():
        if isinstance(items, dict):
            items = [items]
        
        for item in items:
            movie_type = item.get('type', 'video')
            file_id = item.get('file_id')
            caption = item.get('caption')
            path = item.get('path')
            
            # Agar URLs ro'yxat bo'lsa, ularni birma-bir qo'shish yoki bitta qilib saqlash
            # Biz bu yerda soddalashtirib birinchi URL ni olamiz
            urls = item.get('urls', [])
            url = urls[0] if urls and isinstance(urls, list) else None
            
            cursor.execute('''
            INSERT INTO movies (code, type, file_id, caption, path, url)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (code, movie_type, file_id, caption, path, url))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Muvaffaqiyatli ko'chirildi: {count} ta kino yozuvi.")

if __name__ == "__main__":
    migrate_data()
