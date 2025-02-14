# database.py
import sqlite3
import json
import os

DB_PATH = os.path.join(os.getcwd(), 'news.db')

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def insert_news_item(news_item):
    conn = get_connection()
    cursor = conn.cursor()

    # Only store up to 35 items
    cursor.execute('SELECT COUNT(*) FROM news')
    count = cursor.fetchone()[0]
    if count >= 35:
        cursor.execute('''
            DELETE FROM news
            WHERE id IN (
                SELECT id FROM news
                ORDER BY created_at ASC
                LIMIT 1
            )
        ''')
        conn.commit()

    # Convert dictionary to JSON before storing
    if not isinstance(news_item, str):
        news_item = json.dumps(news_item)

    cursor.execute('INSERT INTO news (content) VALUES (?)', (news_item,))
    conn.commit()
    conn.close()

def get_all_news():
    """Returns list of news items (latest first). Each item is a Python object (dict) after JSON decode."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT content FROM news ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()

    news_items = []
    for row in rows:
        try:
            news_items.append(json.loads(row[0]))
        except json.JSONDecodeError:
            news_items.append(row[0])  # fallback if it's plain text
    return news_items
