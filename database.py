import sqlite3
import os

DB_NAME = 'bot_database.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kinolar jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        type TEXT NOT NULL,
        file_id TEXT,
        caption TEXT,
        path TEXT,
        url TEXT
    )
    ''')
    
    # Indeks yaratamiz (qidiruv tez bo'lishi uchun)
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movie_code ON movies(code)')
    
    # Foydalanuvchilar jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Sozlamalar (Kanallar) jadvali
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    ''')
    
    conn.commit()
    conn.close()

def set_setting(key, value):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    row = cursor.fetchone()
    conn.close()
    return row['value'] if row else default

def get_channels():
    channels_str = get_setting('required_channels', '')
    urls_str = get_setting('required_urls', '')
    
    channels = [c.strip() for c in channels_str.split(',') if c.strip()]
    urls = [u.strip() for u in urls_str.split(',') if u.strip()]
    return channels, urls

def add_channel(channel_id, url):
    channels, urls = get_channels()
    if channel_id not in channels:
        channels.append(channel_id)
        urls.append(url)
        set_setting('required_channels', ','.join(channels))
        set_setting('required_urls', ','.join(urls))
        return True
    return False

def remove_channel(index):
    channels, urls = get_channels()
    if 0 <= index < len(channels):
        channels.pop(index)
        urls.pop(index)
        set_setting('required_channels', ','.join(channels))
        set_setting('required_urls', ','.join(urls))
        return True
    return False

def add_movie(code, movie_type, file_id=None, caption=None, path=None, url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO movies (code, type, file_id, caption, path, url)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (code, movie_type, file_id, caption, path, url))
    conn.commit()
    conn.close()

def get_movie_by_code(code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movies WHERE code = ?', (code,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_codes():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT code FROM movies')
    rows = cursor.fetchall()
    conn.close()
    return [row['code'] for row in rows]

def add_user(user_id, username=None, full_name=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR IGNORE INTO users (user_id, username, full_name)
    VALUES (?, ?, ?)
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()

def get_stats():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT code) FROM movies')
    movie_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    conn.close()
    return movie_count, user_count

if __name__ == "__main__":
    init_db()
    print("Ma'lumotlar bazasi tayyor!")
