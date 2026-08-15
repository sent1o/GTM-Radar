import sqlite3

DB_NAME = "sites.db"

def reset_testing_state():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Скидаємо всі статуси стартапів назад на unscraped
    cursor.execute("UPDATE startups SET status = 'unscraped'")
    
    # Чистимо таблиці зі сторінками і текстами, щоб почати з чистого листа
    cursor.execute("DELETE FROM pages")
    cursor.execute("DELETE FROM snapshots")
    cursor.execute("DELETE FROM insights")
    
    conn.commit()
    conn.close()
    print("Базу обнулено! Статуси скинуті на unscraped, таблиці сторінок очищені.")

if __name__ == "__main__":
    reset_testing_state()