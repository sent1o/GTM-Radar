import sqlite3
import json

DB_NAME = "sites.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Таблиця 1: Startups
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS startups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ph_id TEXT UNIQUE,
        name TEXT NOT NULL,
        website_url TEXT NOT NULL,
        tagline TEXT,
        tags TEXT, 
        votes_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'unscraped',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Таблиця 2: Pages
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startup_id INTEGER,
        page_type TEXT NOT NULL,
        url TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
    )
    ''')

    # Таблиця 3: Snapshots
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER,
        image_url TEXT,
        raw_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    ''')

    # Таблиця 4: Insights
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
        startup_id INTEGER,
        ai_summary TEXT,
        old_snapshot_id INTEGER,
        new_snapshot_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (startup_id) REFERENCES startups(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()

def insert_startup(startup):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    tags_json = json.dumps(startup.get("tags", []))
    
    # Використовуємо INSERT OR IGNORE, щоб не дублювати стартапи, якщо проженемо парсер двічі
    cursor.execute('''
    INSERT OR IGNORE INTO startups (ph_id, name, website_url, tagline, tags, votes_count)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        startup.get("ph_id"),
        startup.get("name"),
        startup.get("website_url"),
        startup.get("tagline"),
        tags_json,
        startup.get("votes_count")
    ))
    
    conn.commit()
    conn.close()

# Одразу ініціалізуємо базу при імпорті
init_db()