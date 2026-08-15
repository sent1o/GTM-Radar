import streamlit as st
import sqlite3
import pandas as pd
import asyncio
import os
import urllib.parse
from dotenv import load_dotenv

from scrapers.phscraper import ProductHuntScraper
from scrapers.extract_startup import StartupExtractor
from workers.openai_router import OpenAIRouter
from scrapers.extract_text import TextExtractor
import db

load_dotenv()
DB_NAME = "sites.db"

# --- Функції для UI ---
def get_db_stats():
    conn = sqlite3.connect(DB_NAME)
    stats = pd.read_sql_query("SELECT status, COUNT(*) as count FROM startups GROUP BY status", conn)
    conn.close()
    return stats

def get_recent_startups(limit=200):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"SELECT id, name, website_url, status FROM startups ORDER BY created_at DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_recent_pages(limit=200):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(f"""
        SELECT p.id, s.name, p.page_type, p.url 
        FROM pages p 
        JOIN startups s ON p.startup_id = s.id 
        ORDER BY p.created_at DESC LIMIT {limit}
    """, conn)
    conn.close()
    return df

# --- Логіка Роутера з конкурентністю ---
async def process_single_startup(startup_id, url, extractor, router, sem, log_callback):
    async with sem:
        # Витягуємо чистий домен для логів
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.replace('www.', '') if parsed.netloc else url[:30]

        log_callback(f"[INIT]   {domain} | Старт...")
        try:
            links = await extractor.extract_all_links(url)
            if not links:
                err_msg = "Не знайдено жодного лінка."
                log_callback(f"[ERROR]  {domain} | {err_msg}")
                db.log_failed_startup(startup_id, url, 'playwright_links', err_msg)
                return startup_id, 'failed', None
            
            log_callback(f"[SCRAPE] {domain} | Зібрано {len(links)} лінків. ШІ аналізує...")
            categorized = await asyncio.to_thread(router.categorize_links, base_url=url, links=links)
            
            if not categorized:
                err_msg = "Роутер повернув порожній результат."
                log_callback(f"[ERROR]  {domain} | {err_msg}")
                db.log_failed_startup(startup_id, url, 'openai_router', err_msg)
                return startup_id, 'failed', None

            log_callback(f"[OK]     {domain} | Знайдено {list(categorized.keys())}")
            return startup_id, 'scraped', categorized
            
        except Exception as e:
            err_msg = str(e)[:150] # Обрізаємо кілометрові помилки
            log_callback(f"[ERROR]  {domain} | {err_msg}")
            db.log_failed_startup(startup_id, url, 'exception', err_msg)
            return startup_id, 'failed', None

async def run_playwright_router(startups_limit, log_placeholder):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT id, website_url FROM startups WHERE status = 'unscraped' LIMIT {startups_limit}")
    targets = cursor.fetchall()
    conn.close()
    
    if not targets:
        return "Немає стартапів зі статусом unscraped."
        
    extractor = StartupExtractor()
    router = OpenAIRouter(api_key=os.getenv("OPENAI_KEY"))
    
    logs = []
    def log_cb(msg):
        logs.append(msg)
        # Показуємо останні 12 рядків у консолі
        log_placeholder.code('\n'.join(logs[-12:]), language="bash")
        
    log_cb(f"🚀 Запуск пачки з {len(targets)} стартапів...")
    
    # 3 одночасних браузери, щоб не вбити систему
    sem = asyncio.Semaphore(3)
    tasks = [process_single_startup(sid, url, extractor, router, sem, log_cb) for sid, url in targets]
    
    results = await asyncio.gather(*tasks)
    
    # Записуємо результати в БД (робимо це послідовно, щоб SQLite не видав лок)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    processed = 0
    
    for startup_id, status, categorized in results:
        if status == 'scraped' and categorized:
            for p_type, p_url in categorized.items():
                cursor.execute(
                    "INSERT INTO pages (startup_id, page_type, url) VALUES (?, ?, ?)",
                    (startup_id, p_type, p_url)
                )
        cursor.execute("UPDATE startups SET status = ? WHERE id = ?", (status, startup_id))
        processed += 1
        
    conn.commit()
    conn.close()
    
    log_cb("🎉 Всі процеси завершено.")
    return f"Оброблено {processed} стартапів."

# --- Старі синхронні функції (спрощено) ---
async def run_ph_scraper(pages_limit, log_placeholder):
    scraper = ProductHuntScraper(api_token=os.getenv("PH_TOKEN"))
    cursor_ph = None
    total_added = 0
    
    for page in range(pages_limit):
        log_placeholder.code(f"Тягнемо сторінку {page + 1} з PH...", language="bash")
        raw_data = scraper.fetch_startups(topic="saas", cursor=cursor_ph)
        if not raw_data or "data" not in raw_data: break
            
        startups, page_info = scraper.parse_response(raw_data)
        for s in startups:
            db.insert_startup(s)
            total_added += 1
            
        if not page_info.get('hasNextPage'): break
        cursor_ph = page_info.get('endCursor')
        
    log_placeholder.code(f"Додано {total_added} стартапів.", language="bash")
    return f"Додано/оновлено стартапів: {total_added}"

async def run_text_extractor(startups_limit, log_placeholder):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"SELECT p.id, p.url, p.page_type FROM pages p JOIN startups s ON p.startup_id = s.id WHERE s.status = 'scraped' AND p.page_type = 'pricing' LIMIT {startups_limit}")
    pages = cursor.fetchall()
    
    if not pages:
        conn.close()
        return "Немає підходящих сторінок для екстракції."
        
    extractor = TextExtractor()
    processed = 0
    
    for page_id, url, p_type in pages:
        log_placeholder.code(f"Тягнемо текст: {url}", language="bash")
        text = await extractor.extract_light_mode(url)
        if text:
            cursor.execute("INSERT INTO snapshots (page_id, raw_text) VALUES (?, ?)", (page_id, text))
            processed += 1
            conn.commit()
            
    conn.close()
    log_placeholder.code(f"Готово. Зібрано {processed} текстів.", language="bash")
    return f"Зібрано текст для {processed} сторінок."

# --- UI Дашборду ---
st.set_page_config(page_title="GTM Radar Admin", layout="wide")
st.title("🎯 GTM Radar Dashboard")

st.subheader("Статистика бази")
stats_df = get_db_stats()
if not stats_df.empty:
    cols = st.columns(len(stats_df))
    for i, row in stats_df.iterrows():
        cols[i].metric(label=f"Статус: {row['status']}", value=row['count'])
else:
    st.info("База порожня")

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.header("1. Product Hunt")
    ph_pages = st.number_input("Кількість сторінок PH", min_value=1, max_value=50, value=3)
    if st.button("Запустити PH"):
        log_box1 = st.empty()
        with st.spinner("Тягнемо..."):
            result = asyncio.run(run_ph_scraper(ph_pages, log_box1))
            st.success(result)

with col2:
    st.header("2. Router (Playwright)")
    router_limit = st.number_input("Ліміт для роутера", min_value=1, max_value=100, value=5)
    if st.button("Запустити Роутер"):
        log_box2 = st.empty()
        with st.spinner("Шукаємо..."):
            result = asyncio.run(run_playwright_router(router_limit, log_box2))
            st.success(result)

with col3:
    st.header("3. Text Extractor")
    extractor_limit = st.number_input("Ліміт для екстрактора", min_value=1, max_value=100, value=5)
    if st.button("Запустити Екстрактор"):
        log_box3 = st.empty()
        with st.spinner("Пилососимо..."):
            result = asyncio.run(run_text_extractor(extractor_limit, log_box3))
            st.success(result)

st.divider()

# Секція відображення
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Останні стартапи")
    st.dataframe(get_recent_startups(), height=400)
with col_b:
    st.subheader("Знайдені сторінки (Pages)")
    st.dataframe(get_recent_pages(), height=400)